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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from testy.users.models import Group as Group_  # noqa: WPS120
from testy.users.models import Membership, Role, User

admin.site.unregister(Group)


@admin.register(Group_)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_count')
    ordering = ('name',)
    search_fields = ('name',)

    @classmethod
    def user_count(cls, obj):
        return obj.user_set.count()


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'avatar',
    ]
    fieldsets = (
        (None, {'fields': ('username', 'password', 'first_name', 'last_name', 'email')}),
        ('Groups', {'fields': ('groups',)}),
        (
            'Status', {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'avatar'),
            },
        ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups',)
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups__name')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    fields = ('name', 'permissions', 'type')
    search_fields = ('name', 'type', 'permissions')
    autocomplete_fields = ('permissions',)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role')
    search_fields = ('project', 'user', 'role')
    autocomplete_fields = ('project', 'user', 'role')
