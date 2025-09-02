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
from functools import partial

import orjson
from django.db.models import F
from django.http import HttpResponse
from django_filters import CharFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from simple_history.utils import get_history_model_for_model

from testy.core.services.copy import CopyService
from testy.filters import TestyFilterBackend
from testy.paginations import StandardSetPagination
from testy.root.mixins import TestyArchiveMixin, TestyModelViewSet
from testy.swagger.serializers import TestWithBreadcrumbsSerializer
from testy.swagger.v2.cases import (
    cases_create_schema,
    cases_retrieve_schema,
    cases_update_schema,
    cases_version_restore_schema,
)
from testy.swagger.v2.suites import suite_copy_schema, suite_list_schema
from testy.tests_description.api.v2.serializers import (
    TestCaseCopySerializer,
    TestCaseHistorySerializer,
    TestCaseInputSerializer,
    TestCaseInputWithStepsSerializer,
    TestCaseListSerializer,
    TestCaseRestoreSerializer,
    TestCaseRetrieveSerializer,
    TestCaseUnionSerializer,
    TestSuiteBaseSerializer,
    TestSuiteCopyOutputSerializer,
    TestSuiteCopySerializer,
    TestSuiteOutputCreateSerializer,
    TestSuiteOutputSerializer,
    TestSuiteRetrieveSerializer,
    TestSuiteSerializer,
    TestSuiteTreeBreadcrumbsSerializer,
    TestSuiteUnionSerializer,
    TestSuiteUpdateOutputSerializer,
)
from testy.tests_description.filters import (
    CasesBySuiteFilter,
    SuiteProjectParentFilter,
    SuiteUnionFilterNoSearch,
    SuiteUnionOrderingFilter,
    TestCaseFilter,
    TestCaseFilterSearch,
    TestCaseHistoryFilter,
    TestSuiteFilter,
    UnionCaseFilter,
)
from testy.tests_description.models import TestCase, TestSuite
from testy.tests_description.permissions import TestCaseCopyPermission, TestSuiteCopyPermission
from testy.tests_description.selectors.cases import TestCaseSelector
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.tests_description.services.cases import TestCaseService
from testy.tests_description.services.suites import TestSuiteService
from testy.tests_representation.api.v2.serializers import TestSerializer
from testy.tests_representation.filters import TestFilterNested
from testy.tests_representation.models import Test
from testy.tests_representation.selectors.testplan import TestPlanSelector
from testy.tests_representation.selectors.tests import TestSelector
from testy.utilities.request import get_boolean, get_integer, validate_query_params_data
from testy.utilities.tree import get_breadcrumbs_treeview

_USER = 'user'
_GET = 'get'
_POST = 'post'
_COPY = 'copy'
_LIST = 'list'
_IS_ARCHIVE = 'is_archive'
_NAME = 'name'
_ID = 'id'

logger = logging.getLogger(__name__)


