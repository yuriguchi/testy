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

import logging
import warnings
from typing import TYPE_CHECKING, Any, Iterable, Mapping, TypeVar

from django.contrib.postgres.aggregates import ArrayAgg, StringAgg
from django.db.models import (
    Case,
    CharField,
    DateTimeField,
    Exists,
    F,
    Model,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    TextField,
    Value,
    When,
)
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from mptt.querysets import TreeQuerySet

from testy.root.querysets import SoftDeleteTreeQuerySet
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.tests_representation.models import Parameter, Test, TestPlan
from testy.tests_representation.selectors.results import TestResultSelector
from testy.tests_representation.selectors.tests import TestSelector
from testy.tests_representation.services.statistics import HistogramProcessor, LabelProcessor, PieChartProcessor
from testy.utilities.request import PeriodDateTime
from testy.utilities.sql import ConcatSubquery, SubCount, get_max_level
from testy.utilities.string import parse_bool_from_str
from testy.utilities.tree import (
    build_tree,
    form_tree_prefetch_lookups,
    form_tree_prefetch_objects,
    get_breadcrumbs_treeview,
)

if TYPE_CHECKING:
    from django.db.models.query import ValuesQuerySet

    from testy.tests_representation.api.v2.serializers import TestPlanUnionSerializer, TestUnionSerializer

logger = logging.getLogger(__name__)

_CHILD_TEST_PLANS = 'child_test_plans'
_PARAMETERS = 'parameters'
_PK = 'pk'
_NAME = 'name'
_ID = 'id'
_DB_TRUE = Value(True)
_PARENT = 'parent'
_CREATED_AT_DESC = '-created_at'
_TYPE = 'type'
_PLAN = 'plan'
_OUTER_REF_PK = OuterRef('pk')
_MT = TypeVar('_MT', bound=Model)
_IS_LEAF = 'is_leaf'


