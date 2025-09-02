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
import os
from typing import TYPE_CHECKING, Any, Callable, Iterable, Mapping, Protocol

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db.models import Model
from django.utils.deconstruct import deconstructible
from rest_framework import serializers

_ID = 'id'

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Comparator(Protocol):
    def __call__(self, old_value: Any, new_value: Any) -> bool:
        """
        Return True if objects are equal False otherwise.

        Args:
            old_value: first value to compare.
            new_value: second value to compare.
        """


FieldsToComparator = tuple[Iterable[str], Comparator]


@deconstructible
class ExtensionValidator:
    def __call__(self, file):
        name, extension = os.path.splitext(file.name)
        if settings.ALLOWED_FILE_EXTENSIONS and extension not in settings.ALLOWED_FILE_EXTENSIONS:
            message = f'Extension not allowed. Allowed extensions are: {settings.ALLOWED_FILE_EXTENSIONS}'
            raise serializers.ValidationError(message)


@deconstructible
class ProjectValidator:
    def __call__(self, value):
        if not isinstance(value, ContentType):
            return
        try:
            value.model_class()._meta.get_field('project')
        except FieldDoesNotExist:
            if value.model != 'project':
                raise serializers.ValidationError(f'{value} does not have parent project nor project itself')


def compare_related_manager(old_value: 'RelatedManager', new_value: Iterable[Model]) -> bool:
    new_qs = old_value.model.objects.filter(pk__in=[instance.pk for instance in new_value])
    old_qs = old_value.all()
    return not bool(old_qs.difference(new_qs))


def compare_steps(old_value: 'RelatedManager', new_value: list[Mapping[str, Any]]) -> bool:
    old_step_results = old_value.all().order_by(_ID)
    new_value.sort(key=lambda elem: elem.get(_ID))
    for old_step, new_step in zip(old_step_results, new_value):
        if old_step.id != new_step.get(_ID) or old_step.status != new_step.get('status'):  # noqa: WPS221
            return False
    return True


def validator_launcher(
    attrs: dict[str, Any],
    *,
    validator_instance: Callable[[dict[str, Any]], None],
    fields_to_validate: list[str],
    none_valid_fields: list[str] | None = None,
) -> None:
    if not none_valid_fields:
        none_valid_fields = []
    attrs_to_validate = {}
    for field in fields_to_validate:
        attr_value = attrs.get(field)
        if attr_value is None and field not in none_valid_fields:
            return
        attrs_to_validate[field] = attr_value
    validator_instance(attrs_to_validate)


@deconstructible
class CaseInsensitiveUsernameValidator:
    def __call__(self, value):
        if get_user_model().objects.filter(username__iexact=value).exclude(username=value).exists():
            raise ValidationError(
                [{'username': ['A user with that username in a different letter case already exists.']}],
            )
