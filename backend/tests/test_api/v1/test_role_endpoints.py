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
from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission

from tests import constants
from tests.commons import RequestType, model_to_dict_via_serializer
from testy.users.api.v1.serializers import RoleSerializer
from testy.users.choices import UserAllowedPermissionCodenames
from testy.users.models import Membership, Role
from testy.users.selectors.permissions import PermissionSelector


@pytest.mark.django_db
class TestRoleEndpoints:
    view_name_list = 'api:v1:role-list'
    view_name_detail = 'api:v1:role-detail'
    view_name_assign = 'api:v1:role-assign'
    view_name_unassign = 'api:v1:role-unassign'

    def test_list(self, api_client, authorized_superuser, role_factory):
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            role_factory()
        expected_instances = model_to_dict_via_serializer(
            Role.objects.order_by('name'),
            RoleSerializer,
            many=True,
        )
        response = api_client.send_request(self.view_name_list)
        assert response.json()['results'] == expected_instances

    def test_retrieve(self, api_client, authorized_superuser, role):
        expected_dict = model_to_dict_via_serializer(role, RoleSerializer)
        response = api_client.send_request(self.view_name_detail, reverse_kwargs={'pk': role.pk})
        actual_dict = response.json()
        assert actual_dict == expected_dict

    def test_creation(self, api_client, authorized_superuser):
        role_dict = {
            'name': constants.ROLE_NAME,
            'permissions': [Permission.objects.filter(codename__in=UserAllowedPermissionCodenames.values).first().pk],
        }
        response = api_client.send_request(self.view_name_list, role_dict, HTTPStatus.CREATED, RequestType.POST)
        assert model_to_dict_via_serializer(Role.objects.first(), RoleSerializer) == response.json()

    @pytest.mark.parametrize('request_type', [RequestType.PUT, RequestType.PATCH])
    def test_update(self, api_client, authorized_superuser, role, request_type):
        new_name = 'new_name'
        api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': role.pk},
            request_type=request_type,
            data={
                'name': new_name,
                'permissions': PermissionSelector.permission_by_codenames(
                    UserAllowedPermissionCodenames.values,
                ).values_list('id', flat=True),
            },
        )
        role.refresh_from_db()
        assert role.name == new_name

    def test_delete(self, api_client, authorized_superuser, role):
        assert Role.objects.count() == 1, 'Role was not created'
        api_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': role.pk},
        )
        assert not Role.objects.count(), f'Role with id "{role.id}" was not deleted.'

    def test_role_permissions(self, authorized_client, role):
        authorized_client.send_request(self.view_name_list)
        authorized_client.send_request(
            self.view_name_list,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.FORBIDDEN,
        )
        authorized_client.send_request(self.view_name_detail, reverse_kwargs={'pk': role.pk})
        forbidden_request_types = [RequestType.PUT, RequestType.PATCH, RequestType.DELETE]
        for request_type in forbidden_request_types:
            authorized_client.send_request(
                self.view_name_detail,
                request_type=request_type,
                reverse_kwargs={'pk': role.pk},
                expected_status=HTTPStatus.FORBIDDEN,
            )

    def test_role_assignation(self, authorized_superuser_client, user, project_factory, role):
        project = project_factory()
        authorized_superuser_client.send_request(
            self.view_name_assign,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.OK,
            data={
                'user': user.pk,
                'project': project.pk,
                'roles': [role.pk],
            },
        )
        assert user.project_set.first() == project

    def test_roles_update(
        self,
        authorized_superuser_client,
        user,
        role_factory,
        membership_factory,
        project,
    ):
        role = role_factory()
        src_membership = membership_factory(user=user, project=project)

        authorized_superuser_client.send_request(
            self.view_name_assign,
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
            data={
                'user': user.pk,
                'project': project.pk,
                'roles': [role.pk, src_membership.role.pk],
            },
        )
        assert user.memberships.count() == 2
        authorized_superuser_client.send_request(
            self.view_name_assign,
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
            data={
                'user': user.pk,
                'project': project.pk,
                'roles': [src_membership.role.pk],
            },
        )
        assert user.memberships.count() == 1
        assert user.memberships.first() == src_membership

    def test_roles_unassign(self, authorized_superuser_client, user, membership_factory, project):
        for _ in range(3):
            membership_factory(user=user, project=project)
        authorized_superuser_client.send_request(
            self.view_name_unassign,
            data={
                'project': project.pk,
                'user': user.pk,
            },
            request_type=RequestType.POST,
        )
        assert not Membership.objects.all()
