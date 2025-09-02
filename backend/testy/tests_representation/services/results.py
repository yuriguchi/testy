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

from typing import Any, Iterable

from django.db import transaction
from simple_history.utils import bulk_create_with_history, bulk_update_with_history

from testy.core.services.attachments import AttachmentService
from testy.tests_description.selectors.cases import TestCaseSelector
from testy.tests_representation.models import Test, TestResult, TestStepResult
from testy.tests_representation.signals import pre_create_result
from testy.users.models import User


class TestResultService:
    non_side_effect_fields = [
        'status', 'user', 'test', 'comment', 'is_archive', 'test_case_version', 'execution_time', 'attributes',
    ]

    step_non_side_effect_fields = ['test_result', 'step', 'status', 'project']

    @transaction.atomic
    def result_create(self, data: dict[str, Any], user: User) -> TestResult:
        pre_create_result.send(sender=self.result_create, data=data)
        test_result: TestResult = TestResult.model_create(
            fields=self.non_side_effect_fields,
            data=data,
            commit=False,
        )
        test_result.user = user
        test_result.project = test_result.test.case.project
        test_result.test_case_version = TestCaseSelector().case_version(test_result.test.case)
        test_result.full_clean()
        test_result.save()

        for attachment in data.get('attachments', []):
            AttachmentService().attachment_set_content_object(attachment, test_result)

        for steps_results in data.get('steps_results', []):
            steps_results['test_result'] = test_result
            steps_results['project'] = test_result.project
            TestStepResult.model_create(
                fields=self.step_non_side_effect_fields,
                data=steps_results,
            )

        return test_result

    @transaction.atomic
    def result_update(self, test_result: TestResult, data: dict[str, Any]) -> TestResult:
        test_result, updated_fields = test_result.model_update(
            fields=self.non_side_effect_fields,
            data=data,
            commit=False,
        )

        if updated_fields:
            test_result.test_case_version = TestCaseSelector().case_version(test_result.test.case)
        test_result.full_clean()
        test_result.save(update_fields=updated_fields)

        AttachmentService().attachments_update_content_object(data.get('attachments', []), test_result)

        for step_result_data in data.get('steps_results', []):
            step_result = TestStepResult.objects.get(pk=step_result_data['id'])
            step_result.model_update(
                fields=self.step_non_side_effect_fields,
                data=step_result_data,
            )

        return test_result

    @classmethod
    @transaction.atomic
    def result_bulk_create(cls, results: Iterable[TestResult], user: User, batch_size: int = 500) -> list[TestResult]:
        results = bulk_create_with_history(results, TestResult, batch_size=batch_size, default_user=user)
        id_to_status = {result.test_id: result.status for result in results}
        tests = Test.objects.filter(id__in=id_to_status.keys())
        tests_to_update = []
        for test in tests:
            test.last_status = id_to_status[test.id]
            tests_to_update.append(test)
        bulk_update_with_history(
            tests_to_update,
            Test,
            batch_size=batch_size,
            default_user=user,
            fields=['last_status'],
        )
        return results
