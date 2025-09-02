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

import logging
import re
from copy import deepcopy
from typing import Any, TypeVar

from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from testy.root.ltree.managers import LtreeManager
from testy.root.ltree.models import LtreeModel
from testy.root.querysets import DeletedQuerySet, DeletedTreeQuerySet, SoftDeleteQuerySet, SoftDeleteTreeQuerySet

logger = logging.getLogger(__name__)
_MT = TypeVar('_MT', bound=models.Model)


class ServiceModelMixin(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def model_create(
        cls: type[_MT],
        fields: list[str],
        data: dict[str, Any],
        commit: bool = True,
    ) -> _MT:
        actually_fields = {key: data[key] for key in fields if key in data}
        instance = cls(**actually_fields)

        if commit:
            instance.full_clean()
            instance.save()

        return instance

    def model_update(  # noqa: WPS231
        self: _MT,
        fields: list[str],
        data: dict[str, Any],
        commit: bool = True,
        force: bool = False,
        skip_history: bool = False,
    ) -> tuple[_MT, list[str]]:
        has_updated = False
        update_fields = []

        for field in fields:
            if field not in data:
                continue

            if getattr(self, field) != data[field]:
                has_updated = True
                setattr(self, field, data[field])
                update_fields.append(field)

        if not has_updated:
            logger.warning('Model was not updated.')

        if (has_updated and commit) or force:
            # needed when there were changes in generic models, for example, attachment of a test case was removed
            self.full_clean()
            if skip_history:
                self.save_without_history(data, update_fields if update_fields else None)
            else:
                self.save(update_fields=update_fields if update_fields else None)
        return self, update_fields

    def save_without_history(self, data, update_fields):
        if not hasattr(self, 'save_without_historical_record'):
            raise ValueError(f'Model {self} not historical')
        self.save_without_historical_record(update_fields=update_fields)

        history_instance = self.history.latest()
        if update_fields:
            for field in update_fields:
                setattr(history_instance, field, data[field])
        history_instance.full_clean(exclude=['history_user', 'history_change_reason'])
        history_instance.save(update_fields=update_fields)

    @transaction.atomic
    def model_clone(  # noqa: WPS231
        self: _MT,
        related_managers: list[str] | None = None,
        attrs_to_change: dict[str, Any] | None = None,
        attachment_references_fields: list[str] | None = None,
        common_attrs_to_change: dict[str, Any] | None = None,
    ) -> _MT:
        self_copy = deepcopy(self)
        attrs = {'pk': None, 'id': None}
        cloned_related_objects = {}
        attachments_mapping = {}

        if not related_managers:
            related_managers = []

        if not attachment_references_fields:
            attachment_references_fields = []

        if attrs_to_change:
            attrs.update(attrs_to_change)

        if common_attrs_to_change:
            attrs.update(common_attrs_to_change)

        for related_manager_name in related_managers:
            related_manager = getattr(self_copy, related_manager_name, None)
            if not related_manager:
                model_class = type(self_copy)
                logger.warning(f'No manager {related_manager_name} on model {model_class}')
                continue
            cloned_related_objects[related_manager_name] = [
                rel_instance.model_clone(common_attrs_to_change=common_attrs_to_change)
                for rel_instance in related_manager.all()
            ]
            if related_manager_name != 'attachments':
                continue
            attachments_mapping = self._map_old_attach_id_to_new(
                related_manager,
                cloned_related_objects[related_manager_name],
            )

        for attr_name, attr_value in attrs.items():
            setattr(self_copy, attr_name, attr_value)

        for field_name in attachment_references_fields:
            for old_id, new_id in attachments_mapping.items():
                formatted_text = self._change_attachments_reference(getattr(self_copy, field_name), old_id, new_id)
                setattr(self_copy, field_name, formatted_text)

        self_copy._state.adding = True
        self_copy.save()
        type(self).objects.filter(pk=self_copy.id).update(
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
        for related_manager_name, instances in cloned_related_objects.items():
            getattr(self_copy, related_manager_name).set(instances)
        return self_copy

    @classmethod
    def _change_attachments_reference(cls, src_text, old_id, new_id):
        return re.sub(f'attachments/{old_id}/', f'attachments/{new_id}/', src_text)

    @classmethod
    def _map_old_attach_id_to_new(cls, related_manager, cloned_objects):
        mapping = {}
        for src_attach, cloned_attach in zip(related_manager.all(), cloned_objects):
            mapping[src_attach.id] = cloned_attach.id
        return mapping


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)


class SoftDeleteTreeManager(LtreeManager):
    def get_queryset(self):
        return SoftDeleteTreeQuerySet(self.model, using=self._db).filter(is_deleted=False)


class DeletedTreeManager(LtreeManager):
    def get_queryset(self):
        return DeletedTreeQuerySet(self.model, using=self._db).filter(is_deleted=True)


class DeletedManager(models.Manager):
    def get_queryset(self):
        return DeletedQuerySet(self.model, using=self._db).filter(is_deleted=True)


class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def delete(self, commit: bool = True, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if commit:
            self.save(*args, **kwargs)

    def restore(self, commit: bool = True, *args, **kwargs):
        self.is_deleted = False
        self.deleted_at = None
        if commit:
            self.save(*args, **kwargs)

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


class BaseModel(ServiceModelMixin, SoftDeleteMixin):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    objects = SoftDeleteManager()
    deleted_objects = DeletedManager()

    class Meta:
        abstract = True

    class ModelHierarchyWeightMeta:
        weight = 0


class LtreeBaseModel(LtreeModel, BaseModel):
    objects = SoftDeleteTreeManager()
    deleted_objects = DeletedTreeManager()

    class MPTTMeta:
        root_node_ordering = False

    class Meta:
        abstract = True
