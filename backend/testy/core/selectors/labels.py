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
from typing import Iterable

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, QuerySet
from django.db.models.functions import Lower

from testy.core.models import Label, LabeledItem
from testy.tests_representation.selectors.testplan import TestPlanSelector


class LabelSelector:
    @classmethod
    def label_list(cls) -> QuerySet[Label]:
        return Label.objects.all().select_related('user').order_by(Lower('name'))

    @classmethod
    def label_list_by_testplans(cls, testplan_ids: Iterable[int]) -> QuerySet[Label]:
        testplans = TestPlanSelector().plans_by_ids(testplan_ids)

        return Label.objects.filter(
            id__in=testplans.get_descendants(
                include_self=True,
            ).prefetch_related(
                'tests', 'tests__case', 'tests__case__labeled_items', 'tests__case__labeled_items__label',
            ).filter(
                tests__is_deleted=False,
                tests__case__labeled_items__is_deleted=False,
            ).values_list(
                'tests__case__labeled_items__label', flat=True,
            ).distinct(),
        )

    @classmethod
    def label_list_by_ids(cls, ids: Iterable[int], field_name: str) -> QuerySet[Label]:
        return Label.objects.filter(**{f'{field_name}__in': ids}).order_by('id')

    @classmethod
    def label_list_by_parent_object_and_history_ids(cls, instance: Model, history_id: int):
        return QuerySet(LabeledItem).filter(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk,
            content_object_history_id=history_id,
        )