class TestPlanSelector:  # noqa: WPS214

    @classmethod
    def testplan_list_raw(cls) -> QuerySet[TestPlan]:
        return TestPlan.objects.all()

    @classmethod
    def annotate_title(cls, qs: QuerySet[TestPlan]) -> QuerySet[TestPlan]:
        return qs.annotate(
            parameter_ids=ArrayAgg('parameters__id'),
            parameter_str=StringAgg(
                'parameters__data',
                delimiter=', ',
                output_field=TextField(),
                ordering='parameters__data',
            ),
            title=Case(
                When(
                    parameter_str__isnull=False,
                    then=Concat(
                        F(_NAME),
                        Value(' '),
                        Value('['),
                        F('parameter_str'),
                        Value(']'),
                    ),
                ),
                default=F(_NAME),
                output_field=TextField(),
            ),
        )

    @classmethod
    def plan_list_by_tree_id(cls, tree_ids: Iterable[int]) -> QuerySet[TestPlan]:
        return TestPlan.objects.filter(tree_id__in=tree_ids)

    @classmethod
    def list_qs(cls, qs: QuerySet[TestPlan], search: str | None = None) -> QuerySet[TestPlan]:
        if not search:
            qs = cls.annotate_has_children_with_tests(qs)
        return cls.annotate_title(qs).select_related('parent')

    @classmethod
    def testplan_list_titled(cls) -> QuerySet[TestPlan]:
        return (
            cls
            .annotate_title(cls.testplan_list_raw())
            .prefetch_related(_PARAMETERS, 'attachments')
            .order_by(_NAME)
        )

    @classmethod
    def testplan_list(cls) -> QuerySet[TestPlan]:
        plan_subq = TestPlan.objects.filter(parent=_OUTER_REF_PK)
        qs = TestPlan.objects.all().prefetch_related(_PARAMETERS, 'attachments').select_related(_PARENT)
        return cls.annotate_title(qs).annotate(
            has_children=Exists(plan_subq),
        ).order_by(_NAME)

    @classmethod
    def annotate_has_children(
        cls,
        qs: QuerySet[TestPlan],
        children_subq: QuerySet[TestPlan] | None = None,
    ) -> QuerySet[TestPlan]:
        if children_subq is None:
            children_subq = TestPlan.objects.filter(parent=_OUTER_REF_PK)
        tests_subq = Test.objects.filter(plan=_OUTER_REF_PK)
        return qs.annotate(
            has_children=Case(
                When(Exists(children_subq), then=_DB_TRUE),
                When(Exists(tests_subq), then=_DB_TRUE),
                default=Value(False),
            ),
        )

    @classmethod
    def annotate_has_children_with_tests(
        cls,
        qs: QuerySet[TestPlan],
        children_subq: QuerySet[TestPlan] | None = None,
    ):
        if children_subq is None:
            children_subq = TestPlan.objects.filter(parent_id=_OUTER_REF_PK)
        return qs.annotate(has_children=Exists(children_subq))

    @classmethod
    def testplan_deleted_list(cls):
        max_level = get_max_level(TestPlan)
        return TestPlan.deleted_objects.all().prefetch_related(
            *form_tree_prefetch_objects(
                nested_prefetch_field=_CHILD_TEST_PLANS,
                prefetch_field=_CHILD_TEST_PLANS,
                tree_depth=max_level,
                queryset_class=TestPlan,
                manager_name='deleted_objects',
            ),
            *form_tree_prefetch_lookups(_CHILD_TEST_PLANS, _PARAMETERS, max_level),
        )

    @classmethod
    def testplan_project_root_list(cls, project_id: int) -> SoftDeleteTreeQuerySet[TestPlan]:
        return TestPlan.objects.filter(project=project_id, parent__isnull=True).order_by(_NAME)

    @classmethod
    def testplan_get_by_pk(cls, pk) -> TestPlan | None:
        return get_object_or_404(TestPlan, pk=pk)

    @classmethod
    def testplan_breadcrumbs_by_ids(cls, ids: list[int]) -> dict[str, dict[str, Any]]:
        plans = TestPlan.objects.filter(pk__in=ids).prefetch_related(_PARAMETERS)
        ancestors = plans.get_ancestors(include_self=False).prefetch_related(_PARAMETERS)
        ids_to_breadcrumbs = {}
        for plan in plans:
            tree = [ancestor for ancestor in ancestors if ancestor.is_ancestor_of(plan)]
            tree.append(plan)
            ids_to_breadcrumbs[plan.id] = get_breadcrumbs_treeview(
                instances=tree,
                depth=len(tree) - 1,
                title_method=cls._get_testplan_title,
            )
        return ids_to_breadcrumbs

    @classmethod
    def testplan_list_ancestors(cls, instance: TestPlan) -> TreeQuerySet[TestPlan]:
        return instance.get_ancestors(include_self=True).prefetch_related(_PARAMETERS)

    @classmethod
    def get_testplan_descendants_ids_by_testplan(cls, test_plan: TestPlan, include_self: bool = True):
        return test_plan.get_descendants(include_self=include_self).values_list(_PK, flat=True)

    def testplan_statistics(
        self,
        test_plans: SoftDeleteTreeQuerySet[TestPlan],
        parameters: dict[str, Any],
        is_whole_project: bool,
        is_archive: bool = False,
        project_id: int | None = None,
    ):
        label_processor = LabelProcessor(parameters)
        pie_chart_processor = PieChartProcessor(parameters)
        if not test_plans.exists():
            return []
        root_only = parse_bool_from_str(parameters.get('root_only', None))

        is_archive_condition = Q() if is_archive else Q(is_archive=False)
        return pie_chart_processor.process_statistic(
            test_plans,
            label_processor,
            is_archive_condition,
            project_id,
            is_whole_project,
            root_only,
        )

    def get_plan_progress(self, plan_id: int, period: PeriodDateTime):
        last_status_period = TestResultSelector.get_last_status_subquery(
            filters=[Q(created_at__gte=period.start) & Q(created_at__lte=period.end)],
        )
        last_status_total = TestResultSelector.get_last_status_subquery()
        descendants_include_self_lookup = Q(
            plan__path__descendant=OuterRef('path'),
            plan__is_archive=False,
        )
        tests_total_query = Test.objects.filter(descendants_include_self_lookup).values(_PK)
        tests_progress_period = self._get_tests_subquery(last_status_period, descendants_include_self_lookup)
        tests_progress_total = self._get_tests_subquery(last_status_total, descendants_include_self_lookup)
        return (
            TestPlan.objects
            .filter(parent=plan_id, is_archive=False)
            .prefetch_related(_PARAMETERS)
            .annotate(
                tests_total=SubCount(tests_total_query),
                tests_progress_period=SubCount(tests_progress_period),
                tests_progress_total=SubCount(tests_progress_total),
            )
        )

    def testplan_histogram(
        self,
        test_plans: SoftDeleteTreeQuerySet[TestPlan],
        parameters: dict[str, Any],
        is_whole_project: bool,
        is_archive: bool = False,
        project_id: int | None = None,
    ):
        histogram_processor = HistogramProcessor(parameters)
        label_processor = LabelProcessor(parameters, 'test__case')
        if not test_plans.exists():
            return []
        root_only = parse_bool_from_str(parameters.get('root_only', None))
        is_archive_condition = Q() if is_archive else Q(is_archive=False)
        return histogram_processor.process_statistic(
            test_plans,
            label_processor,
            is_archive_condition,
            project_id,
            is_whole_project,
            root_only,
        )

    @classmethod
    def plans_tests_union(
        cls,
        tests: QuerySet[Test],
        parent_id: int | None,
        plans: QuerySet[TestPlan],
    ) -> 'ValuesQuerySet[TestPlan, dict[str, Any]]':
        fields = (
            _ID,
            'created_at',
            _NAME,
            'started_at',
            _IS_LEAF,
            _TYPE,
            'union_assignee_username',
            'union_suite_path',
        )
        if parent_id is None:
            plans_values = plans.annotate(
                is_leaf=Value(False),
                type=Value(_PLAN),
                union_suite_path=Value(None, output_field=CharField()),
                union_assignee_username=Value(None, output_field=CharField()),
            ).values(*fields)
            return plans_values.order_by(_IS_LEAF, _NAME)

        tests = tests.filter(plan=parent_id)

        tests_for_display = tests.annotate(
            name=F('case__name'),
            started_at=Value(None, output_field=DateTimeField()),
            is_leaf=Value(True),
            type=Value('test'),
            union_suite_path=F('suite_path'),
            union_assignee_username=F('assignee__username'),
        ).values(*fields)

        plans_values = plans.annotate(
            is_leaf=Value(False),
            type=Value(_PLAN),
            union_suite_path=Value(None, output_field=CharField()),
            union_assignee_username=Value(None, output_field=CharField()),
        ).values(*fields)
        plans_values = plans_values.union(tests_for_display)
        return plans_values.order_by(_IS_LEAF, _NAME)

    def plan_annotated_by_ids(self, ids: Iterable[int]) -> QuerySet[TestPlan]:
        child_subq = Subquery(TestPlan.objects.filter(parent_id=_OUTER_REF_PK))
        tests_subq = Subquery(Test.objects.filter(plan_id=_OUTER_REF_PK))
        qs = TestPlan.objects.filter(pk__in=ids).prefetch_related(_PARAMETERS).select_related(_PARENT)
        return self.annotate_title(qs).annotate(
            has_children=Case(
                When(Exists(child_subq), then=_DB_TRUE),
                When(Exists(tests_subq), then=_DB_TRUE),
                default=Value(False),
            ),
            is_leaf=Value(False),
        ).order_by(_CREATED_AT_DESC)

    @classmethod
    def list_ancestors_flat(cls, plan: TestPlan) -> list[int]:
        return list(plan.get_ancestors(include_self=False).values_list(_PK, flat=True))

    def get_union_data(
        self,
        qs: QuerySet,
        test_serializer: 'type[TestUnionSerializer]',
        plan_serializer: 'type[TestPlanUnionSerializer]',
    ) -> list[Mapping[str, Any]]:
        plan_ids = []
        test_ids = []

        for elem in qs:
            if elem[_TYPE] == _PLAN:
                plan_ids.append(elem[_ID])
            else:
                test_ids.append(elem[_ID])

        plans = {plan.pk: plan for plan in self.plan_annotated_by_ids(plan_ids)}
        tests = TestSelector().test_list_with_last_status(
            filter_condition={'pk__in': test_ids},
        ).annotate(is_leaf=Value(True))
        tests = TestSuiteSelector.annotate_suite_path(tests, 'case__suite__path')
        tests = {test.pk: test for test in tests}

        result_data = []

        for elem in qs:
            serializer = plan_serializer if elem[_TYPE] == _PLAN else test_serializer
            objects_dict = plans if elem[_TYPE] == _PLAN else tests
            if data_dict := objects_dict.get(elem[_ID]):
                result_data.append(serializer(data_dict).data)
        return result_data

    @classmethod
    def plans_by_ids(cls, ids: Iterable[int], field_name: str = 'id') -> SoftDeleteTreeQuerySet[TestPlan]:
        return TestPlan.objects.filter(**{f'{field_name}__in': ids})

    @classmethod
    def annotate_plan_path(cls, qs: QuerySet[_MT], outer_ref_key: str = 'path') -> QuerySet[_MT]:
        ancestor_paths = TestPlan.objects.filter(
            Q(path__ancestor=OuterRef(outer_ref_key)),
        ).order_by('path')
        ancestor_paths = cls.annotate_title(ancestor_paths).values('title')
        return qs.annotate(plan_path=ConcatSubquery(ancestor_paths, separator='/')).order_by('case__name')

    @classmethod
    def plans_breadcrumbs_by_root(
        cls,
        plans: QuerySet[TestPlan],
        parent_id: int | None = None,
    ) -> list[dict[str, Any]]:
        if parent_id is None:
            plans = cls.plan_list_by_tree_id(plans.values_list('tree_id', flat=True))
        else:
            plans = plans.get_descendants(include_self=True)
        qs = cls.annotate_title(plans)
        qs = cls.annotate_has_children_with_tests(qs, Subquery(qs.filter(parent_id=_OUTER_REF_PK)))
        return build_tree(
            qs.values('id', 'title', 'has_children', 'parent'),
            title_key='title',
            omitted_ids={parent_id} if parent_id else None,
        )

    def plans_breadcrumbs(self, plans: QuerySet[TestPlan]) -> QuerySet[TestPlan]:
        max_level = get_max_level(TestPlan)
        annotate_qs = self.annotate_has_children(self.annotate_title(self.testplan_list_raw()))
        qs = self.annotate_title(plans)
        qs = self.annotate_has_children_with_tests(qs)
        return qs.prefetch_related(
            *form_tree_prefetch_objects(
                'child_test_plans',
                'child_test_plans',
                tree_depth=max_level,
                queryset=annotate_qs,
            ),
        ).order_by('name')

    def testplan_list_v1(self, is_archive: bool = False) -> QuerySet[TestPlan]:
        warnings.warn('Function is deprecated', DeprecationWarning, stacklevel=2)
        max_level = get_max_level(TestPlan)
        testplan_prefetch_objects = form_tree_prefetch_objects(
            nested_prefetch_field=_CHILD_TEST_PLANS,
            prefetch_field=_CHILD_TEST_PLANS,
            tree_depth=max_level,
            queryset_class=TestPlan,
            queryset_filter=None if is_archive else {'is_archive': False},
        )
        testplan_prefetch_objects.extend(
            form_tree_prefetch_objects(
                nested_prefetch_field=_CHILD_TEST_PLANS,
                prefetch_field=_PARAMETERS,
                tree_depth=max_level,
                queryset_class=Parameter,
            ),
        )
        return TestPlan.objects.all().prefetch_related(
            *testplan_prefetch_objects,
        )

    def testplan_treeview_list(self, qs: QuerySet[TestPlan], parent_id: int | None = None) -> QuerySet[TestPlan]:
        warnings.warn('Treeviews are deprecated', DeprecationWarning, stacklevel=2)
        qs = self.annotate_title(qs)
        max_level = get_max_level(TestPlan)
        testplan_prefetch_objects = form_tree_prefetch_objects(
            nested_prefetch_field=_CHILD_TEST_PLANS,
            prefetch_field=_CHILD_TEST_PLANS,
            tree_depth=max_level,
            queryset=qs,
        )
        testplan_prefetch_objects.extend(
            form_tree_prefetch_objects(
                nested_prefetch_field=_CHILD_TEST_PLANS,
                prefetch_field=_PARAMETERS,
                tree_depth=max_level,
                queryset_class=Parameter,
            ),
        )
        qs = TestPlan.objects.filter(parent=parent_id).order_by('-created_at').prefetch_related(
            *testplan_prefetch_objects,
        )
        return self.annotate_title(qs)

    @classmethod
    def _get_tests_subquery(cls, last_status_subquery, descendants_lookup):
        return Test.objects.filter(
            descendants_lookup,
            last_status__isnull=False,
        ).values(_PK)

    @classmethod
    def _get_testplan_title(cls, instance: TestPlan):
        if parameters := instance.parameters.all():
            return '{0} [{1}]'.format(instance.name, ', '.join([parameter.data for parameter in parameters]))
        return instance.name
