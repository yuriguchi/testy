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
from copy import deepcopy
from functools import partial

from django.db.models import OuterRef, Q
from django_filters import BaseCSVFilter, NumberFilter
from django_filters import rest_framework as filters
from simple_history.utils import get_history_model_for_model

from testy.core.filters import ParentFilterMixin, SearchFilterMixin
from testy.filters import (
    ArchiveFilterMixin,
    FilterListMixin,
    IsFilteredMixin,
    LabelsFilterMetaclass,
    NumberInFilter,
    StringInFilter,
    TreeSearchBaseFilter,
    ordering_filter,
    project_filter,
    union_ordering_filter,
)
from testy.messages.filters import (
    CASE_INSENSITIVE_TEXT_MSG,
    COMMA_SEPARATED_LIST_IDS_MSG,
    COMMA_SEPARATED_LIST_OR_NULL_MSG,
    ID_FILTER_MSG,
    SEARCH_FILTER_MSG,
    TREE_SEARCH_FILTER_MSG,
)
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.tests_representation.models import Parameter, ResultStatus, Test, TestPlan, TestResult
from testy.tests_representation.selectors.testplan import TestPlanSelector
from testy.utilities.request import get_boolean
from testy.utilities.sql import get_max_level
from testy.utilities.string import parse_bool_from_str, parse_int


class PlanFilter(SearchFilterMixin):
    project = project_filter()
    parameters = NumberInFilter(
        'parameter_ids',
        method='filter_by_parameters',
        help_text=COMMA_SEPARATED_LIST_IDS_MSG,
    )
    parent = filters.CharFilter(
        'parent',
        method='filter_by_parent',
        help_text=COMMA_SEPARATED_LIST_OR_NULL_MSG,
    )
    attributes = filters.BaseCSVFilter(
        'attributes',
        lookup_expr='has_keys',
        help_text='Filter by attributes having exact provided keys, as comma separated list',
    )
    any_attributes = filters.BaseCSVFilter(
        'attributes',
        lookup_expr='has_any_keys',
        help_text='Filter by attributes having any of provided keys, as comma separated list',
    )
    treesearch = filters.CharFilter(
        method='filter_by_treesearch',
        help_text=TREE_SEARCH_FILTER_MSG.format('title', 'id'),
    )
    search = filters.CharFilter(
        method='filter_by_search',
        help_text=SEARCH_FILTER_MSG.format('title', 'id'),
    )
    test_plan_started_after = filters.DateTimeFilter(field_name='started_at', lookup_expr='gte')
    test_plan_started_before = filters.DateTimeFilter(field_name='started_at', lookup_expr='lte')
    test_plan_created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    test_plan_created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    ordering = ordering_filter(
        fields=(
            ('started_at', 'started_at'),
            ('created_at', 'created_at'),
            ('name', 'name'),
            ('id', 'id'),
        ),
    )
    search_fields = ['title', 'id']

    def filter_by_treesearch(self, qs, field_name, value):
        if not parse_bool_from_str(self.data.get('is_archive')):
            qs = qs.filter(is_archive=False)
        qs = self.filter_by_search(qs, field_name, value)
        ancestors = qs.get_ancestors(include_self=True)
        ancestors = TestPlanSelector.annotate_title(ancestors)
        return TestPlanSelector.annotate_has_children_with_tests(
            ancestors,
            ancestors.filter(parent_id=OuterRef('pk')),
        )

    @classmethod
    def filter_by_parameters(cls, queryset, field_name, parameter_ids):
        for parameter_id in parameter_ids:
            queryset = queryset.filter(parameters__id=parameter_id)
        return queryset

    @classmethod
    def filter_by_parent(cls, queryset, field_name, parent):
        lookup = Q()
        if parent == 'null':
            lookup = Q(**{f'{field_name}__isnull': True})
        elif parent_id := parse_int(parent):
            lookup = Q(**{f'{field_name}__id': parent_id})
        return queryset.filter(lookup)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if not parse_bool_from_str(self.data.get('is_archive')):
            queryset = queryset.filter(is_archive=False)
        return queryset

    class Meta:
        model = TestPlan
        fields = (
            'project',
            'treesearch',
            'search',
            'parameters',
            'parent',
            'attributes',
            'any_attributes',
            'ordering',
            'test_plan_started_after',
            'test_plan_started_before',
            'test_plan_created_after',
            'test_plan_created_before',
        )


