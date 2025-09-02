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

import orjson
from django.db.models import F
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from mptt.exceptions import InvalidMove
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from simple_history.utils import get_history_model_for_model

from testy.core.services.copy import CopyService
from testy.paginations import StandardSetPagination
from testy.root.mixins import TestyArchiveMixin, TestyModelViewSet
from testy.swagger.v1.cases import (
    cases_copy_schema,
    cases_create_schema,
    cases_history_schema,
    cases_list_schema,
    cases_retrieve_schema,
    cases_search_schema,
    cases_tests_schema,
    cases_update_schema,
    cases_version_restore_schema,
)
from testy.swagger.v1.suites import suite_copy_schema, suite_list_schema, suite_retrieve_schema
from testy.tests_description.api.v1.serializers import (
    TestCaseCopySerializer,
    TestCaseHistorySerializer,
    TestCaseInputSerializer,
    TestCaseInputWithStepsSerializer,
    TestCaseListSerializer,
    TestCaseRestoreSerializer,
    TestCaseRetrieveSerializer,
    TestSuiteBaseSerializer,
    TestSuiteCopySerializer,
    TestSuiteRetrieveSerializer,
    TestSuiteSerializer,
    TestSuiteTreeSerializer,
)
from testy.tests_description.filters import (
    TestCaseFilter,
    TestCaseHistoryFilter,
    TestSuiteFilter,
    TestSuiteSearchFilter,
)
from testy.tests_description.models import TestCase, TestSuite
from testy.tests_description.permissions import TestCaseCopyPermission, TestSuiteCopyPermission
from testy.tests_description.selectors.cases import TestCaseSelector
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.tests_description.services.cases import TestCaseService
from testy.tests_description.services.suites import TestSuiteService
from testy.tests_representation.api.v1.serializers import TestSerializer
from testy.tests_representation.filters import TestFilterNested
from testy.tests_representation.models import Test
from testy.tests_representation.selectors.testplan import TestPlanSelector
from testy.tests_representation.selectors.tests import TestSelector
from testy.utilities.request import get_boolean

_USER = 'user'
_GET = 'get'
_POST = 'post'
_COPY = 'copy'
_LIST = 'list'
_IS_ARCHIVE = 'is_archive'
_NAME = 'name'
_ID = 'id'


