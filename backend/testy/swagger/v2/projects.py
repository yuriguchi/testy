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

from testy.core.api.v2.serializers import ProjectStatisticsSerializer
from testy.swagger.common_query_parameters import is_archive_parameter
from testy.swagger.custom_schema_generation import TestyPaginatorInspector
from testy.tests_representation.api.v2.serializers import TestPlanProgressSerializer
from testy.users.api.v2.serializers import UserRoleSerializer

project_list_schema = swagger_auto_schema(
    manual_parameters=[
        is_archive_parameter,
    ],
    responses={status.HTTP_200_OK: ProjectStatisticsSerializer(many=True)},
    paginator_inspectors=[TestyPaginatorInspector],
)

project_members_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'users',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            'email',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            'first_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            'last_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            'is_active',
            openapi.IN_QUERY,
            type=openapi.TYPE_BOOLEAN,
        ),
        openapi.Parameter(
            'is_superuser',
            openapi.IN_QUERY,
            type=openapi.TYPE_BOOLEAN,
        ),
    ],
    responses={status.HTTP_200_OK: UserRoleSerializer(many=True)},
)

project_progress_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'started_at',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='Start of the period in iso format',
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='End of the period in iso format',
        ),
    ],
    responses={status.HTTP_200_OK: TestPlanProgressSerializer(many=True)},
    tags=['Statistics'],
)
