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
import datetime
from functools import partial
from typing import Any

import pytimeparse
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from rest_framework import serializers

from testy.core.selectors.custom_attribute import CustomAttributeSelector
from testy.core.validators import BaseCustomAttributeValuesValidator
from testy.tests_description.models import TestCase


@deconstructible
class TestCaseCustomAttributeValuesValidator(BaseCustomAttributeValuesValidator):
    app_name = 'tests_description'
    model_name = 'testcase'

    def __call__(self, attrs: dict[str, Any]):
        custom_attr = attrs.get('attributes', {})
        project = attrs['project']
        suite = attrs['suite']

        attr_getter = partial(
            CustomAttributeSelector.required_attribute_names_by_project_and_suite,
            project=project,
            suite=suite,
        )
        self._validate(custom_attr, attr_getter)


class CasesCopyProjectValidator:
    def __call__(self, attrs: dict[str, Any]):
        dst_suite = attrs.get('dst_suite_id')
        cases_ids = [case['id'] for case in attrs.get('cases')]
        cases = TestCase.objects.filter(pk__in=cases_ids)
        cases_projects = cases.values_list('project_id', flat=True).distinct('project_id')
        if cases_projects.count() != 1 or cases_projects[0] != dst_suite.project_id:
            raise serializers.ValidationError('Cannot copy case to another project.')


@deconstructible
class EstimateValidator:
    def __call__(self, value):  # noqa: WPS238, WPS231
        estimate = value.get('estimate')
        estimate = estimate.strip()
        if estimate[0] == '-':
            raise ValidationError('Estimate value cannot be negative.')
        for week_alias in ('w', 'wk', 'week', 'weeks'):
            if week_alias in estimate:
                raise ValidationError('Max estimate period is a day')
        estimate = f'{estimate}m' if estimate.isnumeric() else estimate
        secs = pytimeparse.parse(estimate)
        if not secs:
            raise ValidationError('Invalid estimate format.')
        try:
            datetime.timedelta(seconds=secs)
        except OverflowError:
            raise ValidationError('Estimate value is too big.')


@deconstructible
class TestSuiteCustomAttributeValuesValidator(BaseCustomAttributeValuesValidator):
    app_name = 'tests_description'
    model_name = 'testsuite'
    requires_context = True

    def __call__(self, attrs: dict[str, Any], serializer):
        attributes = attrs.get('attributes', {}) or {}
        project = attrs.get('project')
        if project is None and (instance := serializer.instance):
            project = instance.project
        attr_getter = partial(CustomAttributeSelector.required_attribute_names_by_project, project=project)
        self._validate(attributes, attr_getter)
