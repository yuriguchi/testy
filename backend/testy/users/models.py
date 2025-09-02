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
from functools import partial

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from testy.root.models import BaseModel, ServiceModelMixin
from testy.users.choices import RoleTypes
from testy.utilities.sql import unique_soft_delete_constraint
from testy.utils import get_media_file_path
from testy.validators import CaseInsensitiveUsernameValidator


class Group(Group, ServiceModelMixin):  # noqa: WPS440
    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        proxy = True


class User(AbstractUser, ServiceModelMixin):
    config = models.JSONField(default=dict, blank=True)
    username = models.CharField(
        _('username'),
        max_length=settings.FILEPATH_MAX_LEN,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[AbstractUser.username_validator, CaseInsensitiveUsernameValidator()],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    avatar = models.ImageField(
        null=True,
        blank=True,
        max_length=settings.FILEPATH_MAX_LEN,
        upload_to=partial(get_media_file_path, media_name='avatars'),
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Role(BaseModel):
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    permissions = models.ManyToManyField(Permission, blank=True)
    type = models.IntegerField(choices=RoleTypes.choices, default=RoleTypes.CUSTOM)
    history = HistoricalRecords(related_name='history_roles')

    class Meta:
        default_related_name = 'roles'
        constraints = [
            unique_soft_delete_constraint('name', 'role'),
        ]

    def __str__(self):
        return self.name


class Membership(BaseModel):
    project = models.ForeignKey('core.Project', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'memberships'