@cases_list_schema
class TestCaseViewSet(TestyModelViewSet, TestyArchiveMixin):
    queryset = TestCaseSelector().case_list()
    serializer_class = TestCaseListSerializer
    permission_classes = [IsAuthenticated, TestCaseCopyPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    pagination_class = StandardSetPagination
    http_method_names = [_GET, _POST, 'put', 'delete', 'head', 'options', 'trace']
    search_fields = [_NAME]
    lookup_value_regex = r'\d+'
    schema_tags = ['Test cases']

    @property
    def filterset_class(self):
        if self.action in {'list', 'cases_search'}:
            return TestCaseFilter
        elif self.action == 'get_tests':
            return TestFilterNested
        elif self.action == 'get_history':
            return TestCaseHistoryFilter

    def get_queryset(self):
        if self.action in {'recovery_list', 'restore', 'delete_permanently'}:
            return TestCaseSelector().case_deleted_list()
        if self.action == 'restore_archived':
            return TestCaseSelector().case_list({_IS_ARCHIVE: True})
        if self.action == 'cases_search':
            return TestCaseSelector().case_list_with_label_names()
        if self.action == 'get_history':
            return get_history_model_for_model(TestCase).objects.none()
        if self.action == 'get_tests':
            return Test.objects.none()
        return TestCaseSelector().case_list()

    def get_serializer_class(self):
        if self.action == 'copy_cases':
            return TestCaseRetrieveSerializer
        if self.action in {'create', 'update'}:
            if get_boolean(self.request, 'is_steps', method='data'):
                return TestCaseInputWithStepsSerializer
            return TestCaseInputSerializer
        return super().get_serializer_class()

    @cases_create_schema
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('is_steps', False):
            test_case = TestCaseService().case_with_steps_create({_USER: request.user, **serializer.validated_data})
        else:
            test_case = TestCaseService().case_create({_USER: request.user, **serializer.validated_data})
        serializer_output = TestCaseRetrieveSerializer(test_case, context=self.get_serializer_context())
        headers = self.get_success_headers(serializer_output.data)
        return Response(serializer_output.data, status=status.HTTP_201_CREATED, headers=headers)

    @cases_update_schema
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get('is_steps', False):
            instance = TestCaseService().case_with_steps_update(
                serializer.instance, {
                    _USER: request.user, **serializer.validated_data,
                },
            )
        else:
            instance = TestCaseService().case_update(
                serializer.instance, {
                    _USER: request.user, **serializer.validated_data,
                },
            )

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(TestCaseRetrieveSerializer(instance, context=self.get_serializer_context()).data)

    @cases_retrieve_schema
    def retrieve(self, request, pk=None, **kwargs):
        instance = self.get_object()
        version = request.query_params.get('version')
        instance, version = TestCaseSelector.case_by_version(instance, version)
        serializer = TestCaseRetrieveSerializer(instance, version=version, context=self.get_serializer_context())
        return Response(serializer.data)

    @cases_copy_schema
    @action(methods=[_POST], url_path=_COPY, url_name=_COPY, detail=False)
    def copy_cases(self, request):
        serializer = TestCaseCopySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cases = CopyService.cases_copy(serializer.validated_data)
        return Response(self.get_serializer(cases, many=True).data)

    @cases_tests_schema
    @action(methods=[_GET], url_path='tests', url_name='tests', detail=True)
    def get_tests(self, request, pk):
        qs = TestSelector.test_list_raw()
        queryset = TestSelector().test_list_with_last_status(qs, {'case_id': pk})
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        serializer = TestSerializer(page, many=True, context=self.get_serializer_context())
        response_tests = []
        plan_ids = {test['plan'] for test in serializer.data}
        ids_to_breadcrumbs = TestPlanSelector().testplan_breadcrumbs_by_ids(plan_ids)
        for test in serializer.data:
            test['breadcrumbs'] = ids_to_breadcrumbs[test.get('plan')]
            response_tests.append(test)
        return self.get_paginated_response(response_tests)

    @cases_history_schema
    @action(methods=[_GET], url_path='history', url_name='history', detail=True)
    def get_history(self, request, pk):
        pagination = StandardSetPagination()
        queryset = TestCaseSelector.get_history_by_case_id(pk)
        queryset = self.filter_queryset(queryset)
        page = pagination.paginate_queryset(queryset, request) or queryset
        serializer = TestCaseHistorySerializer(
            page,
            context=self.get_serializer_context(),
            many=True,
        )
        return pagination.get_paginated_response(serializer.data)

    @cases_version_restore_schema
    @action(methods=[_POST], url_path='version/restore', url_name='restore-version', detail=True)
    def restore_case_version(self, request, pk):
        instance = self.get_object()
        serializer = TestCaseRestoreSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_test_case = TestCaseService.restore_version(serializer.validated_data.get('version'), pk)
        return Response(TestCaseRetrieveSerializer(updated_test_case, context=self.get_serializer_context()).data)

    @cases_search_schema
    @action(methods=[_GET], url_path='search', url_name='search', detail=False)
    def cases_search(self, request):
        cases = self.get_queryset()
        cases = self.filter_queryset(cases)
        suites = TestSuite.objects.filter(
            id__in=cases.values_list('suite_id', flat=True),
        ).get_ancestors(
            include_self=True,
        ).annotate(
            title=F(_NAME),
        ).values(_ID, _NAME, 'title', 'parent_id').order_by('name')
        suite_map = {}
        tree = {}
        for suite in suites:
            suite['children'] = []
            suite['test_cases'] = []
            suite_map[suite['id']] = suite
            if suite['parent_id'] is None:
                tree[suite['id']] = suite
        for suite in suites:
            if parent_id := suite['parent_id']:
                parent = suite_map.get(parent_id)
                parent['children'].append(suite)
        for case in cases.values(_ID, _NAME, 'suite_id', 'labels', 'is_archive').order_by('name'):
            suite_map[case['suite_id']]['test_cases'].append(case)
        data = orjson.dumps(list(tree.values()))
        return HttpResponse(content=data, content_type='application/json')


@suite_list_schema
@suite_retrieve_schema
class TestSuiteViewSet(TestyModelViewSet):
    permission_classes = [IsAuthenticated, TestSuiteCopyPermission]
    queryset = TestSuite.objects.none()
    serializer_class = TestSuiteSerializer
    filter_backends = [DjangoFilterBackend, TestSuiteSearchFilter]
    pagination_class = StandardSetPagination
    search_fields = [_NAME]
    schema_tags = ['Test suites']

    @property
    def filterset_class(self):
        if self.action == 'list':
            return TestSuiteFilter

    def perform_create(self, serializer: TestSuiteSerializer):
        serializer.instance = TestSuiteService().suite_create(serializer.validated_data)

    def perform_update(self, serializer: TestSuiteSerializer):
        serializer.instance = TestSuiteService().suite_update(serializer.instance, serializer.validated_data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except InvalidMove as err:
            return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(self.get_serializer(self.get_object()).data)

    def get_serializer_class(self):
        action_serialized_flat = self.action in {'recovery_list', 'restore', 'delete_permanently', _LIST}
        if self.action == 'retrieve':
            return TestSuiteRetrieveSerializer
        if get_boolean(self.request, 'treeview'):
            return TestSuiteTreeSerializer
        if action_serialized_flat or get_boolean(self.request, 'is_flat'):
            return TestSuiteBaseSerializer
        return TestSuiteSerializer

    def get_queryset(self):
        treeview = get_boolean(self.request, 'treeview')
        if self.action in {'recovery_list', 'restore', 'delete_permanently'}:
            return TestSuiteSelector().suite_deleted_list()
        if treeview and self.action == _LIST:
            parent = self.request.query_params.get('parent')
            root_only = parent is None or parent == ''  # if parent is provided turn off root_only
            return TestSuiteSelector().suite_list_treeview(root_only=root_only)
        if self.action == 'retrieve':
            return TestSuiteSelector.suite_list_retrieve()
        if self.action == 'breadcrumbs_view':
            return TestSuiteSelector.suite_list_raw()
        return TestSuiteSelector().suite_list()

    @suite_copy_schema
    @action(methods=[_POST], url_path=_COPY, url_name=_COPY, detail=False)
    def copy_suites(self, request):
        serializer = TestSuiteCopySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if suite := serializer.validated_data.get('dst_suite_id'):
            if suite.project != serializer.validated_data.get('dst_project_id'):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'errors': ["Project and Suite's project must be same"]},
                )
        suites = CopyService.suites_copy(serializer.validated_data)
        return Response(TestSuiteBaseSerializer(suites, many=True, context=self.get_serializer_context()).data)
