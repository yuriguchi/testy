# TestY TMS - Test Management System
# Copyright (C) 2024 KNS Group LLC (YADRO)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Also add information on how to contact you by electronic and paper mail.
#
# If your software can interact with users remotely through a computer
# network, you should also make sure that it provides a way for users to
# get its source.  For example, if your program is a web application, its
# interface could display a "Source" link that leads users to an archive
# of the code.  There are many ways you could offer source, and different
# solutions will be better for different programs; see section 13 for the
# specific requirements.
#
# You should also get your employer (if you work as a programmer) or school,
# if any, to sign a "copyright disclaimer" for the program, if necessary.
# For more information on this, and how to apply and follow the GNU AGPL, see
# <http://www.gnu.org/licenses/>.
import warnings
from typing import TYPE_CHECKING, Any, Iterable, Mapping, TypeVar

from django.db.models import (
    BooleanField,
    Case,
    Exists,
    F,
    Func,
    Model,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Sum,
    Value,
    When,
)
from django.shortcuts import get_object_or_404
from mptt.querysets import TreeQuerySet

from testy.tests_description.models import TestCase, TestSuite
from testy.tests_description.selectors.cases import TestCaseSelector
from testy.tests_representation.models import Test, TestPlan
from testy.utilities.sql import ConcatSubquery, SubCount, get_max_level
from testy.utilities.tree import build_tree, form_tree_prefetch_lookups, form_tree_prefetch_objects

if TYPE_CHECKING:
    from django.db.models.query import ValuesQuerySet

    from testy.tests_description.api.v2.serializers import TestCaseUnionSerializer, TestSuiteUnionSerializer

_CHILD_TEST_SUITES = 'child_test_suites'
_TEST_CASES = 'test_cases'
_NAME = 'name'
_ID = 'id'
_PARENT = 'parent'
_TREE_ID = 'tree_id'
_PK = 'pk'
_OUTER_REF_PK = OuterRef(_PK)
_OUTER_REF_PATH = OuterRef('path')
_DB_TRUE = Value(True)
_MT = TypeVar('_MT', bound=Model)
_SUITE = 'suite'
_TYPE = 'type'
_IS_LEAF = 'is_leaf'


