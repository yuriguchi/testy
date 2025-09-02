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
import re
from datetime import timedelta
from functools import partial
from itertools import chain
from typing import Any, Callable, Iterable

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.timezone import now
from rest_framework import serializers

from testy.core.models import Project
from testy.core.selectors.custom_attribute import CustomAttributeSelector
from testy.core.selectors.project_settings import ProjectSettings
from testy.core.validators import BaseCustomAttributeValuesValidator
from testy.tests_description.selectors.cases import TestCaseSelector
from testy.tests_representation.choices import ResultStatusType, TestStatuses
from testy.tests_representation.selectors.status import ResultStatusSelector
from testy.users.selectors.roles import RoleSelector
from testy.utilities.time import WorkTimeProcessor
from testy.validators import FieldsToComparator

_ID = 'id'
_TYPE = 'type'
_PROJECT = 'project'
_NAME = 'name'
_STATUS = 'status'


@deconstructible
class ResultStatusValidator:
    requires_context = True
    err_msg = 'Status name "{0}" clashes with already existing status name "{1}" in project {2}.'

    def __call__(self, data, serializer):
        instance = serializer.instance
        type_value = self._check_type(data, instance)
        self._check_color(data, (self._check_hex_color, self._check_rgb_color, self._check_rgba_color))
        project = data.get(_PROJECT, getattr(instance, _PROJECT, None))

        if type_value == ResultStatusType.SYSTEM and project:
            raise ValidationError('System status cannot have project')
        if type_value == ResultStatusType.CUSTOM and project is None:
            raise ValidationError('Custom status must have project')

        self._check_name(data, instance, type_value)

    @classmethod
    def _check_type(cls, data, instance):
        if _TYPE in data and instance and data[_TYPE] != instance.type:
            raise ValidationError('Status type cannot be changed')

        return data.get(_TYPE, getattr(instance, _TYPE, ResultStatusType.CUSTOM))

    def _check_name(self, data, instance, type_value):
        name = data.get(_NAME, getattr(instance, _NAME, None))
        project = data.get(_PROJECT, getattr(instance, _PROJECT, None))
        system_labels = {label.lower() for label in TestStatuses.labels}

        if type_value == ResultStatusType.CUSTOM and name.lower() in system_labels:
            raise ValidationError(f'Status with name "{name}" is forbidden')
        if duplicate := ResultStatusSelector.status_list_by_project_and_name(project=project, name=name).first():
            if duplicate.pk != getattr(instance, 'pk', None):
                raise ValidationError(self.err_msg.format(name, duplicate.name, getattr(project, _NAME, None)))

    @classmethod
    def _check_expression(cls, expression: str, target: str) -> bool:
        return bool(re.search(expression, target, re.IGNORECASE))

    @classmethod
    def _check_hex_color(cls, target: str) -> bool:
        expression = '^#(?:[0-9a-fA-F]{3}){1,2}$'
        return cls._check_expression(expression, target)

    @classmethod
    def _check_rgb_color(cls, target: str) -> bool:
        expression = r'^(rgb)?\(([01]?\d\d?|2[0-4]\d|25[0-5])(\W+)([01]?\d\d?|2[0-4]\d|25[0-5])\W+(([01]?\d\d?|2[0-4]\d|25[0-5])\)?)$'  # noqa: E501
        return cls._check_expression(expression, target)

    @classmethod
    def _check_rgba_color(cls, target: str) -> bool:
        expression = r'^(rgba)?\(([01]?\d\d?|2[0-4]\d|25[0-5])\W+([01]?\d\d?|2[0-4]\d|25[0-5])\W+([01]?\d\d?|2[0-4]\d|25[0-5])\W+?(1|0|0\.[0-9]+|\.[0-9]+)\)$'  # noqa: E501
        return cls._check_expression(expression, target)

    @classmethod
    def _check_color(cls, data, checkers: tuple[Callable[[str], bool], ...]):
        if target := data.get('color'):
            for check in checkers:
                if check(target):
                    return

            raise ValidationError('Status color must be in hex or rgb or rgba')


@deconstructible
class TestPlanParentValidator:
    def __call__(self, attrs):
        parent = attrs.get('parent')
        archived_ancestors = parent.get_ancestors(include_self=True).filter(is_archive=True)
        if archived_ancestors:
            ids = list(archived_ancestors.values_list(_ID, flat=True))
            raise serializers.ValidationError(
                f'Cannot make child to an archived ancestor, archive ancestors ids are: {ids}',
            )


@deconstructible
class TestResultArchiveTestValidator:
    requires_context = True

    def __call__(self, attrs, serializer):
        instance = serializer.instance
        test = attrs.get('test') or serializer.instance.test
        if test.is_archive and not instance:
            raise ValidationError('Cannot create a result in an archived test')
        if instance and (test.is_archive or instance.is_archive):
            raise ValidationError('Cannot update result in an archived test/archived result')


