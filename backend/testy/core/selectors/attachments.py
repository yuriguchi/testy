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
from typing import Iterable, List, TypeVar

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, QuerySet

from testy.core.models import Attachment

_MT = TypeVar('_MT', bound=Model)


class AttachmentSelector:
    @classmethod
    def attachment_list(cls) -> QuerySet[Attachment]:
        return Attachment.objects.all()

    @classmethod
    def attachment_list_by_parent_object(cls, model: type[Model], object_id: int) -> QuerySet[Attachment]:
        return Attachment.objects.filter(
            content_type=ContentType.objects.get_for_model(model).id,
            object_id=object_id,
        )

    @classmethod
    def attachment_list_from_object_with_excluding(
        cls,
        model: type[Model],
        exclude_ids: list[int],
    ) -> QuerySet[Attachment]:
        return model.attachments.exclude(pk__in=exclude_ids)

    @classmethod
    def attachment_list_by_ids(cls, ids: Iterable[int], model: type[Model]) -> QuerySet[Attachment]:
        content_type = ContentType.objects.get_for_model(model)
        return Attachment.objects.filter(content_type=content_type, object_id__in=ids)

    @classmethod
    def attachment_list_by_parent_object_and_history_ids(  # noqa: WPS118
        cls,
        parent_model: type[Model],
        object_id: int,
        history_ids: List[int],
    ):
        return QuerySet(Attachment).filter(
            content_type=ContentType.objects.get_for_model(parent_model).id,
            object_id=object_id,
            content_object_history_ids__contains=history_ids,
        )