class TestSuiteSelector:  # noqa: WPS214

    @classmethod
    def suite_list_raw(cls) -> QuerySet[TestSuite]:
        return TestSuite.objects.all().order_by(_NAME)

    @classmethod
    def suite_by_id(cls, suite_id: int) -> TestSuite:
        return get_object_or_404(TestSuite, pk=suite_id)

    @classmethod
    def suite_deleted_list(cls):
        max_level = get_max_level(TestSuite)
        return TestSuite.deleted_objects.all().select_related(_PARENT).prefetch_related(
            *form_tree_prefetch_objects(
                nested_prefetch_field=_CHILD_TEST_SUITES,
                prefetch_field=_CHILD_TEST_SUITES,
                tree_depth=max_level,
                queryset_class=TestSuite,
                manager_name='deleted_objects',
            ),
        )

    @classmethod
    def list_qs(cls, qs: QuerySet[TestSuite], search: str | None = None) -> QuerySet[TestSuite]:
        annotation_methods = [
            cls.annotate_cases_count,
            cls.annotate_descendants_count,
            cls.annotate_estimates,
            cls.annotate_suite_path,
        ]
        if not search:
            annotation_methods.append(cls.annotate_has_children_with_cases)
        for method in annotation_methods:
            qs = method(qs)
        return qs.select_related(_PARENT)

    @classmethod
    def suite_list_union(cls, qs):
        annotation_methods = [
            cls.annotate_cases_count,
            cls.annotate_descendants_count,
            cls.annotate_estimates,
            cls.annotate_suite_path,
            cls.annotate_has_children,
        ]
        for method in annotation_methods:
            qs = method(qs)
        return qs.select_related(_PARENT).order_by(_NAME).annotate(is_leaf=Value(False))

    def suites_by_plans(self, plans: QuerySet[TestPlan]) -> QuerySet[TestSuite]:
        suite_ids = Test.objects.filter(plan__in=plans).values_list('case__suite__id', flat=True)
        max_level = get_max_level(TestSuite)
        qs = TestSuite.objects.filter(id__in=suite_ids).get_ancestors(include_self=True)
        child_subq = Subquery(qs.filter(parent_id=_OUTER_REF_PK))
        qs = self.annotate_has_children_with_cases(qs, child_subq)
        qs = self.annotate_is_used(qs, suite_ids)
        return qs.filter(parent=None).prefetch_related(
            *form_tree_prefetch_objects(
                _CHILD_TEST_SUITES,
                _CHILD_TEST_SUITES,
                tree_depth=max_level,
                queryset=qs,
            ),
        ).order_by(_ID)

    def root_suites_by_plans(
        self,
        plans: QuerySet[TestPlan],
        parent: int | None,
    ) -> list[dict[str, Any]]:
        plan_ids = list(plans.values_list(_ID, flat=True))
        tests = Test.objects.filter(plan__in=plan_ids)
        suite_ids = tests.values_list('case__suite__id', flat=True).distinct()
        if parent is None:
            qs = TestSuite.objects.filter(tree_id__in=tests.values_list('case__suite__tree_id', flat=True).distinct())
        else:
            qs = TestSuite.objects.filter(id__in=suite_ids).get_ancestors(include_self=True)
        child_subq = Subquery(qs.filter(parent_id=_OUTER_REF_PK))

        qs = self.annotate_has_children_with_cases(qs, child_subq)
        qs = self.annotate_is_used(qs, suite_ids)
        return build_tree(qs.values(_ID, _NAME, _PARENT, 'has_children', 'is_used'))

    @classmethod
    def annotate_is_used(cls, qs: QuerySet[TestSuite], used_ids: Iterable[int]) -> QuerySet[TestSuite]:
        is_used_condition = Case(
            When(id__in=used_ids, then=True),
            output_field=BooleanField(),
            default=False,
        )
        return qs.annotate(is_used=is_used_condition)

    @classmethod
    def suite_list_by_tree_ids(cls, tree_ids: Iterable[int]) -> QuerySet[TestSuite]:
        return TestSuite.objects.filter(tree_id__in=tree_ids)

    @classmethod
    def suites_breadcrumbs_by_root(
        cls,
        suites: QuerySet[TestSuite],
        parent_id: int | None,
    ) -> list[dict[str, Any]]:
        if parent_id is None:
            suites = cls.suite_list_by_tree_ids(suites.values_list('tree_id', flat=True))
        else:
            suites = suites.get_descendants(include_self=True)
        qs = cls.annotate_has_children_with_cases(suites, Subquery(suites.filter(parent_id=_OUTER_REF_PK)))
        return build_tree(
            qs.values('id', 'name', 'has_children', 'parent'),
            omitted_ids={parent_id} if parent_id else None,
        )

    @classmethod
    def suites_breadcrumbs(cls, suites: QuerySet[TestSuite]) -> QuerySet[TestSuite]:
        max_level = get_max_level(TestSuite)
        suites = cls.annotate_has_children_with_cases(suites)
        annotated_qs = cls.annotate_has_children_with_cases(cls.suite_list_raw())
        return suites.prefetch_related(
            *form_tree_prefetch_objects(
                'child_test_suites',
                'child_test_suites',
                tree_depth=max_level,
                queryset=annotated_qs,
            ),
        ).order_by(_NAME)

    @classmethod
    def annotate_suite_path(cls, qs: QuerySet[_MT], outer_ref_key: str = 'path') -> QuerySet[_MT]:
        ancestor_paths = TestSuite.objects.filter(
            Q(path__ancestor=OuterRef(outer_ref_key)),
        ).order_by('path').values(_NAME)
        return qs.annotate(suite_path=ConcatSubquery(ancestor_paths, separator='/'))

    @classmethod
    def suite_list_retrieve(cls):
        annotation_methods = [
            cls.annotate_cases_count,
            cls.annotate_descendants_count,
            cls.annotate_estimates,
            cls.annotate_suite_path,
        ]
        qs = cls.suite_list_raw()
        for method in annotation_methods:
            qs = method(qs)
        return qs.order_by(_NAME)

    @classmethod
    def suite_list_ancestors(cls, instance: TestSuite) -> TreeQuerySet[TestSuite]:
        return instance.get_ancestors(include_self=True)

    @classmethod
    def suites_by_ids(cls, ids: Iterable[int], field_name: str = 'pk') -> TreeQuerySet[TestSuite]:
        return TestSuite.objects.filter(**{f'{field_name}__in': ids}).order_by(_ID)

    @classmethod
    def testsuite_project_root_list(cls, project_id: int):
        return TestSuite.objects.filter(project=project_id, parent=None).order_by(_NAME)

    @classmethod
    def annotate_cases_count(cls, qs: QuerySet[TestSuite]) -> QuerySet[TestSuite]:
        cases_count_subq = TestCase.objects.filter(is_archive=False, suite_id=_OUTER_REF_PK)
        total_cases_count_subq = TestCase.objects.filter(
            suite__tree_id=OuterRef(_TREE_ID),
            suite__path__descendant=_OUTER_REF_PATH,
            is_archive=False,
        )
        return qs.annotate(
            cases_count=SubCount(cases_count_subq),
            total_cases_count=SubCount(total_cases_count_subq),
        )

    @classmethod
    def annotate_estimates(cls, qs: QuerySet[TestSuite]) -> QuerySet[TestSuite]:
        return qs.annotate(
            estimates=cls._get_estimate_sum_subquery(),
            total_estimates=cls._get_estimate_sum_subquery(sum_descendants=True),
        )

    @classmethod
    def annotate_descendants_count(cls, qs: QuerySet[TestSuite]) -> QuerySet[TestSuite]:
        descendants_lookup = Q(tree_id=OuterRef(_TREE_ID), path__descendant=_OUTER_REF_PATH)
        descendants_lookup &= ~Q(path=_OUTER_REF_PATH)
        descendants_subquery = TestSuite.objects.filter(descendants_lookup).annotate(
            descendant_count=Func(  # Django автоматом создает GROUP BY если ты используешь Count()
                F(_ID),
                function='Count',
            ),
        ).values('descendant_count')
        return qs.annotate(descendant_count=Subquery(descendants_subquery))

    @classmethod
    def suites_cases_union(
        cls,
        cases: QuerySet[TestCase],
        parent_id: int | None,
        suites: QuerySet[TestSuite],
    ) -> 'ValuesQuerySet[TestSuite, dict[str, Any]]':
        fields = (_ID, 'created_at', _NAME, _IS_LEAF, _TYPE)

        cases_for_display = TestCase.objects.none()
        if parent_id is None:
            return suites.annotate(
                is_leaf=Value(False),
                type=Value(_SUITE),
            ).values(*fields).order_by(_IS_LEAF, _NAME)
        cases_for_display = cases.filter(suite=parent_id, pk__in=cases)

        cases_for_display = cases_for_display.annotate(
            is_leaf=Value(True),
            type=Value('case'),
        ).values(*fields)

        suites_values = suites.annotate(
            is_leaf=Value(False),
            type=Value(_SUITE),
        ).values(*fields)
        suites_values = suites_values.union(cases_for_display).values(*fields).order_by(_IS_LEAF)
        return suites_values.order_by(_IS_LEAF, _NAME)

    def get_union_data(
        self,
        qs: 'ValuesQuerySet[TestSuite, dict[str, Any]]',
        suite_serializer: 'type[TestSuiteUnionSerializer]',
        case_serializer: 'type[TestCaseUnionSerializer]',
    ) -> list[Mapping[str, Any]]:
        suite_ids = []
        case_ids = []

        for elem in qs:
            if elem[_TYPE] == _SUITE:
                suite_ids.append(elem[_ID])
            else:
                case_ids.append(elem[_ID])

        db_cases = TestCaseSelector.cases_for_union_data(case_ids)
        db_cases = TestSuiteSelector.annotate_suite_path(db_cases, 'suite__path').select_related(_SUITE)

        db_suites = self.suites_by_ids(suite_ids, _PK)
        db_suites = self.suite_list_union(db_suites)

        suites = {suite.pk: suite for suite in db_suites}
        cases = {case.pk: case for case in db_cases}

        result_data = []

        for elem in qs:
            serializer = suite_serializer if elem[_TYPE] == _SUITE else case_serializer
            objects_dict = suites if elem[_TYPE] == _SUITE else cases
            if data_dict := objects_dict.get(elem[_ID]):
                result_data.append(serializer(data_dict).data)
        return result_data

    @classmethod
    def annotate_has_children(
        cls,
        qs: QuerySet[TestSuite],
        children_subq: QuerySet[TestSuite] | None = None,
    ) -> QuerySet[TestSuite]:
        if children_subq is None:
            children_subq = TestSuite.objects.filter(parent_id=_OUTER_REF_PK)
        case_subq = TestCase.objects.filter(suite_id=_OUTER_REF_PK)
        return qs.annotate(
            has_children=Case(
                When(Exists(children_subq), then=_DB_TRUE),
                When(Exists(case_subq), then=_DB_TRUE),
                default=Value(False),
            ),
        )

    @classmethod
    def annotate_has_children_with_cases(
        cls,
        qs: QuerySet[TestSuite],
        children_subq: QuerySet[TestSuite] | None = None,
    ):
        if children_subq is None:
            children_subq = TestSuite.objects.all().filter(parent_id=_OUTER_REF_PK)
        return qs.annotate(has_children=Exists(children_subq))

    @classmethod
    def list_ancestors_flat(cls, suite: TestSuite) -> list[int]:
        return list(suite.get_ancestors(include_self=False).values_list(_PK, flat=True))

    @classmethod
    def suites_tree_prefetch_children(cls, max_level: int):
        warnings.warn('Deprecated in 2.0', DeprecationWarning, stacklevel=2)
        qs = cls.suite_list_raw()
        qs = cls.annotate_estimates(qs)
        qs = cls.annotate_descendants_count(qs)
        qs = cls.annotate_suite_path(qs)
        return form_tree_prefetch_objects(
            nested_prefetch_field=_CHILD_TEST_SUITES,
            prefetch_field=_CHILD_TEST_SUITES,
            tree_depth=max_level,
            queryset=cls.annotate_cases_count(qs).order_by(_NAME),
            order_by_fields=[_NAME],
        )

    def suite_list_treeview(self, root_only: bool = True) -> QuerySet[TestSuite]:
        warnings.warn('Deprecated in 2.0', DeprecationWarning, stacklevel=2)
        max_level = get_max_level(TestSuite)
        parent = {_PARENT: None} if root_only else {}
        qs = (
            TestSuite.objects
            .filter(**parent)
            .order_by(_NAME)
            .prefetch_related(
                *self.suites_tree_prefetch_children(max_level),
            )
        )
        qs = self.annotate_estimates(qs)
        qs = self.annotate_cases_count(qs)
        qs = self.annotate_suite_path(qs)
        qs = self.annotate_suite_path(qs)
        return self.annotate_descendants_count(qs)

    def suite_list(self) -> QuerySet[TestSuite]:
        warnings.warn('Deprecated in 2.0', DeprecationWarning, stacklevel=2)
        max_level = get_max_level(TestSuite)
        qs = (
            TestSuite.objects.all()
            .order_by(_NAME)
            .prefetch_related(
                *self.suites_tree_prefetch_cases(max_level),
                *form_tree_prefetch_lookups(
                    _CHILD_TEST_SUITES,
                    'test_cases__attachments',
                    max_level,
                ),
                *form_tree_prefetch_lookups(
                    _CHILD_TEST_SUITES,
                    'test_cases__labeled_items__label',
                    max_level,
                ),
            )
        )
        return self.annotate_suite_path(qs)

    @classmethod
    def suites_tree_prefetch_cases(cls, max_level: int):
        warnings.warn('Function deprecated in 2.0', DeprecationWarning, stacklevel=2)
        return form_tree_prefetch_objects(
            nested_prefetch_field=_CHILD_TEST_SUITES,
            prefetch_field='test_cases',
            tree_depth=max_level,
            queryset=TestCaseSelector().case_list(filter_condition={'is_archive': False}),
        )

    @classmethod
    def suite_list_by_ids(cls, suite_ids: Iterable[int]) -> QuerySet[TestSuite]:
        return TestSuite.objects.filter(id__in=suite_ids)

    @classmethod
    def _get_estimate_sum_subquery(cls, sum_descendants: bool = False):
        if sum_descendants:
            filter_condition = Q(tree_id=OuterRef(_TREE_ID), path__descendant=_OUTER_REF_PATH)
        else:
            filter_condition = Q(pk=_OUTER_REF_PK)
        return Subquery(
            TestSuite.objects.filter(filter_condition)
            .prefetch_related(_TEST_CASES)
            .values(_TREE_ID)
            .annotate(
                total=Sum(
                    'test_cases__estimate',
                    filter=Q(test_cases__is_archive=False, test_cases__is_deleted=False),
                ),
            )
            .values('total'),
        )