@deconstructible
class TestResultUpdateValidator:
    requires_context = True

    def __init__(self, fields_to_comparator: Iterable[FieldsToComparator]):
        self._fields_to_comparator = fields_to_comparator

    def __call__(self, attrs, serializer):  # noqa: WPS231
        instance = serializer.instance
        payload_attrs = set(attrs.keys())
        attrs_to_validate = chain(*(elem[0] for elem in self._fields_to_comparator))

        time_limited_fields = set(payload_attrs).intersection(set(attrs_to_validate))

        if not instance or not time_limited_fields:
            return

        project_settings = ProjectSettings(**instance.project.settings)

        if not project_settings.is_result_editable:
            raise ValidationError('Results in this project are not editable. Contact with project admin')

        creation_timedelta = now() - instance.created_at
        version_changed = instance.test_case_version != instance.test.case.history.first().history_id
        time_over = (
            project_settings.result_edit_limit
            and creation_timedelta > timedelta(seconds=project_settings.result_edit_limit)
        )
        update_forbidden = time_over or version_changed
        err_msg = self._default_error_message(project_settings.result_edit_limit)

        if version_changed:
            err_msg = 'Test case version changed you can only update "comment" on current result'
        for fields, are_equal in self._fields_to_comparator:
            for field in fields:
                if field not in attrs:
                    continue
                if not are_equal(getattr(instance, field), attrs.get(field)) and update_forbidden:
                    raise ValidationError(err_msg)

    @classmethod
    def _default_error_message(cls, result_edit_limit: int | None):
        if result_edit_limit is None:
            return None
        result_edit_limit_str = WorkTimeProcessor.format_duration(result_edit_limit, to_workday=False)
        return f"""Update gap closed, you can only update "comment" on this result.\n
        Update gap is set to "{result_edit_limit_str}"
        """  # noqa: S608


class TestPlanCasesValidator:
    err_msg = 'You cannot add archive test case, archive test cases ids: {0}'

    def __call__(self, attrs):
        cases_ids = attrs.get('test_cases')
        cases = TestCaseSelector.cases_by_ids(cases_ids, 'pk')
        if archived_cases := [case.pk for case in cases if case.is_archive]:
            raise ValidationError(self.err_msg.format(archived_cases))


class BulkUpdateExcludeIncludeValidator:
    err_msg = 'Included_tests and excluded_tests should not be provided.'

    def __call__(self, attrs):
        if all([attrs.get('included_tests'), attrs.get('excluded_tests')]):
            raise ValidationError(self.err_msg)


class MoveTestsSameProjectValidator:
    err_msg = 'All tests must be in {0} project.'

    def __call__(self, attrs: dict[str, Any]):
        dst_plan = attrs.get('plan')
        current_plan = attrs.get('current_plan')
        if current_plan.project.pk != dst_plan.project.pk:
            raise ValidationError(self.err_msg.format(dst_plan.project.name))


@deconstructible
class TestPlanCustomAttributeValuesValidator(BaseCustomAttributeValuesValidator):
    app_name = 'tests_representation'
    model_name = 'testplan'
    requires_context = True

    def __call__(self, attrs: dict[str, Any], serializer):
        attributes = attrs.get('attributes', {}) or {}
        project = attrs.get(_PROJECT)
        if project is None and (instance := serializer.instance):
            project = instance.project
        attr_getter = partial(CustomAttributeSelector.required_attribute_names_by_project, project=project)
        self._validate(attributes, attr_getter)


@deconstructible
class TestResultCustomAttributeValuesValidator(BaseCustomAttributeValuesValidator):
    app_name = 'tests_representation'
    model_name = 'testresult'
    requires_context = True

    def __call__(self, attrs: dict[str, Any], serializer):
        attributes = attrs.get('attributes', {})
        if test := attrs.get('test'):
            project = test.project
            suite = test.case.suite
        elif instance := serializer.instance:
            project = instance.project
            suite = instance.test.case.suite
        else:
            return
        status = attrs.get(_STATUS, getattr(serializer.instance, _STATUS, None))
        attr_getter = partial(
            CustomAttributeSelector.required_attributes_by_status,
            project=project,
            suite=suite,
            status=status,
        )
        self._validate(attributes, attr_getter)


@deconstructible
class DateRangeValidator:
    def __call__(self, attrs):
        started_at = attrs.get('started_at')
        due_date = attrs.get('due_date')

        if started_at >= due_date:
            raise ValidationError('End date must be greater than start date.')


class AssigneeValidator:
    requires_context = True

    def __call__(self, data, serializer):
        assignee = data.get('assignee')
        if not assignee:
            return
        view_action = serializer.context['view'].action
        project = self._get_project(data, serializer, view_action)
        is_restricted = RoleSelector.restricted_project_access(assignee)
        if not project.is_private and not is_restricted:
            return
        if not RoleSelector.project_view_allowed(assignee, project):
            raise ValidationError('User is not a member of a project.')

    @classmethod
    def _get_project(cls, data, serializer, action: str) -> Project:
        if action == 'bulk_update_tests':
            return data.get('current_plan').project
        return data.get(_PROJECT) or serializer.instance.project