class PlanProjectParentFilter(ParentFilterMixin):
    project = project_filter()
    parent = filters.CharFilter(
        'parent',
        method='filter_by_parent',
        help_text=COMMA_SEPARATED_LIST_OR_NULL_MSG,
    )

    class Meta:
        model = TestPlan
        fields = ('project', 'parent')


class PlanUnionFilter(PlanFilter):
    ordering = None
    parent = filters.CharFilter(
        'parent',
        method='filter_by_parent',
        required=True,
        help_text=COMMA_SEPARATED_LIST_OR_NULL_MSG,
    )

    @classmethod
    def filter_by_parent(cls, queryset, field_name, parent):
        lookup = Q()
        if parent == 'null':
            lookup = Q(**{f'{field_name}__isnull': True})
        elif parent_id := parse_int(parent):
            lookup = Q(**{f'{field_name}__id': parent_id})
        return queryset.filter(lookup)

    class Meta(PlanFilter.Meta):
        fields = (
            'project',
            'treesearch',
            'search',
            'parameters',
            'parent',
            'attributes',
            'any_attributes',
            'test_plan_started_after',
            'test_plan_started_before',
            'test_plan_created_after',
            'test_plan_created_before',
        )


class PlanUnionOrderingFilter(filters.FilterSet):
    ordering = union_ordering_filter(
        fields=(
            ('id', 'id'),
            ('is_leaf', 'is_leaf'),
            ('started_at', 'started_at'),
            ('created_at', 'created_at'),
            ('name', 'name'),
            ('union_assignee_username', 'assignee_username'),
            ('union_suite_path', 'suite_path'),
        ),
    )


class PlanUnionFilterNoSearch(PlanFilter):
    ordering = None
    search = None
    treesearch = None

    class Meta(PlanFilter.Meta):
        fields = (
            'project',
            'parameters',
            'parent',
            'attributes',
            'any_attributes',
            'test_plan_started_after',
            'test_plan_started_before',
            'test_plan_created_after',
            'test_plan_created_before',
        )


class UnionTestFilter(ArchiveFilterMixin, IsFilteredMixin, SearchFilterMixin, metaclass=LabelsFilterMetaclass):
    last_status = filters.BaseCSVFilter(
        field_name='last_status',
        method='filter_by_last_status',
        help_text=COMMA_SEPARATED_LIST_OR_NULL_MSG,
    )
    assignee = NumberInFilter(help_text=ID_FILTER_MSG)
    assignee_username = filters.CharFilter(
        'assignee__username',
        lookup_expr='icontains',
        help_text=CASE_INSENSITIVE_TEXT_MSG,
    )
    suite_path = filters.CharFilter(
        'suite_path',
        lookup_expr='icontains',
        help_text=CASE_INSENSITIVE_TEXT_MSG,
    )
    search = filters.CharFilter(
        method='filter_by_search',
        help_text=SEARCH_FILTER_MSG.format('name, id'),
    )
    test_created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    test_created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    plan = NumberInFilter(field_name='plan', help_text='Filter by comma separated list of plan ids')
    suite = NumberInFilter(field_name='case__suite', help_text='Filter by comma separated list of suite ids')
    treesearch = filters.CharFilter(
        method='filter_by_search',
        help_text=SEARCH_FILTER_MSG.format('name'),
    )

    labels_outer_ref_prefix = 'case'
    search_fields = ['case__name', 'id']

    @classmethod
    def filter_by_last_status(cls, queryset, field_name: str, statuses):
        local_statuses = deepcopy(statuses)
        filter_conditions = Q(**{f'{field_name}__in': local_statuses})
        if 'null' in local_statuses:
            local_statuses.remove('null')
            filter_conditions |= Q(**{f'{field_name}__isnull': True})
        return queryset.filter(filter_conditions)

    class Meta:
        model = Test
        fields = ('project', 'plan', 'assignee')


