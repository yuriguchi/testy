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
from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters import rest_framework as filters

from testy.filters import FilterListMixin, case_insensitive_filter
from testy.users.choices import UserAllowedPermissionCodenames

UserModel = get_user_model()


class UserFilter(filters.FilterSet, FilterListMixin):
    username = case_insensitive_filter()
    email = case_insensitive_filter()
    first_name = case_insensitive_filter()
    last_name = case_insensitive_filter()
    project = filters.BaseCSVFilter(
        field_name='memberships__project',
        method='filter_by_list',
        help_text='Filter users by their projects using a comma-separated list of project IDs.',
    )
    exclude_external = filters.NumberFilter(method='filter_by_exclude_external')

    def filter_by_exclude_external(self, queryset, name, value):
        return queryset.exclude(
            ~Q(
                memberships__project_id=value,
                memberships__role__permissions__codename=UserAllowedPermissionCodenames.VIEW_PROJECT,
            ),
            memberships__role__permissions__codename=UserAllowedPermissionCodenames.VIEW_PROJECT_RESTRICTION,
        )

    class Meta:
        model = UserModel
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser')
