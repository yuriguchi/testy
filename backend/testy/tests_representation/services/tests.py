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

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import QuerySet
from simple_history.utils import bulk_update_with_history

from testy.root.celery import app
from testy.tests_description.models import TestCase
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.tests_representation.models import Test, TestPlan
from testy.tests_representation.selectors.tests import TestSelector
from testy.users.models import User

channel_layer = get_channel_layer()


class TestService:
    non_side_effect_fields = ['case', 'plan', 'assignee', 'is_archive', 'project']

    def test_create(self, data: dict[str, Any]) -> Test:
        test = Test.model_create(
            fields=self.non_side_effect_fields,
            data=data,
            commit=False,
        )
        test.project = test.case.project
        test.full_clean()
        test.save()
        return test

    @transaction.atomic
    def test_delete_by_test_case_ids(self, test_plan: TestPlan, test_case_ids: list[int]) -> None:
        Test.objects.filter(plan=test_plan).filter(case__in=test_case_ids).delete()

    @transaction.atomic
    def bulk_test_create(self, test_plans: list[TestPlan], cases: QuerySet[TestCase]):
        test_objects = [  # noqa: WPS361
            self._make_test_model({'case': case, 'plan': tp, 'project': tp.project}) for tp in test_plans
            for case in cases
        ]
        return Test.objects.bulk_create(test_objects)

    def test_update(
        self,
        test: Test,
        data: dict[str, Any],
        user: User,
        commit: bool = True,
        notify_user: bool = True,
    ) -> Test:
        old_assignee_id = test.assignee_id
        test, _ = test.model_update(
            fields=self.non_side_effect_fields,
            data=data,
            commit=commit,
        )
        if not notify_user:
            return test
        if assignee := data.get('assignee'):
            assignee = assignee.pk
        ct_id = ContentType.objects.get_for_model(test).pk
        self.notify_assignee(test, old_assignee_id, assignee, user.pk, ct_id)
        return test

    def bulk_update_tests(self, queryset: QuerySet[Test], payload: dict[str, Any], user: User):
        tests = TestSelector.test_list_for_bulk_operation(
            queryset=queryset,
            included_tests=payload.pop('included_tests', None),
            excluded_tests=payload.pop('excluded_tests', None),
        )
        updated_tests = []

        test_to_old_assignee = {}
        for test in tests:
            test_to_old_assignee[test.pk] = test.assignee_id
            updated_tests.append(self.test_update(test, payload, commit=False, user=user, notify_user=False))

        if assignee := payload.get('assignee'):
            assignee = assignee.pk

        app.send_task(
            'testy.tests_representation.tasks.notify_bulk_assign',
            args=[
                test_to_old_assignee,
                assignee,
                user.pk,
            ],
        )
        bulk_update_with_history(
            updated_tests,
            Test,
            fields=payload.keys(),
            default_user=user,
            default_change_reason='Bulk update tests',
        )
        qs = TestSelector().test_list_with_last_status(filter_condition={'pk__in': tests})
        return TestSuiteSelector.annotate_suite_path(qs, 'case__suite__path')

    def get_testcase_ids_by_testplan(self, test_plan: TestPlan) -> QuerySet[int]:
        return test_plan.tests.values_list('case', flat=True)

    @classmethod
    def notify_assignee(
        cls,
        test: Test,
        old_assignee_id: int | None,
        new_assignee_id: int | None,
        actor_id: int,
        ct_id: int,
    ) -> None:
        if old_assignee_id and new_assignee_id != old_assignee_id:
            cls.produce_action(test, old_assignee_id, actor_id, 'test.unassigned', ct_id)
        if new_assignee_id:
            cls.produce_action(test, new_assignee_id, actor_id, 'test.assigned', ct_id)

    @classmethod
    def produce_action(
        cls,
        test: Test,
        receiver_id: int,
        actor_id: int,
        action_type: str,
        content_type_id: int,
    ) -> None:
        async_to_sync(channel_layer.send)(
            'notifications',
            {
                'type': action_type,
                'object_id': test.pk,
                'content_type_id': content_type_id,
                'receiver_id': receiver_id,
                'actor_id': actor_id,
                'project_id': test.project.pk,
                'plan_id': test.plan.pk,
                'name': test.case.name,
            },
        )

    def _make_test_model(self, data):
        return Test.model_create(
            fields=self.non_side_effect_fields,
            data=data,
            commit=False,
        )
