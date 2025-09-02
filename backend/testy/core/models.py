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
from copy import deepcopy
from functools import partial
from pathlib import Path
from typing import Any

import pgtrigger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from simple_history.models import HistoricalRecords

from testy.core.choices import AccessRequestStatus, ActionCode, CustomFieldType, LabelTypes, SystemMessageLevel
from testy.core.constraints import unique_soft_delete_constraint
from testy.raw_sql import DELETE_LABELED_ITEM_TRIGGER, INSERT_LABELED_ITEM_TRIGGER
from testy.root.models import BaseModel, DeletedManager, SoftDeleteManager, SoftDeleteMixin
from testy.users.models import Membership, User
from testy.utils import get_media_file_path
from testy.validators import ExtensionValidator, ProjectValidator

UserModel = get_user_model()

_NAME = 'name'
_PROJECT = 'project'
_CONTENT_TYPE = 'content_type'
_OBJECT_ID = 'object_id'


class Project(BaseModel):
    name = models.CharField(_NAME, max_length=settings.CHAR_FIELD_MAX_LEN)
    description = models.TextField('description', blank=True)
    is_archive = models.BooleanField(default=False)
    icon = models.ImageField(
        null=True,
        blank=True,
        max_length=settings.FILEPATH_MAX_LEN,
        upload_to=partial(get_media_file_path, media_name='icons'),
    )
    is_private = models.BooleanField(default=False)
    members = models.ManyToManyField(
        User,
        through=Membership,
        through_fields=(_PROJECT, 'user'),
    )
    settings = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = (_NAME,)
        verbose_name = gettext_lazy(_PROJECT)
        verbose_name_plural = gettext_lazy('projects')
        triggers = [
            pgtrigger.Trigger(
                name='insert_statistics_on_project_create',
                operation=pgtrigger.Insert,
                when=pgtrigger.Before,
                func="""
                INSERT INTO core_projectstatistics
                (project_id, cases_count, suites_count, tests_count, plans_count, is_deleted)
                VALUES (NEW.id, 0, 0, 0, 0, FALSE);
                RETURN NEW;
                """,
            ),
            pgtrigger.Trigger(
                name='delete_statistics_on_project_delete',
                operation=pgtrigger.Delete,
                when=pgtrigger.Before,
                func='DELETE FROM core_projectstatistics WHERE project_id = OLD.id; RETURN OLD;',
            ),
        ]

    class ModelHierarchyWeightMeta:  # noqa: WPS431
        weight = 10

    def __str__(self) -> str:
        return self.name


class ProjectStatistics(SoftDeleteMixin):
    cases_count = models.IntegerField(default=0)
    suites_count = models.IntegerField(default=0)
    tests_count = models.IntegerField(default=0)
    plans_count = models.IntegerField(default=0)
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    objects = SoftDeleteManager()
    deleted_objects = DeletedManager()


class Attachment(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # Name of file without extension
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    # Full filename
    filename = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    file_extension = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    # Size of file in bytes
    size = models.PositiveBigIntegerField()
    # Parent object table, example: core_project
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        validators=[ProjectValidator()],
        null=True,
        blank=True,
    )
    # Id of object from table of content_type
    object_id = models.PositiveIntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    # Instance of parent object
    content_object = GenericForeignKey(_CONTENT_TYPE, _OBJECT_ID)
    user = models.ForeignKey(UserModel, null=True, on_delete=models.SET_NULL)
    file = models.FileField(
        max_length=settings.FILEPATH_MAX_LEN,
        upload_to=partial(get_media_file_path, media_name='attachments'),
        validators=[ExtensionValidator()],
    )
    content_object_history_ids = ArrayField(models.IntegerField(), default=list, blank=True)

    def __str__(self):
        if self.file:
            return str(self.file.url)
        return ''

    def model_clone(
        self,
        related_managers: list[str] = None,
        attrs_to_change: dict[str, Any] = None,
        attachment_references_fields: list[str] = None,
        common_attrs_to_change: dict[str, Any] = None,
    ):
        self_copy = deepcopy(self)
        attrs = {'pk': None, 'id': None}
        if common_attrs_to_change:
            attrs.update(common_attrs_to_change)
        for attr_name, attr_value in attrs.items():
            setattr(self_copy, attr_name, attr_value)
        new_file = None
        if self.file and Path(self.file.path).exists():
            new_file = ContentFile(self.file.read())
        self_copy._state.adding = True
        if new_file:
            self_copy.file.save(self.filename, new_file, save=False)
        self_copy.save()
        return self_copy


