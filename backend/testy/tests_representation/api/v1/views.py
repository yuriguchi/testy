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
from typing import Any

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from mptt.exceptions import InvalidMove
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from testy.core.api.v1.serializers import LabelSerializer
from testy.core.selectors.labels import LabelSelector
from testy.core.selectors.projects import ProjectSelector
from testy.core.services.copy import CopyService
from testy.filters import NumberInFilter, TestyBaseSearchFilter
from testy.paginations import StandardSetPagination
from testy.permissions import ForbidChangesOnArchivedProject, IsAdminOrForbidArchiveUpdate
from testy.root.mixins import TestyArchiveMixin, TestyModelViewSet
from testy.root.querysets import SoftDeleteTreeQuerySet
from testy.swagger.v1.results import result_list_schema
from testy.swagger.v1.testplans import (
    get_plan_histogram_schema,
    get_plan_statistic_schema,
    plan_activity_schema,
    plan_case_ids_schema,
    plan_copy_schema,
    plan_create_schema,
    plan_labels_schema,
    plan_list_schema,
    plan_progress_schema,
    plan_suites_ids_schema,
    plan_update_schema,
)
from testy.swagger.v1.tests import test_bulk_update_schema, test_list_schema
from testy.tests_description.api.v1.serializers import TestSuiteTreeBreadcrumbsSerializer
from testy.tests_description.selectors.cases import TestCaseSelector
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.tests_representation.api.v1.serializers import (
    BulkUpdateTestsSerializer,
    ParameterSerializer,
    ResultStatusSerializer,
    TestPlanCopySerializer,
    TestPlanInputSerializer,
    TestPlanMinSerializer,
    TestPlanOutputSerializer,
    TestPlanProgressSerializer,
    TestPlanRetrieveSerializer,
    TestPlanTreeSerializer,
    TestPlanUpdateSerializer,
    TestResultActivitySerializer,
    TestResultInputSerializer,
    TestResultSerializer,
    TestSerializer,
)
from testy.tests_representation.filters import (
    ActivityFilter,
    ParameterFilter,
    PlanFilterV1,
    ResultStatusFilter,
    TestFilter,
    TestPlanSearchFilter,
    TestResultFilter,
)
from testy.tests_representation.models import Test, TestPlan, TestResult
from testy.tests_representation.permissions import ResultStatusPermission, TestPlanPermission, TestResultPermission
from testy.tests_representation.selectors.parameters import ParameterSelector
from testy.tests_representation.selectors.results import TestResultSelector
from testy.tests_representation.selectors.status import ResultStatusSelector
from testy.tests_representation.selectors.testplan import TestPlanSelector
from testy.tests_representation.selectors.tests import TestSelector
from testy.tests_representation.services.parameters import ParameterService
from testy.tests_representation.services.results import TestResultService
from testy.tests_representation.services.status import ResultStatusService
from testy.tests_representation.services.testplans import TestPlanService
from testy.tests_representation.services.tests import TestService
from testy.utilities.request import (
    PeriodDateTime,
    get_boolean,
    get_integer,
    mock_request_with_query_params,
    validate_query_params_data,
)

_LABELS = 'labels'
_GET = 'get'
_REQUEST = 'request'
_LABELS_CONDITION = 'labels_condition'
_IS_ARCHIVE = 'is_archive'
_LIST = 'list'
_ACTIVITY = 'activity'
_RESULT_STATUS = 'status'


class ParameterViewSet(TestyModelViewSet):
    queryset = ParameterSelector().parameter_list()
    serializer_class = ParameterSerializer
    filter_backends = [DjangoFilterBackend]
    schema_tags = ['Parameters']

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return ParameterFilter

    def perform_create(self, serializer: ParameterSerializer):
        serializer.instance = ParameterService().parameter_create(serializer.validated_data)

    def perform_update(self, serializer: ParameterSerializer):
        serializer.instance = ParameterService().parameter_update(serializer.instance, serializer.validated_data)


