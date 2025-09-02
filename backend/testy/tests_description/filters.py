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
from functools import partial

from django.db.models import OuterRef, Q
from django_filters import CharFilter, NumberFilter
from django_filters import rest_framework as filters
from simple_history.utils import get_history_model_for_model

from testy.core.filters import ParentFilterMixin, SearchFilterMixin
from testy.filters import (
    ArchiveFilterMixin,
    IsFilteredMixin,
    LabelsFilterMetaclass,
    NumberInFilter,
    TreeSearchBaseFilter,
    case_insensitive_filter,
    ordering_filter,
    project_filter,
    union_ordering_filter,
)
from testy.messages.filters import COMMA_SEPARATED_LIST_OR_NULL_MSG, SEARCH_FILTER_MSG, TREE_SEARCH_FILTER_MSG
from testy.tests_description.models import TestCase, TestSuite
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.utilities.request import get_boolean
from testy.utilities.sql import get_max_level
from testy.utilities.string import parse_int


class TestCaseFilter(SearchFilterMixin, ArchiveFilterMixin, metaclass=LabelsFilterMetaclass):
    project = project_filter()
    name = case_insensitive_filter()
    ordering = ordering_filter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('title', 'title'),
            ('created_at', 'created_at'),
        ),
    )
    search = CharFilter(method='filter_by_search', help_text=SEARCH_FILTER_MSG.format('name, id'))
    suite = NumberInFilter(method='filter_by_suite')
    test_case_created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    test_case_created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    search_fields = ['name', 'id']
    labels_outer_ref_prefix = None

    def filter_by_suite(self, queryset, field_name, suite_ids):
        if get_boolean(self.request, 'show_descendants'):
            suites = TestSuiteSelector.suite_list_by_ids(suite_ids).get_descendants(include_self=True)
            suite_ids = suites.values_list('id', flat=True)
        queryset = queryset.filter(suite_id__in=suite_ids)
        if not self.request.query_params.get('ordering'):
            queryset = queryset.order_by('name')
        return queryset

    class Meta:
        model = TestCase
        fields = ('id', 'project', 'suite', 'name', 'search', 'test_case_created_after', 'test_case_created_before')


class SuiteProjectParentFilter(ParentFilterMixin):
    project = project_filter()
    parent = filters.CharFilter(
        'parent',
        method='filter_by_parent',
        help_text=COMMA_SEPARATED_LIST_OR_NULL_MSG,
    )

    class Meta:
        model = TestSuite
        fields = ('project', 'parent')


class TestCaseFilterSearch(SearchFilterMixin, ArchiveFilterMixin, metaclass=LabelsFilterMetaclass):
    project = project_filter()
    name = case_insensitive_filter()
    labels_outer_ref_prefix = None
    search = filters.CharFilter(method='filter_by_search', help_text=SEARCH_FILTER_MSG.format('name, id'))

    search_fields = ['name', 'id']


class TestCaseHistoryFilter(filters.FilterSet):
    ordering = ordering_filter(
        fields=(
            ('history_date', 'history_date'),
            ('history_user', 'history_user'),
            ('history_type', 'history_type'),
        ),
    )

    class Meta:
        model = get_history_model_for_model(TestCase)
        fields = ('id',)


class TestSuiteFilter(SearchFilterMixin):
    project = project_filter()
    parent = filters.CharFilter(
        'parent',
        method='filter_by_parent',
        help_text=COMMA_SEPARATED_LIST_OR_NULL_MSG,
    )
    test_suite_created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    test_suite_created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    treesearch = filters.CharFilter(
        method='filter_by_treesearch',
        help_text=TREE_SEARCH_FILTER_MSG.format('name', 'id'),
    )
    search = filters.CharFilter(method='filter_by_search', help_text=SEARCH_FILTER_MSG.format('name', 'id'))
    ordering = ordering_filter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('descendant_count', 'descendant_count'),
            ('total_cases_count', 'total_cases_count'),
            ('total_estimates', 'total_estimates'),
            ('created_at', 'created_at'),
        ),
    )
    path = filters.CharFilter(field_name='suite_path', lookup_expr='icontains')
    path_exact = filters.CharFilter(field_name='suite_path', lookup_expr='iexact')
    search_fields = ['name', 'id']

    def filter_by_treesearch(self, qs, field_name, value):
        qs = self.filter_by_search(qs, field_name, value)
        ancestors = qs.get_ancestors(include_self=True)
        ancestors = TestSuiteSelector.list_qs(ancestors, self.request.query_params.get('treesearch'))
        return TestSuiteSelector.annotate_has_children_with_cases(
            ancestors,
            ancestors.filter(parent_id=OuterRef('pk')),
        )

    @classmethod
    def filter_by_parent(cls, queryset, field_name, parent):
        lookup = Q()
        if parent == 'null':
            lookup = Q(**{f'{field_name}__isnull': True})
        elif parent_id := parse_int(parent):
            lookup = Q(**{f'{field_name}__id': parent_id})
        return queryset.filter(lookup)

    class Meta:
        model = TestSuite
        fields = (
            'project',
            'treesearch',
            'search',
            'parent',
            'ordering',
            'test_suite_created_after',
            'test_suite_created_before',
        )


class UnionCaseFilter(SearchFilterMixin, ArchiveFilterMixin, IsFilteredMixin, metaclass=LabelsFilterMetaclass):
    project = project_filter()
    search = CharFilter(method='filter_by_search', help_text=SEARCH_FILTER_MSG.format('name, id'))
    test_case_created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    test_case_created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    suite = NumberInFilter('suite', help_text='Comma separated list of test suite ids')

    labels_outer_ref_prefix = None
    search_fields = ['name', 'id']


class SuiteUnionOrderingFilter(filters.FilterSet):
    ordering = union_ordering_filter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('created_at', 'created_at'),
        ),
    )


class CasesBySuiteFilter(TestCaseFilter):
    project = NumberFilter()


class SuiteUnionFilterNoSearch(TestSuiteFilter):
    search = None
    ordering = None

    class Meta(TestSuiteFilter.Meta):
        fields = ('project', 'parent')


class TestSuiteSearchFilter(TreeSearchBaseFilter):
    def __init__(self, *args, **kwargs):
        warnings.warn('Deprecated in 2.0', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)

    children_field_name = 'child_test_suites'
    max_level_method = partial(get_max_level, TestSuite)
    model_class = TestSuite

    def get_ancestors(self, valid_options):
        qs = super().get_ancestors(valid_options)
        qs = TestSuiteSelector.annotate_cases_count(qs)
        qs = TestSuiteSelector.annotate_descendants_count(qs)
        qs = TestSuiteSelector.annotate_suite_path(qs)
        return TestSuiteSelector.annotate_estimates(qs)

    def custom_filter(self, queryset, filter_conditions, request):
        valid_options = self.get_valid_options(filter_conditions, request)
        if get_boolean(request, 'is_flat'):
            return TestSuiteSelector.annotate_suite_path(valid_options)
        max_level = self.max_level_method()
        ancestors = self.get_ancestors(valid_options)
        parent_id = parse_int(request.query_params.get('parent', ''))
        parent_lookup = {'parent_id': parent_id} if parent_id else {'parent_id__isnull': True}
        qs = ancestors.filter(**parent_lookup).prefetch_related(
            *TestSuiteSelector.suites_tree_prefetch_children(max_level),
        )
        qs = TestSuiteSelector.annotate_cases_count(qs)
        qs = TestSuiteSelector.annotate_estimates(qs)
        qs = TestSuiteSelector.annotate_suite_path(qs)
        return TestSuiteSelector.annotate_descendants_count(qs)