class TestFilter(ArchiveFilterMixin, SearchFilterMixin, metaclass=LabelsFilterMetaclass):
    project = project_filter()
    assignee = NumberInFilter(help_text=ID_FILTER_MSG)
    unassigned = filters.BooleanFilter(field_name='assignee', lookup_expr='isnull')
    suite = NumberInFilter('case__suite_id', method='filter_by_suite', help_text=COMMA_SEPARATED_LIST_OR_NULL_MSG)
    plan = NumberInFilter(field_name='plan', help_text='Filter by comma separated list of plan ids')
    last_status = filters.BaseCSVFilter(
        field_name='last_status',
        method='filter_by_last_status',
        help_text=COMMA_SEPARATED_LIST_OR_NULL_MSG,
    )
    search = filters.CharFilter(
        method='filter_by_search',
        help_text=SEARCH_FILTER_MSG.format('title, id'),
    )
    case = NumberInFilter(field_name='case', help_text='Filter by comma separated list of case ids')
    ordering = ordering_filter(
        fields=(
            ('id', 'id'),
            ('last_status', 'last_status'),
            ('created_at', 'created_at'),
            ('case__name', 'name'),
            ('is_archive', 'is_archive'),
            ('assignee', 'assignee'),
            ('assignee__username', 'assignee_username'),
            ('suite_path', 'suite_path'),
        ),
    )

    labels_outer_ref_prefix = 'case'
    search_fields = ['case__name', 'id']

    def filter_by_suite(self, queryset, field_name, suite_ids):
        filter_conditons = {f'{field_name}__in': suite_ids}
        if get_boolean(self.request, 'nested_search'):
            suites = TestSuiteSelector.suites_by_ids(suite_ids, 'pk')
            suite_ids = suites.get_descendants(include_self=True).values_list('id', flat=True)
            filter_conditons = {f'{field_name}__in': suite_ids}
        return queryset.filter(**filter_conditons)

    @classmethod
    def filter_by_last_status(cls, queryset, field_name: str, statuses):
        local_statuses = deepcopy(statuses)
        filter_conditions = Q(**{f'{field_name}__in': local_statuses})
        if 'null' in local_statuses:
            local_statuses.remove('null')
            filter_conditions |= Q(**{f'{field_name}__isnull': True})
        return queryset.filter(filter_conditions)

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        if not self.request.query_params.get('ordering'):
            qs = qs.order_by('case__name')
        return qs

    class Meta:
        model = Test
        fields = (
            'project',
            'plan',
            'case',
            'suite',
            'assignee',
            'unassigned',
            'last_status',
            'labels',
            'not_labels',
            'ordering',
            'search',
        )


class TestsByPlanFilter(TestFilter):
    project = NumberFilter()
    created_at_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    @classmethod
    def filter_by_last_status(cls, queryset, field_name: str, statuses):
        local_statuses = deepcopy(statuses)
        filter_conditions = Q(**{f'{field_name}__in': local_statuses})
        if 'null' in local_statuses:
            local_statuses.remove('null')
            filter_conditions |= Q(**{f'{field_name}__isnull': True})
        return queryset.filter(filter_conditions)

    class Meta:
        model = Test
        fields = (
            'project',
            'plan',
            'suite',
            'case',
            'assignee',
            'unassigned',
            'last_status',
            'labels',
            'not_labels',
            'ordering',
        )


class TestFilterNested(TestFilter):
    project = filters.NumberFilter('project')


