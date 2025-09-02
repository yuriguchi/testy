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
from django.db.models import Model

from testy.core.choices import LabelTypes
from testy.core.models import Label, LabeledItem
from testy.core.selectors.labels import LabelSelector


class LabelService:
    non_side_effect_fields = ['name', 'user', 'project', 'type']

    def label_create(self, data: dict[str, Any]) -> Label:
        return Label.model_create(
            fields=self.non_side_effect_fields,
            data=data,
        )

    def label_update(self, label: Label, data: dict[str, Any]) -> Label:
        label, _ = label.model_update(
            fields=self.non_side_effect_fields,
            data=data,
        )
        return label

    def add(self, labels, content_object, label_kwargs=None, labeled_item_kwargs=None):
        self._project = content_object.project
        labels_objs = self._to_label_model_instances(labels, label_kwargs)

        lookup_kwargs = {
            'object_id': content_object.id,
            'content_type': ContentType.objects.get_for_model(content_object),
            **labeled_item_kwargs,
        }

        for label in labels_objs:
            LabeledItem.objects.get_or_create(label=label, **lookup_kwargs, defaults=None)

    def set(self, labels, content_object, label_kwargs=None, labeled_item_kwargs=None):
        self.clear(content_object)
        self.add(labels, content_object, label_kwargs, labeled_item_kwargs)

    def clear(self, content_object):
        lookup_kwargs = {
            'object_id': content_object.id,
            'content_type': ContentType.objects.get_for_model(content_object),
        }

        LabeledItem.objects.filter(**lookup_kwargs).delete()

    @classmethod
    def restore_by_version(cls, instance: Model, history_id: int):
        labeled_items = LabelSelector.label_list_by_parent_object_and_history_ids(instance, history_id)
        for labeled_item in labeled_items:
            cls._restore_item(labeled_item, instance.history.latest().history_id)

    @classmethod
    def _restore_item(cls, labeled_item: LabeledItem, history_id: int):
        labeled_item.pk = None
        labeled_item.is_deleted = False
        labeled_item.deleted_at = None
        labeled_item.content_object_history_id = history_id
        labeled_item.save()

    def _to_label_model_instances(self, labels, label_kwargs=None):
        label_objs = set()

        existing = []
        labels_to_create = []

        for label in labels:
            name = label['name'].strip()
            label = Label.objects.filter(name__iexact=name, project=self._project).first()
            if label:
                existing.append(label)
                continue
            labels_to_create.append(name)

        label_objs.update(existing)

        for new_label in labels_to_create:
            lookup = {
                'name__iexact': new_label,
                'project': self._project,
                'type': LabelTypes.CUSTOM,
                **label_kwargs,
            }
            existing_or_created_label, _ = Label.objects.get_or_create(**lookup, defaults={'name': new_label})
            label_objs.add(existing_or_created_label)

        return label_objs
