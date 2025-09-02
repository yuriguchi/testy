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
from rest_framework.permissions import SAFE_METHODS
from users.choices import UserAllowedPermissionCodenames

from testy.core.permissions import BaseProjectPermission
from testy.tests_description.api.v2.serializers import TestCaseCopySerializer, TestSuiteCopySerializer
from testy.tests_description.selectors.cases import TestCaseSelector
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.users.selectors.roles import RoleSelector

_PROJECT = 'project'


class TestCaseCopyPermission(BaseProjectPermission):
    def has_permission(self, request, view):  # noqa: WPS212
        if any([request.method in self.safe_non_read_methods, request.user.is_superuser, view.detail]):
            return True
        if view.action == 'copy_cases':
            return self._validate_cases_copy_permissions(request, view)
        project = self._get_project_from_request(request)
        if not project.is_private and not RoleSelector.restricted_project_access(request.user):
            return True
        if view.action == 'create':
            return RoleSelector.create_action_allowed(
                user=request.user,
                project=project,
                model_name=view.queryset.model._meta.model_name,
            )
        if request.method in SAFE_METHODS and not view.detail:
            return RoleSelector.project_view_allowed(
                user=request.user,
                project=project,
            )
        return True

    def _validate_cases_copy_permissions(self, request, view):
        serializer = TestCaseCopySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_allowed_list: list[bool] = []
        for case in serializer.validated_data.get('cases'):
            is_allowed_list.append(
                self.has_object_permission(request, view, TestCaseSelector.case_by_id(case.get('id'))),
            )
        if dst_suite_id := serializer.validated_data.get('dst_suite_id'):
            is_allowed_list.append(
                self.has_object_permission(request, view, dst_suite_id),
            )
        return all(is_allowed_list)


class TestSuiteCopyPermission(BaseProjectPermission):
    def has_permission(self, request, view):  # noqa: WPS212
        if any([request.method in self.safe_non_read_methods, request.user.is_superuser, view.detail]):
            return True
        if view.action == 'copy_suites':
            return self._validate_suites_copy_permissions(request, view)
        project = self._get_project_from_request(request)
        if not project.is_private and not RoleSelector.restricted_project_access(request.user):
            return True
        if view.action == 'create':
            return RoleSelector.create_action_allowed(
                user=request.user,
                project=project,
                model_name=view.queryset.model._meta.model_name,
            )
        if request.method in SAFE_METHODS and not view.detail:
            return RoleSelector.project_view_allowed(
                user=request.user,
                project=project,
            )
        return True

    def _validate_suites_copy_permissions(self, request, view):
        serializer = TestSuiteCopySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_allowed_list: list[bool] = []
        for suite in serializer.validated_data.get('suites'):
            is_allowed_list.append(
                self.has_object_permission(request, view, TestSuiteSelector().suite_by_id(suite.get('id'))),
            )
        if suite := serializer.validated_data.get('dst_suite_id'):
            is_allowed_list.append(self.has_object_permission(request, view, suite))
        if (project := serializer.validated_data.get('dst_project_id')) and project.is_private:
            is_allowed_list.append(
                RoleSelector.action_allowed_for_instance(
                    user=request.user,
                    project=project,
                    permission_code=UserAllowedPermissionCodenames.VIEW_PROJECT,
                ),
            )
        return all(is_allowed_list)
