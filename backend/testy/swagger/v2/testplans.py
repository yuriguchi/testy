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
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from testy.swagger.common_query_parameters import is_archive_parameter
from testy.swagger.serializers import CaseIdsSerializer, TestPlanStatisticsSerializer
from testy.swagger.v1.testplans import histogram_response_schema
from testy.tests_representation.api.v2.serializers import (
    TestPlanInputSerializer,
    TestPlanMinSerializer,
    TestPlanOutputSerializer,
    TestPlanUpdateSerializer,
    TestResultActivitySerializer,
)

default_histogram_manual_parameters = [
    is_archive_parameter,
    openapi.Parameter(
        'labels_condition',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description='Condition for boolean logic for labels, options are: and/or',
    ),
    openapi.Parameter(
        'labels',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        'not_labels',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        'start_date',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description='start date in iso format',
    ),
    openapi.Parameter(
        'end_date',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description='end date in iso format',
    ),
    openapi.Parameter(
        'attribute',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description='Test result attribute',
    ),
]

default_statistics_manual_parameters = [
    is_archive_parameter,
    openapi.Parameter(
        'estimate_period',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        'labels_condition',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description='Condition for boolean logic for labels, options are: and/or',
    ),
    openapi.Parameter(
        'labels',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        'not_labels',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
    ),
]

get_plan_histogram_schema = swagger_auto_schema(
    manual_parameters=default_histogram_manual_parameters,
    responses={status.HTTP_200_OK: histogram_response_schema},
)
get_project_plan_histogram_schema = swagger_auto_schema(
    manual_parameters=[
        *default_histogram_manual_parameters,
        openapi.Parameter(
            'parent',
            openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Test plan id',
        ),
        openapi.Parameter(
            'project',
            openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Project id for statistic',
        ),
    ],
    responses={status.HTTP_200_OK: histogram_response_schema},
)
get_plan_statistic_schema = swagger_auto_schema(
    manual_parameters=default_statistics_manual_parameters,
    responses={status.HTTP_200_OK: TestPlanStatisticsSerializer(many=True)},
)
get_project_plan_statistic_schema = swagger_auto_schema(
    manual_parameters=[
        *default_histogram_manual_parameters,
        openapi.Parameter(
            'parent',
            openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Test plan id',
        ),
        openapi.Parameter(
            'project',
            openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Project id for statistic',
        ),
    ],
    responses={status.HTTP_200_OK: TestPlanStatisticsSerializer(many=True)},
)

plan_activity_schema = swagger_auto_schema(
    operation_description='Get activity of test results by users for test plan and its nested ones.',
    responses={
        status.HTTP_200_OK: TestResultActivitySerializer(many=True),
    },
)
plan_case_ids_schema = swagger_auto_schema(
    operation_description='Get list of cases used in provided test plan',
    manual_parameters=[
        openapi.Parameter(
            'include_children',
            openapi.IN_QUERY,
            type=openapi.TYPE_BOOLEAN,
            description='Include child test plans case ids or not, True is set if not provided',
        ),
    ],
    responses={status.HTTP_200_OK: CaseIdsSerializer()},
)
plan_progress_schema = swagger_auto_schema(
    operation_description='Get testplan progress.',
    manual_parameters=[
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='start date in iso format',
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='end date in iso format',
        ),
    ],
    tags=['Statistics'],
)

plan_create_schema = swagger_auto_schema(
    request_body=TestPlanInputSerializer,
    responses={status.HTTP_201_CREATED: TestPlanMinSerializer(many=True)},
)
plan_update_schema = swagger_auto_schema(
    request_body=TestPlanUpdateSerializer,
    responses={status.HTTP_201_CREATED: TestPlanOutputSerializer()},
)
