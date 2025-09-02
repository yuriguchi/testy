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

from django.contrib.auth import get_user_model, login
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import authenticate
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from testy.paginations import StandardSetPagination
from testy.swagger.v1.users import user_delete_avatar_schema, user_post_avatar_schema
from testy.users.api.v2.serializers import (
    GroupSerializer,
    MembershipSerializer,
    PasswordUpdateSerializer,
    PermissionSerializer,
    RoleAssignSerializer,
    RoleSerializer,
    RoleUnassignSerializer,
    UserAvatarSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from testy.users.filters import UserFilter
from testy.users.permissions import RolePermission, UserPermission
from testy.users.selectors.groups import GroupSelector
from testy.users.selectors.permissions import PermissionSelector
from testy.users.selectors.roles import RoleSelector
from testy.users.selectors.users import UserSelector
from testy.users.services.groups import GroupService
from testy.users.services.roles import RoleService
from testy.users.services.users import UserService

UserModel = get_user_model()

_ERRORS = 'errors'
_POST = 'post'
_AVATAR = 'avatar'


class GroupViewSet(ModelViewSet):
    queryset = GroupSelector().group_list()
    serializer_class = GroupSerializer
    schema_tags = ['Groups']

    def perform_create(self, serializer: GroupSerializer):
        serializer.instance = GroupService().group_create(serializer.validated_data)

    def perform_update(self, serializer: UserSerializer):
        serializer.instance = GroupService().group_update(serializer.instance, serializer.validated_data)


class UserViewSet(ModelViewSet):
    queryset = UserSelector().user_list()
    serializer_class = UserSerializer
    pagination_class = StandardSetPagination
    permission_classes = [IsAuthenticated, UserPermission]
    schema_tags = ['Users']

    @property
    def filterset_class(self):
        if self.action == 'list':
            return UserFilter

    def get_serializer_class(self):
        match self.action:
            case 'create':
                return UserCreateSerializer
            case 'update' | 'partial_update':
                return UserUpdateSerializer
            case 'change_password':
                return PasswordUpdateSerializer
            case 'avatar':
                return UserAvatarSerializer
        return UserSerializer

    def get_queryset(self):
        return UserSelector().user_list(self.request.user)

    def perform_create(self, serializer: UserSerializer):
        serializer.instance = UserService().user_create(serializer.validated_data)

    def perform_update(self, serializer: UserUpdateSerializer):
        serializer.instance = UserService().user_update(serializer.instance, serializer.validated_data)

    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object():
            return Response({_ERRORS: ['User cannot delete itself']}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    @action(methods=['get', 'patch', 'put'], url_path='me', url_name='me', detail=False)
    def me(self, request):
        if request.method == 'GET':
            return Response(self.get_serializer(request.user).data)
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.instance = UserService().user_update(serializer.instance, serializer.validated_data)
        return Response(serializer.data)

    @swagger_auto_schema(responses={status.HTTP_200_OK: 'Password changed successfully'})
    @action(methods=[_POST], url_path='change-password', url_name='change-password', detail=False)
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get('password')
        UserService.update_password(request.user, password)
        user = authenticate(request, username=request.user.username, password=password)
        login(request, user)
        return Response('Password changed successfully')

    @action(methods=['get', 'patch'], url_path='me/config', url_name='config', detail=False)
    def config(self, request):
        if request.method == 'GET':
            return Response(request.user.config)
        if request.method == 'PATCH':
            return Response(UserService().config_update(request.user, request.data))
        return Response(request.user.config)

    @user_post_avatar_schema
    @user_delete_avatar_schema
    @action(methods=[_POST, 'delete'], url_path='me/avatar', url_name=_AVATAR, detail=False)
    def avatar(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            if _AVATAR not in serializer.validated_data:
                return Response(data={_ERRORS: ['No avatar was provided in request']}, status=HTTPStatus.BAD_REQUEST)
            try:
                serializer.instance = UserService().update_avatar(serializer.instance, serializer.validated_data)
            except OSError:
                return Response(data={_ERRORS: ['Invalid image was provided']}, status=HTTPStatus.BAD_REQUEST)
            return Response(data={'detail': 'Avatar was updated successfully'}, status=HTTPStatus.OK)
        elif request.method == 'DELETE':
            serializer.instance = UserService().update_avatar(serializer.instance, {_AVATAR: None})
            return Response(data={'detail': 'Avatar was deleted successfully'}, status=HTTPStatus.OK)
        return Response(status=HTTPStatus.METHOD_NOT_ALLOWED)


class RoleViewSet(ModelViewSet):
    permission_classes = [RolePermission]
    queryset = RoleSelector.role_list()
    serializer_class = RoleSerializer
    pagination_class = StandardSetPagination
    filter_backends = [DjangoFilterBackend]
    schema_tags = ['Roles']

    def get_serializer_class(self):
        match self.action:
            case 'unassign':
                return RoleUnassignSerializer
            case 'update_role' | 'assign':
                return RoleAssignSerializer
            case 'permissions':
                return PermissionSerializer
        return RoleSerializer

    def perform_create(self, serializer: RoleSerializer):
        serializer.instance = RoleService.role_create(serializer.validated_data)

    def get_queryset(self):
        return RoleSelector.role_list_for_user(self.request.user, exclude_roles=True)

    def perform_update(self, serializer: RoleSerializer):
        serializer.instance = RoleService.role_update(
            serializer.instance,
            serializer.validated_data,
        )

    @swagger_auto_schema(methods=[_POST, 'put'], responses={status.HTTP_200_OK: MembershipSerializer(many=True)})
    @action(methods=[_POST, 'put'], detail=False, url_path='assign', url_name='assign')
    def assign(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        memberships = RoleService.roles_assign(serializer.validated_data)
        return Response(MembershipSerializer(memberships, many=True).data)

    @swagger_auto_schema(responses={status.HTTP_200_OK: 'Role removed successfully'})
    @action(methods=[_POST], detail=False, url_path='unassign', url_name='unassign')
    def unassign(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        RoleService.roles_unassign(serializer.validated_data, request.user)
        return Response(data={'Role removed successfully'})

    @action(methods=['get'], detail=False, url_path='permissions', url_name='permissions')
    def permissions(self, request):
        permissions = PermissionSelector.permission_list()
        return Response(
            data=self.get_serializer(permissions, many=True).data,
        )
