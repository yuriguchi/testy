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
from django.contrib.auth.models import Permission
from rest_framework.fields import CharField, IntegerField, JSONField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedIdentityField, ModelSerializer, Serializer
from users.validators import PasswordValidator

from testy.core.api.v2.serializers import ProjectSerializer
from testy.users.models import Group, Membership, Role
from testy.users.selectors.permissions import PermissionSelector
from testy.users.selectors.roles import RoleSelector

UserModel = get_user_model()


class GroupSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v2:group-detail')

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions', 'url')


class UserSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v2:user-detail')
    avatar_link = SerializerMethodField(read_only=True)
    projects = ProjectSerializer(read_only=True, many=True)

    class Meta:
        model = UserModel
        fields = (
            'id', 'url', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active',
            'date_joined', 'groups', 'avatar', 'avatar_link', 'is_superuser', 'projects',
        )

        read_only_fields = ('date_joined',)
        extra_kwargs = {
            'avatar': {'write_only': True},
        }

    def get_avatar_link(self, instance):
        if not instance.avatar:
            return ''
        return self.context['request'].build_absolute_uri(
            reverse('avatar-path', kwargs={'pk': instance.id}),
        )


class UserCreateSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('password',)
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [PasswordValidator()]},
            'avatar': {'write_only': True},
        }


class PasswordUpdateSerializer(Serializer):
    password = CharField(write_only=True, validators=[PasswordValidator()])


class UserUpdateSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_superuser',
        )


class RoleFromMembershipSerializer(Serializer):
    id = IntegerField(source='role.id', read_only=True)
    name = CharField(source='role.name', read_only=True)
    type = IntegerField(source='role.type', read_only=True)
    permissions = SerializerMethodField()

    def get_permissions(self, instance):
        return PermissionSerializer(instance.role.permissions.all(), many=True).data


class UserRoleSerializer(UserSerializer):
    roles = RoleFromMembershipSerializer(source='memberships', many=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('roles',)


class UserAvatarSerializer(UserSerializer):
    crop = JSONField(allow_null=True)

    class Meta:
        model = UserModel
        fields = ('avatar', 'crop')


class RoleSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v2:role-detail')
    permissions = PrimaryKeyRelatedField(
        many=True,
        queryset=PermissionSelector.permission_list(),
        allow_empty=True,
        required=True,
    )

    class Meta:
        model = Role
        fields: tuple[str, ...] = ('id', 'name', 'permissions', 'type', 'url')


class RoleAssignSerializer(ModelSerializer):
    roles = PrimaryKeyRelatedField(
        many=True,
        queryset=RoleSelector.role_list(),
    )

    class Meta:
        model = Membership
        fields: tuple[str, ...] = ('project', 'user', 'roles')


class RoleUnassignSerializer(ModelSerializer):
    class Meta:
        model = Membership
        fields: tuple[str, ...] = ('project', 'user')


class MembershipSerializer(ModelSerializer):
    class Meta:
        model = Membership
        fields: tuple[str, ...] = ('project', 'user', 'role')
        extra_kwargs = {
            'project': {'required': True, 'allow_null': False},
            'user': {'required': True, 'allow_null': False},
            'role': {'required': True, 'allow_null': False},
        }


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields: tuple[str, ...] = ('id', 'name', 'codename')
