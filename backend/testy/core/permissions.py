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
from operator import attrgetter
from typing import Protocol

from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request

from testy.core.models import Attachment, Project
from testy.core.selectors.projects import ProjectSelector
from testy.users.choices import UserAllowedPermissionCodenames
from testy.users.selectors.roles import RoleSelector


class ProjectAssignable(Protocol):
    project: Project


getter_to_method = {
    'GET': attrgetter('query_params'),
    'POST': attrgetter('data'),
}

MISSING_PROJECT_CODE = 'missing_project'
_PROJECT = 'project'


class BaseProjectPermission(BasePermission):
    safe_non_read_methods = {'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):  # noqa: WPS212
        if any([request.method in self.safe_non_read_methods, request.user.is_superuser, view.detail]):
            return True
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

    def has_object_permission(self, request, view, instance):  # noqa: WPS212
        if request.user.is_superuser or request.method in self.safe_non_read_methods:
            return True
        project = self._get_project_from_request(request, instance)
        if not project.is_private and not RoleSelector.restricted_project_access(request.user):
            return True
        if request.method in SAFE_METHODS:
            return RoleSelector.project_view_allowed(
                user=request.user,
                project=project,
            )
        if request.method in {'PUT', 'PATCH', 'POST'}:
            return RoleSelector.action_allowed_for_instance(
                user=request.user,
                project=project,
                permission_code=f'change_{type(instance)._meta.model_name}',  # noqa: WPS237
            )
        if request.method == 'DELETE':
            return RoleSelector.action_allowed_for_instance(
                request.user,
                project=project,
                permission_code=f'delete_{type(instance)._meta.model_name}',  # noqa: WPS237
            )
        return False

    @classmethod
    def _get_project_from_request(
        cls,
        request: Request,
        instance: ProjectAssignable | None = None,
    ) -> Project:
        if instance is not None:
            return cls._get_project_from_instance(instance)
        project_pk = getter_to_method[request.method](request).get(_PROJECT, None)
        if not project_pk:
            raise ValidationError('Could not get project id from request', code=MISSING_PROJECT_CODE)
        project = ProjectSelector.project_by_id(project_pk)
        if project is None:
            raise ValidationError('Could not get project to validate permissions', code=MISSING_PROJECT_CODE)
        return project

    @classmethod
    def _get_project_from_instance(cls, instance) -> Project:
        if isinstance(instance, Project):
            return instance
        if project := getattr(instance, _PROJECT, None):
            return project
        raise ValidationError('Could not get project id from instance', code=MISSING_PROJECT_CODE)


class ProjectPermission(BaseProjectPermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class ProjectIsPrivatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_private = request.data.get('is_private')
        if view.action in {'update', 'partial_update'} and is_private is not None:
            if obj.is_private != is_private:
                return request.user.is_superuser or RoleSelector.action_allowed_for_instance(
                    request.user,
                    obj,
                    UserAllowedPermissionCodenames.CHANGE_PROJECT,
                )
        return True


class AttachmentReadPermission(BaseProjectPermission):
    def has_permission(self, request, view):  # noqa: WPS212
        if any([request.method in self.safe_non_read_methods, request.user.is_superuser]):
            return True
        attachment = get_object_or_404(Attachment, **view.kwargs)
        if not attachment.project.is_private and not RoleSelector.restricted_project_access(request.user):
            return True
        return RoleSelector.project_view_allowed(
            user=request.user,
            project=attachment.project,
        )


class AttachmentPermission(BaseProjectPermission):
    def has_permission(self, request, view):  # noqa: WPS212
        if any([request.method in self.safe_non_read_methods, request.user.is_superuser, view.detail]):
            return True
        project = self._get_project_from_request(request)
        if not project.is_private and not RoleSelector.restricted_project_access(request.user):
            return True
        return RoleSelector.project_view_allowed(
            user=request.user,
            project=project,
        )

    def has_object_permission(self, request, view, instance):  # noqa: WPS212
        if request.user.is_superuser or request.method in self.safe_non_read_methods:
            return True
        project = self._get_project_from_request(request, instance)
        if not project.is_private and not RoleSelector.restricted_project_access(request.user):
            return True
        return RoleSelector.project_view_allowed(
            user=request.user,
            project=project,
        )
