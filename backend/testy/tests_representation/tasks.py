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
from celery import shared_task
from django.contrib.contenttypes.models import ContentType

from testy.tests_representation.models import Test
from testy.tests_representation.selectors.tests import TestSelector
from testy.tests_representation.services.tests import TestService


@shared_task()
def notify_bulk_assign(tests_mapping: dict[str, int], assignee_id: int, user_id: int):
    tests = TestSelector.test_list_by_ids(tests_mapping.keys()).prefetch_related(
        'project',
        'plan',
        'case',
        'assignee',
    )
    ct_id = ContentType.objects.get_for_model(Test).pk
    for test in tests:
        TestService.notify_assignee(test, tests_mapping.get(str(test.pk)), assignee_id, user_id, ct_id)
