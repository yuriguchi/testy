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

import pgtrigger
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from simple_history.models import HistoricalRecords

from testy.comments.models import Comment
from testy.core.models import Attachment, LabeledItem, LabelIds, Project
from testy.fields import IntegerEstimateField
from testy.root.ltree.indexes import get_indexes
from testy.root.ltree.managers import LtreeManager
from testy.root.ltree.triggers import get_triggers
from testy.root.models import BaseModel, LtreeBaseModel
from testy.triggers import get_statistic_triggers


class TestSuite(LtreeBaseModel):
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_test_suites',
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    description = models.TextField('description', default='', blank=True)
    comments = GenericRelation(Comment)
    attributes = models.JSONField(default=dict, blank=True)
    objects: LtreeManager

    class Meta:
        default_related_name = 'test_suites'
        triggers = get_triggers('suite') + get_statistic_triggers(
            'suites_count',
            pgtrigger.Q(new__is_deleted=True, old__is_deleted=False),
            pgtrigger.Q(new__is_deleted=False, old__is_deleted=True),
        )
        indexes = get_indexes('suite')

    def __str__(self):
        return self.name

    def model_clone(
        self,
        related_managers: list[str] = None,
        attrs_to_change: dict[str, Any] = None,
        attachment_references_fields: list[str] = None,
        common_attrs_to_change: dict[str, Any] = None,
    ):
        if related_managers is None:
            related_managers = ['child_test_suites', 'test_cases']
        return super().model_clone(
            related_managers,
            attrs_to_change,
            attachment_references_fields,
            common_attrs_to_change,
        )


class TestCase(BaseModel):
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, related_name='test_cases')
    setup = models.TextField(blank=True)
    scenario = models.TextField(blank=True)
    expected = models.TextField(blank=True)
    teardown = models.TextField(blank=True)
    estimate = IntegerEstimateField(null=True, blank=True)
    attachments = GenericRelation(Attachment)
    history = HistoricalRecords()
    description = models.TextField('description', default='', blank=True)
    is_steps = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    attributes = models.JSONField(default=dict, blank=True)

    label = GenericRelation(LabelIds)
    labeled_items = GenericRelation(LabeledItem)
    comments = GenericRelation(Comment)

    class Meta:
        default_related_name = 'test_cases'
        triggers = get_statistic_triggers('cases_count')

    def __str__(self):
        return self.name

    def model_clone(
        self,
        related_managers: list[str] = None,
        attrs_to_change: dict[str, Any] = None,
        attachment_references_fields: list[str] = None,
        common_attrs_to_change: dict[str, Any] = None,
    ):
        if related_managers is None:
            related_managers = ['steps', 'attachments', 'labeled_items']
        if attachment_references_fields is None:
            attachment_references_fields = ['setup', 'scenario', 'expected', 'teardown', 'description']
        return super().model_clone(
            related_managers,
            attrs_to_change,
            attachment_references_fields,
            common_attrs_to_change,
        )


class TestCaseStep(BaseModel):
    name = models.CharField(max_length=settings.CHAR_FIELD_MAX_LEN)
    scenario = models.TextField()
    expected = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, null=True, blank=True, related_name='steps')
    test_case_history_id = models.IntegerField(null=True, blank=True)
    history = HistoricalRecords()
    attachments = GenericRelation(Attachment)
    sort_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ('sort_order', 'id')

    def model_clone(
        self,
        related_managers: list[str] = None,
        attrs_to_change: dict[str, Any] = None,
        attachment_references_fields: list[str] = None,
        common_attrs_to_change: dict[str, Any] = None,
    ):
        if related_managers is None:
            related_managers = ['attachments']
        if attachment_references_fields is None:
            attachment_references_fields = ['scenario', 'expected']
        return super().model_clone(
            related_managers,
            attrs_to_change,
            attachment_references_fields,
            common_attrs_to_change,
        )
