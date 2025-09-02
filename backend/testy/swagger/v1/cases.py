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
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from testy.swagger.common_query_parameters import is_archive_parameter, ordering_param_factory, search_param_factory
from testy.swagger.custom_schema_generation import TestyPaginatorInspector
from testy.swagger.serializers import TestWithBreadcrumbsSerializer
from testy.tests_description.api.v1.serializers import (
    TestCaseCopySerializer,
    TestCaseHistorySerializer,
    TestCaseInputWithStepsSerializer,
    TestCaseListSerializer,
    TestCaseRestoreSerializer,
    TestCaseRetrieveSerializer,
    TestSuiteTreeCasesSerializer,
)

_NAME = 'name'

cases_list_schema = method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_description='Returns list of test cases in different formats, depending on parameters.',
        manual_parameters=[
            is_archive_parameter,
            ordering_param_factory('id', _NAME),
            search_param_factory(_NAME),
            openapi.Parameter(
                'labels_condition',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Condition for boolean logic for labels, options are: and/or',
            ),
        ],
        responses={
            status.HTTP_200_OK: TestCaseListSerializer(many=True),
        },
    ),
)

cases_create_schema = swagger_auto_schema(
    request_body=TestCaseInputWithStepsSerializer,
    responses={status.HTTP_201_CREATED: TestCaseRetrieveSerializer()},
)

cases_update_schema = swagger_auto_schema(
    request_body=TestCaseInputWithStepsSerializer,
    responses={status.HTTP_200_OK: TestCaseRetrieveSerializer()},
)

cases_retrieve_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'version',
            openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Numeric string to show older version of chosen test case',
        ),
    ],
    responses={status.HTTP_200_OK: TestCaseRetrieveSerializer()},
)

cases_copy_schema = swagger_auto_schema(
    request_body=TestCaseCopySerializer,
    responses={status.HTTP_200_OK: TestCaseRetrieveSerializer(many=True)},
)

parameter = openapi.Parameter(
    'last_status',
    openapi.IN_QUERY,
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_INTEGER),
    description='List of status codes to filter by',
)

cases_tests_schema = swagger_auto_schema(
    manual_parameters=[
        search_param_factory(_NAME),
    ],
    responses={status.HTTP_200_OK: TestWithBreadcrumbsSerializer(many=True)},
    paginator_inspectors=[TestyPaginatorInspector],
)

cases_history_schema = swagger_auto_schema(
    manual_parameters=[
        ordering_param_factory('history_date', 'history_user', 'history_type'),
        search_param_factory(_NAME),
    ],
    responses={status.HTTP_200_OK: TestCaseHistorySerializer(many=True)},
    paginator_inspectors=[TestyPaginatorInspector],
)

cases_version_restore_schema = swagger_auto_schema(
    operation_description='Restore test cases to its former version',
    request_body=TestCaseRestoreSerializer,
    responses={status.HTTP_200_OK: TestCaseRetrieveSerializer()},
)
cases_search_schema = swagger_auto_schema(
    operation_description='Return treeview of suites with displaying case.',
    manual_parameters=[
        is_archive_parameter,
        ordering_param_factory('id', _NAME),
        search_param_factory(_NAME),
        openapi.Parameter(
            'labels_condition',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='Condition for boolean logic for labels, options are: and/or',
        ),
    ],
    responses={status.HTTP_200_OK: TestSuiteTreeCasesSerializer(many=True)},
)