class Label(BaseModel):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.IntegerField(choices=LabelTypes.choices, default=LabelTypes.CUSTOM)

    class Meta:
        verbose_name = _('Label')
        verbose_name_plural = _('Labels')
        constraints = [unique_soft_delete_constraint([_PROJECT, _NAME], 'label')]

    def clean(self):
        if label := Label.objects.filter(name__iexact=self.name, project=self.project).first():
            raise ValidationError(
                {
                    _NAME: (
                        f'Label name "{self.name}" clashes with already existing label name '
                        f'"{label.name}" in project {self.project}.'  # noqa: WPS326
                    ),
                },
            )


class LabelIds(SoftDeleteMixin):
    ids = ArrayField(models.BigIntegerField(), blank=True, default=list)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(_CONTENT_TYPE, _OBJECT_ID)
    objects = SoftDeleteManager()
    deleted_objects = DeletedManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=[_CONTENT_TYPE, _OBJECT_ID], name='label_ids_unique_constraint'),
        ]


class LabeledItem(BaseModel):
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        validators=[ProjectValidator()],
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(_CONTENT_TYPE, _OBJECT_ID)
    content_object_history_id = models.IntegerField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        triggers = [
            pgtrigger.Trigger(
                name='labeleditem_insert_trigger',
                when=pgtrigger.Before,
                operation=pgtrigger.Insert,
                func=INSERT_LABELED_ITEM_TRIGGER,
            ),
            pgtrigger.Trigger(
                name='labeleditem_soft_delete_trigger',
                when=pgtrigger.After,
                operation=pgtrigger.Update,
                condition=pgtrigger.Q(old__is_deleted=False, new__is_deleted=True),
                func=DELETE_LABELED_ITEM_TRIGGER,
            ),
        ]


class SystemMessage(BaseModel):
    content = models.TextField(blank=False)
    level = models.IntegerField(choices=SystemMessageLevel.choices, blank=False)
    is_active = models.BooleanField(default=False)
    is_closing = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('System message')
        verbose_name_plural = _('System messages')


class CustomAttribute(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    type = models.IntegerField(choices=CustomFieldType.choices, blank=False)
    applied_to = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = (_NAME,)
        verbose_name = _('Custom attribute')
        verbose_name_plural = _('Custom attributes')
        constraints = [unique_soft_delete_constraint(['project', _NAME], 'custom_attribute')]

    def clean(self):
        if custom_attribute := CustomAttribute.objects.filter(name__iexact=self.name, project=self.project).first():
            if custom_attribute.id != self.id:
                raise ValidationError(
                    {
                        _NAME: (
                            f'Custom attribute name "{self.name}" clashes with already existing custom attribute name '
                            f'"{custom_attribute.name}" in project {self.project}.'  # noqa: WPS326
                        ),
                    },
                )


class AccessRequest(BaseModel):
    project = models.ForeignKey('core.Project', on_delete=models.CASCADE)
    reason = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=AccessRequestStatus.choices, default=AccessRequestStatus.PENDING)

    class Meta:
        default_related_name = 'requests'


class NotificationSetting(BaseModel):
    action_code = models.IntegerField(choices=ActionCode.choices, primary_key=True)
    verbose_name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN, blank=True, null=True)
    placeholder_text = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN, blank=True, null=True)
    placeholder_link = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN, blank=True, null=True)
    message = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    subscribers = models.ManyToManyField(User)

    class Meta:
        default_related_name = 'notification_settings'
