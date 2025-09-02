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

from django.contrib.contenttypes.models import ContentType

from testy.core.models import CustomAttribute
from testy.tests_representation.selectors.status import ResultStatusSelector

_STATUS_SPECIFIC = 'status_specific'


class CustomAttributeService:
    non_side_effect_fields = ['name', 'project', 'type', 'applied_to']
    applied_to_fields = ['is_required', 'suite_ids', _STATUS_SPECIFIC]

    @classmethod
    def custom_attribute_create(cls, data: dict[str, Any]) -> CustomAttribute:
        applied_to = data.get('applied_to')
        statuses = list(
            ResultStatusSelector
            .status_list(project=data['project'])
            .values_list('id', flat=True),
        )
        for fields in applied_to.values():
            if _STATUS_SPECIFIC in fields and fields[_STATUS_SPECIFIC] is None:
                fields[_STATUS_SPECIFIC] = statuses
        custom_attribute = CustomAttribute.model_create(
            fields=cls.non_side_effect_fields,
            data=data,
            commit=False,
        )
        custom_attribute.full_clean()
        custom_attribute.save()
        return custom_attribute

    @classmethod
    def custom_attribute_create_v1(cls, data: dict[str, Any]) -> CustomAttribute:
        create_dict = {
            data_key: data_value for data_key, data_value in data.items() if data_key in cls.non_side_effect_fields
        }
        if data.get(_STATUS_SPECIFIC) is None:
            data[_STATUS_SPECIFIC] = list(
                ResultStatusSelector
                .status_list(project=data['project'])
                .values_list('id', flat=True),
            )
        ct_names = [ct.model for ct in data.get('content_types', [])]
        applied_to = dict.fromkeys(ct_names, {})
        for ct_name in ct_names:
            for field in cls.applied_to_fields:
                applied_to[ct_name][field] = data.get(field)
        create_dict['applied_to'] = applied_to
        custom_attribute = CustomAttribute.model_create(
            fields=cls.non_side_effect_fields,
            data=create_dict,
            commit=False,
        )
        custom_attribute.full_clean()
        custom_attribute.save()
        return custom_attribute

    @classmethod
    def custom_attribute_update(cls, custom_attribute: CustomAttribute, data: dict[str, Any]) -> CustomAttribute:
        custom_attribute, _ = custom_attribute.model_update(
            fields=cls.non_side_effect_fields,
            data=data,
            commit=False,
        )
        custom_attribute.full_clean()
        custom_attribute.save()
        return custom_attribute

    @classmethod
    def custom_attribute_update_v1(cls, custom_attribute: CustomAttribute, data: dict[str, Any]) -> CustomAttribute:
        update_dict = {
            data_key: data_value for data_key, data_value in data.items() if data_key in cls.non_side_effect_fields
        }
        ct_names = (
            ContentType
            .objects
            .filter(model__in=custom_attribute.applied_to.keys())
            .values_list('model', flat=True)
        )

        if 'content_types' in data:
            ct_names = [ct.model for ct in data.get('content_types', [])]
        applied_to = dict.fromkeys(ct_names, {})
        for ct_name in ct_names:
            for field in cls.applied_to_fields:
                if field_value := data.get(field):
                    applied_to[ct_name][field] = field_value

        custom_attribute, _ = custom_attribute.model_update(
            fields=cls.non_side_effect_fields,
            data=update_dict,
            commit=False,
        )
        custom_attribute.applied_to = cls._update_nested_dict(custom_attribute.applied_to, applied_to)
        custom_attribute.full_clean()
        custom_attribute.save()
        return custom_attribute

    @classmethod
    def _update_nested_dict(
        cls,
        old: dict[str, Any],
        new: dict[str, Any],
    ) -> dict[str, Any]:
        for dict_key, dict_value in new.items():
            if isinstance(dict_value, dict):
                old[dict_key] = cls._update_nested_dict(old.get(dict_key, {}), dict_value)
            else:
                old[dict_key] = dict_value
        return old