class TestResultFilter(ArchiveFilterMixin):
    project = project_filter()

    class Meta:
        model = TestResult
        fields = ('test',)


class ParameterFilter(filters.FilterSet):
    project = project_filter()

    class Meta:
        model = Parameter
        fields = ('project',)


class ActivityFilter(SearchFilterMixin, FilterListMixin):
    history_user = NumberInFilter(field_name='history_user', help_text='Filter by comma separated list of user ids')
    status = BaseCSVFilter(field_name='status', method='filter_by_list', help_text=COMMA_SEPARATED_LIST_OR_NULL_MSG)
    history_type = StringInFilter(
        field_name='history_type',
        help_text='Filter by comma separated list that can contain +,~,- matches added, modified, deleted',
    )
    test = NumberInFilter(field_name='test', help_text=COMMA_SEPARATED_LIST_IDS_MSG)
    ordering = ordering_filter(
        fields=(
            ('history_user', 'history_user'),
            ('history_date', 'history_date'),
            ('history_type', 'history_type'),
            ('test__case__name', 'test__case__name'),
        ),
    )
    search = filters.CharFilter(
        method='filter_by_search',
        help_text=SEARCH_FILTER_MSG.format('username, case name, histoical record date'),
    )

    search_fields = ['history_user__username', 'test__case__name', 'history_date']

    class Meta:
        model = get_history_model_for_model(TestResult)
        fields = ('id',)


class ResultStatusFilter(filters.FilterSet):
    class Meta:
        model = ResultStatus
        fields = ('type',)


class TestPlanSearchFilter(TreeSearchBaseFilter):
    def __init__(self, *args, **kwargs):
        warnings.warn('Deprecated in 2.0', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)

    children_field_name = 'child_test_plans'
    max_level_method = partial(get_max_level, TestPlan)
    model_class = TestPlan

    def get_ancestors(self, valid_options):
        return super().get_ancestors(valid_options).prefetch_related('parameters')

    def get_valid_options(self, filter_conditions, request):
        additional_filters = {
            'project_id': request.query_params.get('project'),
        }
        if not get_boolean(request, 'is_archive'):
            additional_filters['is_archive'] = False
        qs = TestPlanSelector.annotate_title(TestPlanSelector.testplan_list_raw())
        return qs.filter(filter_conditions, **additional_filters)


class PlanFilterV1(filters.FilterSet):
    def __init__(self, *args, **kwargs):
        warnings.warn('Dont use in new code, only for backward compatibility', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)

    project = project_filter()
    parameters = filters.BaseCSVFilter('parameter_ids', method='filter_by_parameters')
    parent = filters.CharFilter('parent', method='filter_by_parent')
    attributes = filters.BaseCSVFilter('attributes', lookup_expr='has_keys')
    any_attributes = filters.BaseCSVFilter('attributes', lookup_expr='has_any_keys')
    ordering = ordering_filter(
        fields=(
            ('started_at', 'started_at'),
            ('created_at', 'created_at'),
            ('name', 'name'),
            ('id', 'id'),
        ),
    )

    @classmethod
    def filter_by_parameters(cls, queryset, field_name, parameter_ids):
        for parameter_id in parameter_ids:
            queryset = queryset.filter(parameters__id=parameter_id)
        return queryset

    @classmethod
    def filter_by_parent(cls, queryset, field_name, parent):
        lookup = Q()
        if parent == 'null':
            lookup = Q(**{f'{field_name}__isnull': True})
        elif parent_id := parse_int(parent):
            lookup = Q(**{f'{field_name}__id': parent_id})
        return queryset.filter(lookup)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if not parse_bool_from_str(self.data.get('is_archive')):
            queryset = queryset.filter(is_archive=False)
        return queryset

    class Meta:
        model = TestPlan
        fields = ('project', 'parameters', 'parent', 'attributes', 'any_attributes', 'ordering')
