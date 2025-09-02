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
from typing import Any, Iterable, Protocol

from django.db import models
from django.utils.deconstruct import deconstructible
from rest_framework import serializers

from testy.core.models import CustomAttribute, Project
from testy.tests_description.models import TestCase, TestSuite
from testy.tests_representation.selectors.status import ResultStatusSelector


class ReturnsRequiredAttrs(Protocol):
    def __call__(self, content_type_name: str) -> Iterable[CustomAttribute]:
        """
        Protocol for returning a list of required attributes.

        Args:
            content_type_name: The content type name to filter by.
        """


@deconstructible
class CustomAttributeCreateValidator:
    requires_context = True

    def __call__(self, attrs: dict[str, Any], serializer):
        project = attrs.get('project')
        applied_to = attrs.get('applied_to')
        if not project and serializer.instance:
            project = serializer.instance.project

        self._validate_all_suites_project_related(project, applied_to)

    @classmethod
    def _validate_all_suites_project_related(cls, project: Project, applied_to: dict[str, Any] | None) -> None:
        if not cls._is_project_includes_all_suites(project, applied_to):
            raise serializers.ValidationError('Field suite_ids contains non project-related items')

    @classmethod
    def _is_project_includes_all_suites(cls, project: Project, applied_to: dict[str, Any] | None) -> bool:
        is_count_match = True
        if applied_to is None:
            return is_count_match
        for ct_name in applied_to.keys():
            suite_ids = applied_to.get(ct_name, {}).get('suite_ids', [])
            if not suite_ids:
                continue
            requested_suites_count = len(suite_ids)
            found_suites_count = TestSuite.objects.filter(project=project, id__in=suite_ids).count()

            is_count_match = is_count_match and found_suites_count == requested_suites_count
        return is_count_match


@deconstructible
class CustomAttributeV1CreateValidator:
    requires_context = True

    def __call__(self, attrs: dict[str, Any], serializer):
        project = attrs.get('project')
        suites = attrs.get('suite_ids')

        if not project and serializer.instance:
            project = serializer.instance.project

        self._validate_all_suites_project_related(project, suites)

    @classmethod
    def _validate_all_suites_project_related(cls, project: Project, suite_ids: list[int]):
        if not cls._is_project_includes_all_suites(project, suite_ids):
            raise serializers.ValidationError('Field suite_ids contains non project-related items')

    @classmethod
    def _is_project_includes_all_suites(cls, project: Project, suite_ids: list[int]) -> bool:
        if not suite_ids:
            return True

        requested_suites_count = len(suite_ids)
        found_suites_count = TestSuite.objects.filter(project=project, id__in=suite_ids).count()

        return found_suites_count == requested_suites_count


class BaseCustomAttributeValuesValidator:
    app_name = ''
    model_name = ''

    @classmethod
    def _validate(cls, attributes: dict, required_attrs_getter: ReturnsRequiredAttrs):
        required_attributes = required_attrs_getter(content_type_name=cls.model_name)
        attribute_keys = set(attributes.keys())
        if any(',' in attr_key for attr_key in attribute_keys):
            raise serializers.ValidationError('Attribute key has comma')
        if diff := set(required_attributes).difference(attribute_keys):
            diff_list = list(diff)
            raise serializers.ValidationError(f'Missing following required attributes: {diff_list}')

        if empty_attributes := [name for name in required_attributes if not attributes[name]]:
            raise serializers.ValidationError(f'Found empty required attributes: {empty_attributes}')


class ProjectStatusOrderValidator:
    def __call__(self, status_order):
        if not isinstance(status_order, dict):
            raise serializers.ValidationError('Status order must be dict')
        for key, value in status_order.items():
            if not (str(key).isdigit() and str(value).isdigit()):
                raise serializers.ValidationError('Key and value in Status order should contain digits')
        return status_order


class DefaultStatusValidator:
    requires_context = True

    def __call__(self, attrs, serializer):
        view = serializer.context.get('view')
        default_status = attrs.get('default_status')
        if default_status is None or view.action not in {'update', 'partial_update', 'create'}:
            return
        project_id = view.kwargs.get('pk')
        if not ResultStatusSelector.status_by_project_exists(default_status, project_id):
            raise serializers.ValidationError('Status not available for project')


class RecursionValidator:
    requires_context = True

    def __init__(self, model: type[models.Model]):
        self.model = model

    def __call__(self, attrs, serializer):
        instance = serializer.instance
        parent = attrs.get('parent', None)
        if not parent or not serializer.instance:
            return
        old_parent = getattr(serializer.instance, 'parent', None)
        old_parent_pk = None
        if old_parent:
            old_parent_pk = old_parent.pk
        if parent.pk == old_parent_pk:
            return
        new_path = f'{parent.path}.{instance.id}'
        if new_path.startswith(instance.path):
            raise serializers.ValidationError('Updating this node causes a recursion')
        if self.model.objects.filter(path__startswith=new_path).exists():
            raise serializers.ValidationError('This path already exists, potential recursion detected')


class CasesCopyProjectValidator:
    def __call__(self, attrs: dict[str, Any]):
        dst_suite = attrs.get('dst_suite_id')
        if not dst_suite:
            return
        cases_ids = [case['id'] for case in attrs.get('cases')]
        cases = TestCase.objects.filter(pk__in=cases_ids)
        cases_projects = cases.values_list('project_id', flat=True).distinct('project_id')
        if cases_projects.count() != 1 or cases_projects[0] != dst_suite.project_id:
            raise serializers.ValidationError('Cannot copy case to another project.')