class TestCaseViewSet(TestyModelViewSet, TestyArchiveMixin):
    queryset = TestCaseSelector().case_list()
    serializer_class = TestCaseListSerializer
    permission_classes = [IsAuthenticated, TestCaseCopyPermission]
    filter_backends = [TestyFilterBackend]
    pagination_class = StandardSetPagination
    http_method_names = [_GET, _POST, 'put', 'delete', 'head', 'options', 'trace']
    lookup_value_regex = r'\d+'
    schema_tags = ['Test cases']

    @property
    def filterset_class(self):
        match self.action:
            case 'list':
                return TestCaseFilter
            case 'get_tests':
                return TestFilterNested
            case 'get_history':
                return TestCaseHistoryFilter
            case 'cases_search':
                return TestCaseFilterSearch

    def get_queryset(self):
        match self.action:
            case 'recovery_list' | 'restore' | 'delete_permanently':
                return TestCaseSelector().case_deleted_list()
            case 'restore_archived':
                return TestCaseSelector().case_list({_IS_ARCHIVE: True})
            case 'cases_search':
                return TestCaseSelector().case_list_with_label_names()
            case 'get_history':
                return get_history_model_for_model(TestCase).objects.none()
            case 'get_tests':
                return Test.objects.none()

        qs = TestCaseSelector().case_list()
        return TestSuiteSelector.annotate_suite_path(qs, 'suite__path')

    def get_serializer_class(self):
        match self.action:
            case 'copy_cases':
                return TestCaseCopySerializer
            case 'create' | 'update':
                if get_boolean(self.request, 'is_steps', method='data'):
                    return TestCaseInputWithStepsSerializer
                return TestCaseInputSerializer
            case 'retrieve':
                return TestCaseRetrieveSerializer
        return TestCaseListSerializer

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
        is_partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=is_partial)
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

    @swagger_auto_schema(responses={status.HTTP_200_OK: TestCaseRetrieveSerializer(many=True)})
    @action(methods=[_POST], url_path=_COPY, url_name=_COPY, detail=False)
    def copy_cases(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cases = CopyService.cases_copy(serializer.validated_data)
        return Response(TestCaseRetrieveSerializer(cases, many=True, context=self.get_serializer_context()).data)

    @swagger_auto_schema(responses={status.HTTP_200_OK: TestWithBreadcrumbsSerializer(many=True)})
    @action(methods=[_GET], url_path='tests', url_name='tests', detail=True, suffix='List')
    def get_tests(self, request, pk):
        qs = TestSelector().test_list_with_last_status(filter_condition={'case_id': pk})
        qs = TestSuiteSelector.annotate_suite_path(qs, 'case__suite__path')
        page = self.paginate_queryset(self.filter_queryset(qs))
        serializer = TestSerializer(page, many=True, context=self.get_serializer_context())
        response_tests = []
        plan_ids = {test['plan'] for test in serializer.data}
        ids_to_breadcrumbs = TestPlanSelector().testplan_breadcrumbs_by_ids(plan_ids)
        for test in serializer.data:
            test['breadcrumbs'] = ids_to_breadcrumbs[test.get('plan')]
            response_tests.append(test)
        return self.get_paginated_response(response_tests)

    @swagger_auto_schema(responses={status.HTTP_200_OK: TestCaseHistorySerializer(many=True)})
    @action(methods=[_GET], url_path='history', url_name='history', detail=True, suffix='List')
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
            suite_id = case['suite_id']
            if suite_id not in suite_map:
                logger.error(f'Suite {suite_id} from case {case[_ID]} was not found, probably suite was deleted')
                continue
            suite_map[suite_id]['test_cases'].append(case)
        data = orjson.dumps(list(tree.values()))
        return HttpResponse(content=data, content_type='application/json')


@suite_list_schema
class TestSuiteViewSet(TestyModelViewSet):
    permission_classes = [IsAuthenticated, TestSuiteCopyPermission]
    queryset = TestSuite.objects.none()
    serializer_class = TestSuiteSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardSetPagination
    lookup_value_regex = r'\d+'
    schema_tags = ['Test suites']

    @property
    def filterset_class(self):
        if self.action in {_LIST, 'list_union'}:
            return TestSuiteFilter
        if self.action == 'descendants_tree_by_root':
            return SuiteProjectParentFilter

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return TestSuiteOutputSerializer
            case 'cases':
                return TestCaseListSerializer
            case 'retrieve':
                return TestSuiteRetrieveSerializer
            case 'recovery_list' | 'restore' | 'delete_permanently':
                return TestSuiteBaseSerializer
            case 'descendants_tree' | 'descendants_tree_by_root':
                return TestSuiteTreeBreadcrumbsSerializer
        if get_boolean(self.request, 'is_flat'):
            return TestSuiteBaseSerializer
        return TestSuiteSerializer

    def get_queryset(self):
        match self.action:
            case 'list_union' | 'list' | 'descendants_tree_by_root':
                return TestSuiteSelector.suite_list_raw()
            case 'retrieve':
                return TestSuiteSelector.suite_list_retrieve()
            case 'recovery_list' | 'restore' | 'delete_permanently':
                return TestSuiteSelector.suite_deleted_list()
        return TestSuiteSelector.list_qs(TestSuiteSelector.suite_list_raw()).order_by(_NAME)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance = TestSuiteService().suite_create(serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        data = TestSuiteOutputCreateSerializer(serializer.instance, context=self.get_serializer_context()).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        is_partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=is_partial)
        serializer.is_valid(raise_exception=True)
        serializer.instance = TestSuiteService().suite_update(serializer.instance, serializer.validated_data)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(
            TestSuiteUpdateOutputSerializer(
                instance,
                context=self.get_serializer_context(),
            ).data,
        )

    @action(methods=[_GET], url_path='ancestors', url_name='ancestors', detail=True)
    def ancestors(self, request, *args, **kwargs):
        instance = self.get_object()
        ids = TestSuiteSelector.list_ancestors_flat(instance)
        return Response(ids)

    @action(methods=[_GET], url_path='descendants-tree', url_name='all-descendants-tree', detail=False)
    def descendants_tree_by_root(self, request, *args, **kwargs):
        suites = self.filter_queryset(self.get_queryset())
        parent_id = get_integer(request, 'parent')
        suites = TestSuiteSelector.suites_breadcrumbs_by_root(suites, parent_id)
        content = orjson.dumps(suites)
        return HttpResponse(content=content, content_type='application/json')

    @action(methods=[_GET], url_path='descendants-tree', url_name='descendants-tree', detail=True)
    def descendants_tree(self, request, *args, **kwargs):
        instance = self.get_object()
        suites = TestSuiteSelector.suites_by_ids([instance.pk], 'pk')
        suites = TestSuiteSelector.suites_breadcrumbs(suites)
        return Response(self.get_serializer(suites, many=True, context=self.get_serializer_context()).data)

    @action(methods=['get'], url_path='cases', url_name='cases', detail=True)
    def cases(self, request, pk):
        suite = self.get_object()
        suite_ids = [suite.pk]
        if get_boolean(request, 'show_descendants'):
            suite_ids = suite.get_descendants(include_self=True).values_list('id', flat=True)
        cases = TestCaseSelector.case_list_by_suite_ids(suite_ids)
        cases = TestSuiteSelector.annotate_suite_path(cases, 'suite__path')
        cases = CasesBySuiteFilter(request.query_params, request=request, queryset=cases).qs
        page = self.paginate_queryset(cases)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

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
        return Response(TestSuiteCopyOutputSerializer(suites, many=True, context=self.get_serializer_context()).data)

    def list(self, request, *args, **kwargs):
        search_param = request.query_params.get('search') or request.query_params.get('treesearch')
        qs = TestSuiteSelector.list_qs(self.get_queryset(), search_param)
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=[_GET], url_name='union', url_path='union', detail=False)
    def list_union(self, request):
        common_filters = {'search', 'treesearch'}
        parent_id = get_integer(request, 'parent')
        suites = self.filter_queryset(self.get_queryset())

        params = validate_query_params_data(request.query_params, omit_empty=True, search=CharFilter())
        has_common_filters = bool(set(params.keys()).intersection(common_filters))

        cases = TestCaseSelector.case_list_union(suites, parent_id, has_common_filters)

        cases_filter = UnionCaseFilter(request.query_params, request=request, queryset=cases)
        cases = cases_filter.qs
        if cases_filter.is_filtered({'project'}):
            suites = TestSuite.objects.filter(
                id__in=cases.values_list('suite_id', flat=True).distinct(),
            ).get_ancestors(include_self=True)
            suites = SuiteUnionFilterNoSearch(request.query_params, request=request, queryset=suites).qs

        if has_common_filters:
            suites = suites | self.filter_queryset(self.get_queryset())

        suites_union = TestSuiteSelector.suites_cases_union(
            cases,
            parent_id,
            suites,
        )
        suites_union = SuiteUnionOrderingFilter(request.query_params, queryset=suites_union).qs

        page = self.paginate_queryset(suites_union)
        context = self.get_serializer_context()
        data = TestSuiteSelector().get_union_data(
            page,
            partial(TestSuiteUnionSerializer, context=context),
            partial(TestCaseUnionSerializer, context=context),
        )
        return self.get_paginated_response(data)

    @action(methods=[_GET], url_path='breadcrumbs', url_name='breadcrumbs', detail=True)
    def breadcrumbs(self, request, *args, **kwargs):
        instance = self.get_object()
        tree = TestSuiteSelector.suite_list_ancestors(instance)
        return Response(get_breadcrumbs_treeview(tree, len(tree) - 1, lambda suite: suite.name))
