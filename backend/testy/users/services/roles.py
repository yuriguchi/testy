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
from typing import Any

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from testy.core.choices import AccessRequestStatus
from testy.core.models import AccessRequest, Project
from testy.root.tasks import project_access_email
from testy.users.models import Membership, Role, User
from testy.users.selectors.roles import RoleSelector

_PROJECT = 'project'
_USER = 'user'


class RoleService:
    non_side_effect_fields = [
        'name',
        'type',
    ]

    @classmethod
    @transaction.atomic
    def role_create(cls, data: dict[str, Any]) -> Role:
        role = Role.model_create(
            fields=cls.non_side_effect_fields,
            data=data,
        )
        role.permissions.set(data.get('permissions', []))
        return role

    @classmethod
    @transaction.atomic
    def role_update(cls, role: Role, data: dict[str, Any]) -> Role:
        role, _ = role.model_update(
            fields=cls.non_side_effect_fields,
            data=data,
        )
        role.permissions.set(data.get('permissions', []))
        return role

    @classmethod
    @transaction.atomic
    def roles_assign(cls, payload: dict[str, Any]) -> list[Membership]:
        memberships = []
        project = payload.get(_PROJECT)
        user = payload.get(_USER)
        source_qs = Membership.objects.filter(
            project=project,
            user=user,
        )
        access_requests = RoleSelector.access_request_pending_list(
            project=project,
            user=user,
        )
        access_requests.update(status=AccessRequestStatus.RESOLVED)
        for role in payload.get('roles', []):
            membership, _ = Membership.objects.get_or_create(
                project=project,
                user=user,
                role=role,
            )
            memberships.append(membership)
        ids_for_deletion = source_qs.difference(
            Membership.objects.filter(
                pk__in=[membership.pk for membership in memberships],
            ),
        ).values_list('id', flat=True)
        Membership.objects.filter(pk__in=ids_for_deletion).hard_delete()
        return memberships

    @classmethod
    @transaction.atomic
    def roles_unassign(cls, payload: dict[str, Any], requested_user: User) -> None:
        if payload.get(_USER) == requested_user:
            raise ValidationError('User cannot unassign role from itself.')
        project = payload.get(_PROJECT)
        project_lookup = Q(project=project) if project else Q(project__isnull=True)
        Membership.objects.filter(
            project_lookup,
            user=payload.get(_USER),
        ).hard_delete()

    @classmethod
    def access_request_create(cls, project: Project, user: User, reason: str) -> AccessRequest:
        non_side_effect_fields = [_PROJECT, 'reason', 'status', _USER]
        access_request = AccessRequest.model_create(
            fields=non_side_effect_fields,
            data={
                _PROJECT: project,
                'reason': reason,
                _USER: user,
            },
        )
        subject = f'Project "{project.name}" access request from "{user.username}"'
        message = f'Request reason: {reason}' if reason else ''
        recipients = list(RoleSelector.users_to_change_project(project).values_list('email', flat=True))
        project_access_email.delay(subject, message, recipients)
        return access_request