class TestPLanStatisticsView(ViewSet):
    lookup_value_regex = r'\d+'
    schema_tags = ['Test plans']

    def get_view_name(self):
        return 'Test Plan Statistics'

    def get_statistic_objects(self, pk: int) -> SoftDeleteTreeQuerySet[TestPlan]:
        return TestPlanSelector.plans_by_ids(ids=[pk])

    @get_plan_statistic_schema
    def get(self, request, pk):
        test_plans = self.get_statistic_objects(pk)
        is_whole_project = False
        project_id = getattr(test_plans.first(), 'project_id', None)
        is_archive = get_boolean(request, _IS_ARCHIVE)
        params = validate_query_params_data(
            request.query_params,
            labels=NumberInFilter(),
            not_labels=NumberInFilter(),
        )
        return Response(
            TestPlanSelector().testplan_statistics(
                test_plans,
                params,
                is_whole_project,
                is_archive,
                project_id,
            ),
        )

    @get_plan_histogram_schema
    @action(detail=True)
    def get_histogram(self, request, pk):
        test_plans = self.get_statistic_objects(pk)
        is_whole_project = False
        project_id = getattr(test_plans.first(), 'project_id', None)
        is_archive = get_boolean(request, _IS_ARCHIVE)
        params = validate_query_params_data(
            request.query_params,
            labels=NumberInFilter(),
            not_labels=NumberInFilter(),
        )

        return Response(
            TestPlanSelector().testplan_histogram(
                test_plans,
                params,
                is_whole_project,
                is_archive,
                project_id,
            ),
        )


