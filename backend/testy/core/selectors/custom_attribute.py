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
from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, IntegerField, Q, QuerySet, When

from testy.core.constants import (
    CONTENT_TYPES_POSITIONS,
    CUSTOM_ATTRIBUTES_ALLOWED_APPS,
    CUSTOM_ATTRIBUTES_ALLOWED_MODELS,
)
from testy.core.models import CustomAttribute, Project
from testy.tests_description.models import TestSuite

_NAME = 'name'
_APPLIED_TO_LOOKUP = 'applied_to__'


class CustomAttributeSelector:
    @classmethod
    def custom_attribute_list(cls) -> QuerySet[CustomAttribute]:
        return CustomAttribute.objects.all()

    @classmethod
    def required_attribute_names_by_project_and_suite(
        cls,
        project: Project,
        suite: TestSuite,
        content_type_name: str,
    ) -> QuerySet[CustomAttribute]:
        required_attr = cls._required_attributes_by_project_and_suite(project, suite, content_type_name)
        return required_attr.values_list(_NAME, flat=True)

    @classmethod
    def required_attribute_names_by_project(cls, project: Project, content_type_name: str) -> QuerySet[CustomAttribute]:
        return (
            cls
            ._required_attributes_by_project_and_model(project, content_type_name)
            .values_list(_NAME, flat=True)
        )

    @classmethod
    def required_attributes_by_status(
        cls,
        project: Project,
        suite: TestSuite,
        content_type_name: str,
        status,
    ) -> QuerySet[CustomAttribute]:
        required_attr = cls._required_attributes_by_project_and_suite(
            project,
            suite,
            content_type_name,
        ).filter(**{f'{_APPLIED_TO_LOOKUP}{content_type_name}__status_specific__contains': [status.id]})
        return required_attr.values_list(_NAME, flat=True)

    @classmethod
    def get_allowed_content_types(cls) -> QuerySet[ContentType]:
        conditions_list = []
        for model_name, position in CONTENT_TYPES_POSITIONS:
            conditions_list.append(When(model=model_name, then=position))
        return (
            ContentType
            .objects
            .annotate(ordering=Case(*conditions_list, default=0, output_field=IntegerField()))
            .filter(
                app_label__in=CUSTOM_ATTRIBUTES_ALLOWED_APPS,
                model__in=CUSTOM_ATTRIBUTES_ALLOWED_MODELS,
            )
            .order_by('ordering', 'id')
        )

    @classmethod
    def _required_attributes_by_project_and_suite(
        cls, project: Project, suite: TestSuite, content_type_name: str,
    ) -> QuerySet[CustomAttribute]:
        required_attr = cls._required_attributes_by_project_and_model(project, content_type_name)
        non_suite_specific_condition = Q(**{f'{_APPLIED_TO_LOOKUP}{content_type_name}__suite_ids': []})
        non_suite_specific_condition |= ~Q(**{f'{_APPLIED_TO_LOOKUP}{content_type_name}__has_key': 'suite_ids'})
        non_suite_specific = required_attr.filter(non_suite_specific_condition)
        suite_specific = required_attr.filter(
            **{f'{_APPLIED_TO_LOOKUP}{content_type_name}__suite_ids__contains': [suite.id]},
        )
        return non_suite_specific | suite_specific

    @classmethod
    def _required_attributes_by_project_and_model(
        cls,
        project: Project,
        model_name: str,
    ) -> QuerySet[CustomAttribute]:
        return CustomAttribute.objects.filter(
            project=project,
            **{f'applied_to__{model_name}__is_required': True},
        )
