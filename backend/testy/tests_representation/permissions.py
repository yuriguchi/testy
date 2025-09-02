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
from typing import Protocol

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request

from testy.core.models import Project
from testy.core.permissions import MISSING_PROJECT_CODE, BaseProjectPermission, getter_to_method
from testy.tests_representation.choices import ResultStatusType
from testy.tests_representation.selectors.testplan import TestPlanSelector
from testy.users.selectors.roles import RoleSelector


class ProjectAssignable(Protocol):
    project: Project


class TestResultPermission(BaseProjectPermission):

    @classmethod
    def _get_project_from_request(
        cls,
        request: Request,
        instance: ProjectAssignable | None = None,
    ) -> Project:
        if instance is not None:
            return cls._get_project_from_instance(instance)
        test_pk = getter_to_method[request.method](request).get('test', None)
        if not test_pk:
            raise ValidationError('Could not get project id from request', code=MISSING_PROJECT_CODE)
        project = Project.objects.filter(tests__pk=test_pk).first()
        if project is None:
            raise ValidationError('Could not get project to validate permissions', code=MISSING_PROJECT_CODE)
        return project


class TestPlanPermission(BaseProjectPermission):
    def has_permission(self, request, view):  # noqa: WPS212
        if any([request.method in self.safe_non_read_methods, request.user.is_superuser, view.detail]):
            return True
        if view.action == 'copy_plans':
            return self._validate_plans_copy_permissions(request, view)
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

    def _validate_plans_copy_permissions(self, request, view):
        plan_ids = [plan.get('plan') for plan in request.data.get('plans', [])]
        if dst_plan_id := request.data.get('dst_plan'):
            plan_ids.append(dst_plan_id)
        plans = TestPlanSelector.plans_by_ids(plan_ids)
        return all(self.has_object_permission(request, view, plan) for plan in plans)


class ResultStatusPermission(BaseProjectPermission):

    def has_permission(self, request, view):
        conditions = [
            view.action == 'create' and request.data.get('type') == ResultStatusType.SYSTEM,
            view.action == 'delete_permanently',
        ]
        if any(conditions):
            return request.user.is_superuser
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, instance):
        if instance.type == ResultStatusType.SYSTEM:
            return request.user.is_superuser or request.method in SAFE_METHODS
        return super().has_object_permission(request, view, instance)