@plan_list_schema
class TestPlanViewSet(TestyModelViewSet, TestyArchiveMixin):
    serializer_class = TestPlanOutputSerializer
    queryset = TestPlan.objects.none()
    permission_classes = [IsAuthenticated, IsAdminOrForbidArchiveUpdate, TestPlanPermission]
    pagination_class = StandardSetPagination
    lookup_value_regex = r'\d+'
    schema_tags = ['Test plans']

    @property
    def search_fields(self):
        if self.action == _LIST:
            return ['title']
        elif self.action == _ACTIVITY:
            return ['history_user__username', 'test__case__name', 'history_date']

    @property
    def filter_backends(self):
        if self.action == _ACTIVITY:
            return [DjangoFilterBackend, SearchFilter]
        return [DjangoFilterBackend, TestPlanSearchFilter]

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return PlanFilterV1
        elif self.action == _ACTIVITY:
            return ActivityFilter

    def get_queryset(self):
        if self.action in {'recovery_list', 'restore', 'delete_permanently'}:
            return TestPlanSelector().testplan_deleted_list()
        if get_boolean(self.request, 'treeview') and self.action == _LIST:
            qs = TestPlanSelector.testplan_list_raw()
            qs = self.filter_queryset(qs)
            if not self.request.query_params.get('ordering'):
                qs = qs.order_by('-started_at')
            return TestPlanSelector().testplan_treeview_list(
                parent_id=get_integer(self.request, 'parent'),
                qs=qs,
            )
        if self.action == 'breadcrumbs_view':
            return TestPlanSelector.testplan_list_raw()
        return TestPlanSelector().testplan_list_v1(get_boolean(self.request, _IS_ARCHIVE))

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestPlanRetrieveSerializer
        if self.action == 'copy_plans':
            return TestPlanCopySerializer
        if get_boolean(self.request, 'treeview'):
            return TestPlanTreeSerializer
        return TestPlanOutputSerializer

    @plan_activity_schema
    @action(methods=[_GET], url_path=_ACTIVITY, url_name=_ACTIVITY, detail=True)
    def activity(self, request, pk, *args, **kwargs):
        instance = TestPlan.objects.get(pk=pk)
        history_records = TestResultSelector.result_cascade_history_list_by_test_plan(instance)
        history_records = self.filter_queryset(queryset=history_records)
        paginator = StandardSetPagination()
        result_page = paginator.paginate_queryset(history_records, request)
        serializer = TestResultActivitySerializer(result_page, many=True, context={_REQUEST: request})
        final_data = {}
        plan_ids = {test_result['plan_id'] for test_result in serializer.data}
        ids_to_breadcrumbs = TestPlanSelector().testplan_breadcrumbs_by_ids(plan_ids)
        for result_dict in serializer.data:
            result_dict['breadcrumbs'] = ids_to_breadcrumbs[result_dict.pop('plan_id')]
            action_day = result_dict.pop('action_day')
            if results_list := final_data.get(action_day):
                results_list.append(result_dict)
                continue
            final_data[action_day] = [result_dict]
        return paginator.get_paginated_response(final_data)

    @plan_labels_schema
    @action(methods=[_GET], url_path=_LABELS, url_name=_LABELS, detail=True)
    def labels_view(self, request, *args, **kwargs):
        instance = self.get_object()
        labels = LabelSelector().label_list_by_testplans([instance.id])
        return Response(LabelSerializer(labels, many=True, context={_REQUEST: request}).data)

    @plan_suites_ids_schema
    @action(methods=[_GET], url_path='suites', url_name='suites', detail=True)
    def suites_by_plan(self, request, pk):
        plans = TestPlanSelector().plans_by_ids([pk])
        suites = TestSuiteSelector().suites_by_plans(plans)
        return Response(TestSuiteTreeBreadcrumbsSerializer(suites, many=True, context={_REQUEST: self.request}).data)

    @plan_case_ids_schema
    @action(methods=[_GET], url_path='cases', url_name='cases', detail=True)
    def cases_by_plan(self, request, pk):
        case_ids = TestCaseSelector().case_ids_by_testplan_id(
            pk,
            include_children=get_boolean(request, 'include_children', default=True),
        ).order_by('id')
        return Response(data={'case_ids': case_ids})

    @plan_progress_schema
    @action(methods=[_GET], url_path='progress', url_name='progress', detail=True)
    def plan_progress(self, request, pk):
        period = PeriodDateTime(request, 'start_date', 'end_date')
        plans = TestPlanSelector().get_plan_progress(pk, period=period)
        return Response(TestPlanProgressSerializer(plans, many=True).data)

    @plan_create_schema
    def create(self, request, *args, **kwargs):
        serializer = TestPlanInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        test_plans = []
        if serializer.validated_data.get('parameters'):
            test_plans = TestPlanService().testplan_bulk_create(serializer.validated_data)
        else:
            test_plans.append(TestPlanService().testplan_create(serializer.validated_data))
        return Response(
            TestPlanMinSerializer(test_plans, many=True, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @plan_update_schema
    def update(self, request, *args, **kwargs):
        test_plan = self.get_object()
        self.check_object_permissions(request, test_plan)
        serializer = TestPlanUpdateSerializer(
            data=request.data,
            instance=test_plan,
            context=self.get_serializer_context(),
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        try:
            test_plan = TestPlanService().testplan_update(test_plan=test_plan, data=serializer.validated_data)
        except InvalidMove as err:
            return Response({'errors': [str(err)]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            TestPlanOutputSerializer(test_plan, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK,
        )

    @plan_copy_schema
    @action(methods=['post'], url_path='copy', url_name='copy', detail=False)
    def copy_plans(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plans = CopyService.plans_copy(serializer.validated_data)
        return Response(
            TestPlanOutputSerializer(
                plans,
                many=True,
                context=self.get_serializer_context(),
            ).data,
        )

    @action(methods=['get'], url_path='statuses', url_name='statuses', detail=True)
    def get_statuses(self, request, pk):
        instance = TestPlanSelector().testplan_get_by_pk(pk)
        testplans_ids = TestPlanSelector().get_testplan_descendants_ids_by_testplan(instance)
        statuses_ids = (
            Test.objects
            .filter(plan_id__in=testplans_ids)
            .distinct('last_status')
            .values_list('last_status', flat=True)
        )
        statuses = ResultStatusSelector.sort_status_queryset(
            ResultStatusSelector.extended_status_list_by_ids(statuses_ids), instance.project,
        )
        return Response(ResultStatusSerializer(statuses, many=True, context=self.get_serializer_context()).data)

    @action(methods=['get'], url_path='activity/statuses', url_name='activity-statuses', detail=True)
    def get_activity_statuses(self, request, pk):
        testplan_selector = TestPlanSelector()
        instance = testplan_selector.testplan_get_by_pk(pk)
        testplans_ids = testplan_selector.get_testplan_descendants_ids_by_testplan(instance)
        statuses_ids = (
            TestResult.history
            .prefetch_related(_RESULT_STATUS, 'test__plan_id')
            .filter(test__plan_id__in=testplans_ids)
            .order_by(_RESULT_STATUS)
            .distinct(_RESULT_STATUS)
            .values_list(_RESULT_STATUS, flat=True)
        )
        statuses = ResultStatusSelector.sort_status_queryset(
            ResultStatusSelector.extended_status_list_by_ids(statuses_ids), instance.project,
        )
        return Response(ResultStatusSerializer(statuses, many=True, context=self.get_serializer_context()).data)


@test_list_schema
class TestViewSet(TestyModelViewSet, TestyArchiveMixin):
    queryset = TestSelector().test_list_with_last_status()
    serializer_class = TestSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    pagination_class = StandardSetPagination
    permission_classes = [IsAdminOrForbidArchiveUpdate, IsAuthenticated]
    http_method_names = [_GET, 'post', 'put', 'patch', 'head', 'options', 'trace']
    schema_tags = ['Tests']
    search_fields = ['case__name']

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return TestFilter

    def perform_update(self, serializer: TestSerializer):
        serializer.instance = TestService().test_update(
            serializer.instance,
            serializer.validated_data,
            self.request.user,
        )

    def get_queryset(self, test_plan_ids: list[int] | None = None):
        filters = {'plan_id__in': test_plan_ids} if test_plan_ids else {}
        if self.action in {'archive_preview', 'archive_objects', 'restore_archived'}:
            return TestSelector().test_list()
        return TestSelector().test_list_with_last_status(filter_condition=filters)

    def get_serializer_class(self):
        if self.action == 'bulk_update_tests':
            return BulkUpdateTestsSerializer
        return TestSerializer

    @test_bulk_update_schema
    @action(methods=['put'], url_path='bulk-update', url_name='bulk-update', detail=False)
    def bulk_update_tests(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = self.get_queryset(test_plan_ids=[serializer.validated_data.pop('current_plan')])
        filter_conditions = serializer.validated_data.pop('filter_conditions', {})
        if filter_conditions:
            queryset = self._filter_queryset_from_request_payload(queryset, filter_conditions)
        tests = TestService().bulk_update_tests(queryset, serializer.validated_data, request.user)
        return Response(TestSerializer(tests, many=True, context=self.get_serializer_context()).data)

    def _filter_queryset_from_request_payload(self, queryset: QuerySet[Test], filter_conditions: dict[str, Any]):
        mocked_request = mock_request_with_query_params(filter_conditions)
        queryset = TestyBaseSearchFilter().filter_queryset(mocked_request, queryset, self)
        test_filter = TestFilter(mocked_request.GET, queryset, request=mocked_request)
        test_filter.is_valid()
        return test_filter.filter_queryset(queryset)


@result_list_schema
class TestResultViewSet(ModelViewSet, TestyArchiveMixin):
    queryset = TestResultSelector().result_list()
    permission_classes = [IsAuthenticated, ForbidChangesOnArchivedProject, TestResultPermission]
    serializer_class = TestResultSerializer
    filter_backends = [DjangoFilterBackend]
    schema_tags = ['Test results']

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return TestResultFilter

    def perform_update(self, serializer: TestResultSerializer):
        serializer.instance = TestResultService().result_update(serializer.instance, serializer.validated_data)

    def perform_create(self, serializer: TestResultSerializer):
        request = serializer.context.get(_REQUEST)
        serializer.instance = TestResultService().result_create(serializer.validated_data, request.user)

    @action(methods=['delete'], url_path='attributes', url_name='attributes', detail=False)
    def destroy_by_attribute(self, request, *args, **kwargs):
        TestResultSelector.result_by_attributes(
            request.query_params.get('plan'),
            request.query_params.get('attribute_name'),
            request.query_params.get('attribute_value'),
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action in {'create', 'partial_update'}:
            return TestResultInputSerializer
        return TestResultSerializer


class ResultStatusViewSet(TestyModelViewSet):
    queryset = ResultStatusSelector.status_list_raw()
    serializer_class = ResultStatusSerializer
    permission_classes = [IsAuthenticated, ResultStatusPermission]
    filter_backends = [DjangoFilterBackend]
    schema_tags = ['Statuses']

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return ResultStatusFilter

    def get_queryset(self):
        if self.action in {'recovery_list', 'restore', 'delete_permanently'}:
            return ResultStatusSelector.status_deleted_list()
        elif self.action == 'list':
            project = ProjectSelector.project_by_id(self.request.query_params.get('project'))
            return ResultStatusSelector.status_list(
                project=project,
                ordering=True,
            )
        return ResultStatusSelector.status_list_raw()

    def perform_create(self, serializer: ResultStatusSerializer):
        serializer.instance = ResultStatusService().status_create(serializer.validated_data)

    def perform_update(self, serializer: ResultStatusSerializer):
        serializer.instance = ResultStatusService().status_update(serializer.instance, serializer.validated_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ResultStatusService.delete_status(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
