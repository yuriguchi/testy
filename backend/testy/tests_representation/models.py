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
from typing import Any, Iterable

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import BTreeIndex
from django.core.validators import MinValueValidator
from django.db import models, transaction
from simple_history.models import HistoricalRecords

from testy.comments.models import Comment
from testy.core.constraints import unique_soft_delete_constraint
from testy.core.models import Attachment, Project
from testy.root.ltree.indexes import get_indexes
from testy.root.ltree.managers import LtreeManager
from testy.root.ltree.triggers import get_triggers
from testy.root.mixins import TestyArchiveMixin
from testy.root.models import BaseModel, LtreeBaseModel
from testy.tests_description.models import TestCase, TestCaseStep
from testy.tests_representation.choices import ResultStatusType
from testy.triggers import get_statistic_triggers
from testy.users.models import User

UserModel = get_user_model()


class Parameter(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    data = models.TextField()
    group_name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)

    class Meta:
        default_related_name = 'parameters'
        constraints = [unique_soft_delete_constraint(['group_name', 'data', 'project'], 'parameter')]

    def __str__(self):
        return f'{self.group_name}: {self.data}'


class TestPlan(LtreeBaseModel, TestyArchiveMixin):
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_test_plans',
    )
    parameters = models.ManyToManyField(Parameter, blank=True, related_name='test_plans')
    started_at = models.DateTimeField()
    due_date = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    description = models.TextField('description', default='', blank=True)
    comments = GenericRelation(Comment)
    attributes = models.JSONField(default=dict, blank=True)
    attachments = GenericRelation(Attachment)
    objects: LtreeManager

    class Meta:
        default_related_name = 'test_plans'
        triggers = get_triggers('plan') + get_statistic_triggers('plans_count')
        indexes = get_indexes('plan')


class ResultStatus(BaseModel):
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    color = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN, default='#000000')
    type = models.IntegerField(choices=ResultStatusType.choices, default=ResultStatusType.CUSTOM)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Result status'
        verbose_name_plural = 'Result statuses'


class Test(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE)
    assignee = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    history = HistoricalRecords()
    comments = GenericRelation(Comment)

    last_status = models.ForeignKey(ResultStatus, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        default_related_name = 'tests'
        triggers = get_statistic_triggers('tests_count')


class TestResult(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.ForeignKey(to=ResultStatus, on_delete=models.SET_NULL, null=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=True)
    is_archive = models.BooleanField(default=False)
    test_case_version = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(settings.MIN_VALUE_POSITIVE_INTEGER)],
    )
    execution_time = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(settings.MIN_VALUE_POSITIVE_INTEGER)],
    )
    attachments = GenericRelation(Attachment)
    attributes = models.JSONField(default=dict, blank=True)
    history = HistoricalRecords()
    comments = GenericRelation(Comment)

    class Meta:
        default_related_name = 'test_results'
        indexes = [
            BTreeIndex(
                'project_id',
                'is_deleted',
                'is_archive',
                'created_at',
                name='results_histogram_idx',
            ),
        ]

    def model_clone(
        self,
        related_managers: list[str] = None,
        attrs_to_change: dict[str, Any] = None,
        attachment_references_fields: list[str] = None,
        common_attrs_to_change: dict[str, Any] = None,
    ):
        if related_managers is None:
            related_managers = ['attachments', 'steps_results']
        if attachment_references_fields is None:
            attachment_references_fields = ['comment']
        return super().model_clone(
            related_managers,
            attrs_to_change,
            attachment_references_fields,
            common_attrs_to_change,
        )

    @transaction.atomic
    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        is_inserted = self.pk is None
        super().save(force_insert, force_update, using, update_fields)
        latest_result_pk = None
        if latest_result := self.test.results.order_by('-created_at').first():
            latest_result_pk = latest_result.pk
        last_result_updated = update_fields and 'status' in update_fields and self.pk == latest_result_pk
        if is_inserted or last_result_updated:
            self.test.last_status = self.status
            self.test.save()


class TestStepResult(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='steps_results')
    step = models.ForeignKey(TestCaseStep, on_delete=models.CASCADE, related_name='result')
    status = models.ForeignKey(to=ResultStatus, on_delete=models.SET_NULL, null=True)
    history = HistoricalRecords()
