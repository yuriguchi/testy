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
from typing import Optional

from drf_yasg import openapi

project_param = openapi.Parameter(
    'project',
    openapi.IN_QUERY,
    description='Parameter that specifies project',
    type=openapi.TYPE_NUMBER,
    required=True,
)
treeview_param = openapi.Parameter(
    'treeview',
    openapi.IN_QUERY,
    description='Parameter that specifies if output of tree structures should be as tree. Accepts: True, true, 1...',
    type=openapi.TYPE_BOOLEAN,
)
is_flat = openapi.Parameter(
    'is_flat',
    openapi.IN_QUERY,
    description='Parameter is used when searching/filtering within tree structures to get flat output and not treeview',
    type=openapi.TYPE_BOOLEAN,
)


def search_param_factory(*args) -> openapi.Parameter:
    description = (
        'Parameter for ordering list responses, '
        f'add "-" to field name for descending order by: {", ".join(args)}'  # noqa: WPS326
    )
    return openapi.Parameter(
        'search',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description=description,
    )


def ordering_param_factory(*args) -> openapi.Parameter:
    description = f'Parameter for case insensitive search in following fields: {", ".join(args)}'  # noqa: WPS237
    return openapi.Parameter(
        'ordering',
        openapi.IN_QUERY,
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(type=openapi.TYPE_STRING),
        description=description,
    )


def list_param_factory(name: str, custom_description: Optional[str] = None) -> openapi.Parameter:
    return openapi.Parameter(
        name,
        openapi.IN_QUERY,
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(type=openapi.TYPE_INTEGER),
        description=custom_description or 'Filter by list of ids',
    )


def filter_param_by_id(name: str, custom_description: Optional[str] = None) -> openapi.Parameter:
    return openapi.Parameter(
        name,
        openapi.IN_QUERY,
        type=openapi.TYPE_INTEGER,
        description=custom_description or f'Filter by {name} id',
    )


common_ordering_filter = openapi.Parameter(
    'ordering',
    openapi.IN_QUERY,
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_STRING),
    description='Order by any fields that are valid lookups for model, "-" before field name for descending order',
)

is_archive_parameter = openapi.Parameter(
    'is_archive',
    openapi.IN_QUERY,
    type=openapi.TYPE_BOOLEAN,
    description='If True is provided display all plans including archive, if false only is_archive=False instances',
)
