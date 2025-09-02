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

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Q, QuerySet

from testy.core.choices import AccessRequestStatus
from testy.core.models import AccessRequest, Project
from testy.users.choices import RoleTypes, UserAllowedPermissionCodenames
from testy.users.models import Membership, Role, User

UserModel = get_user_model()


class ProjectAssignable(Protocol):
    project: Project


class RoleSelector:
    exclude_list = ['External user']

    @classmethod
    def role_list(cls, exclude_roles: bool = False) -> QuerySet[Role]:
        qs = Role.objects.all().prefetch_related('permissions')
        if exclude_roles:
            return qs.exclude(name__in=cls.exclude_list)
        return qs

    @classmethod
    def role_list_for_user(cls, user: User, exclude_roles: bool = False) -> QuerySet[Role]:
        qs = cls.role_list(exclude_roles=exclude_roles)
        if not user.is_superuser:
            qs = Role.objects.filter(~Q(type=RoleTypes.SUPERUSER_ONLY))
        return qs.order_by('name')

    @classmethod
    def can_assign_role(cls, user: User, project_id: int, role_pks: list[int] | None = None) -> bool:
        if role_pks is not None:
            project_restriction_perm_exists = Permission.objects.filter(
                roles__pk__in=role_pks,
                codename=UserAllowedPermissionCodenames.VIEW_PROJECT_RESTRICTION,
            ).exists()
            if project_restriction_perm_exists:
                return False
        return Membership.objects.filter(
            user=user,
            project__pk=project_id,
            role__permissions__codename=UserAllowedPermissionCodenames.CHANGE_PROJECT,
        ).exists()

    @classmethod
    def action_allowed_for_instance(
        cls,
        user: User,
        project: ProjectAssignable | Project,
        permission_code: UserAllowedPermissionCodenames | str,
    ) -> bool:
        lookup = (
            Q(user__pk=user.pk)
            & Q(role__permissions__codename=permission_code)
            & Q(project=project)
        )
        return Membership.objects.filter(lookup).exists()

    @classmethod
    def create_action_allowed(cls, user: User, project: Project, model_name: str) -> bool:
        lookup = (
            Q(user__pk=user.pk)
            & Q(role__permissions__codename=f'add_{model_name}')
            & Q(project=project)
        )
        return Membership.objects.filter(lookup).exists()

    @classmethod
    def project_view_allowed(cls, user: User, project: Project) -> bool:
        lookup = (
            Q(user__pk=user.pk)
            & Q(role__permissions__codename=UserAllowedPermissionCodenames.VIEW_PROJECT)
            & Q(project=project)
        )
        return Membership.objects.filter(lookup).exists()

    @classmethod
    def restricted_project_access(cls, user: User) -> bool:
        lookup = (
            Q(user__pk=user.pk)
            & Q(role__permissions__codename=UserAllowedPermissionCodenames.VIEW_PROJECT_RESTRICTION)
        )
        return Membership.objects.filter(lookup).exists()

    @classmethod
    def admin_user_role(cls) -> Role | None:
        return Role.objects.filter(name=settings.ADMIN_ROLE_NAME).first()

    @classmethod
    def users_to_change_project(cls, project: Project) -> QuerySet[User]:
        return UserModel.objects.filter(
            memberships__project=project,
            memberships__role__permissions__codename=UserAllowedPermissionCodenames.CHANGE_PROJECT,
        )

    @classmethod
    def access_request_pending_list(cls, project: Project, user: User) -> QuerySet[AccessRequest]:
        return AccessRequest.objects.filter(project=project, user=user, status=AccessRequestStatus.PENDING)
