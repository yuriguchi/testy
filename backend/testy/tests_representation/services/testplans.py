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
from itertools import product
from typing import Any, Iterable

from django.db import transaction

from testy.core.services.attachments import AttachmentService
from testy.tests_description.selectors.cases import TestCaseSelector
from testy.tests_representation.models import Parameter, TestPlan
from testy.tests_representation.services.tests import TestService

_TEST_CASES = 'test_cases'
_PARENT = 'parent'
_ATTACHMENTS = 'attachments'


class TestPlanService:
    non_side_effect_fields = [
        'name', _PARENT, 'started_at', 'due_date', 'finished_at', 'is_archive', 'project', 'description', 'attributes',
    ]

    @transaction.atomic
    def testplan_create(self, data: dict[str, Any]) -> list[TestPlan]:
        test_plan = TestPlan.model_create(fields=self.non_side_effect_fields, data=data)
        if test_cases_ids := data.get(_TEST_CASES, []):
            test_cases = TestCaseSelector.cases_by_ids(test_cases_ids, 'pk')
            TestService().bulk_test_create([test_plan], test_cases)
        for attachment in data.get(_ATTACHMENTS, []):
            AttachmentService().attachment_set_content_object(attachment, test_plan)
        return test_plan

    @transaction.atomic
    def testplan_bulk_create(self, data: dict[str, Any]) -> list[TestPlan]:
        parameters = data.get('parameters')
        parameter_combinations = self._parameter_combinations(parameters)
        created_plans = []
        num_of_combinations = len(parameter_combinations)
        for _ in range(num_of_combinations):
            test_plan_object: TestPlan = TestPlan.model_create(
                fields=self.non_side_effect_fields,
                data=data,
                commit=False,
            )
            created_plans.append(test_plan_object)
        created_plans = TestPlan.objects.bulk_create(created_plans)
        for plan, combined_parameters in zip(created_plans, parameter_combinations):
            plan.parameters.set(combined_parameters)
        if test_cases_ids := data.get('test_cases', []):
            test_cases = TestCaseSelector.cases_by_ids(test_cases_ids, 'pk')
            TestService().bulk_test_create(created_plans, test_cases)
        for test_plan in created_plans:
            for attachment in data.get(_ATTACHMENTS, []):
                AttachmentService().attachment_set_content_object(attachment, test_plan)
        return created_plans

    @transaction.atomic
    def testplan_update(self, *, test_plan: TestPlan, data: dict[str, Any]) -> TestPlan:
        test_plan, _ = test_plan.model_update(
            fields=self.non_side_effect_fields,
            data=data,
        )

        if (test_cases := data.get(_TEST_CASES)) is not None:  # test_cases may be empty list
            old_test_case_ids = set(TestService().get_testcase_ids_by_testplan(test_plan))
            new_test_case_ids = set(test_cases)

            # deleting tests
            if delete_test_case_ids := old_test_case_ids - new_test_case_ids:
                TestService().test_delete_by_test_case_ids(test_plan, delete_test_case_ids)

            # creating tests
            if create_test_case_ids := new_test_case_ids - old_test_case_ids:
                cases = TestCaseSelector.cases_by_ids(create_test_case_ids, 'pk')
                TestService().bulk_test_create([test_plan], cases)
        attachments = data.get(_ATTACHMENTS, [])
        AttachmentService().attachments_update_content_object(attachments, test_plan)
        test_plan.refresh_from_db(fields=[_ATTACHMENTS])
        return test_plan

    @classmethod
    def _parameter_combinations(cls, parameters: Iterable[Parameter]) -> list[tuple[Parameter, ...]]:
        """
        Return all possible combinations of parameters by group name.

        Args:
            parameters: list of Parameter objects.

        Returns:
             list of tuple of every possible combination of parameters.
        """
        group_parameters = {}

        for parameter in parameters:
            group_parameters.setdefault(parameter.group_name, []).append(parameter)

        return list(product(*group_parameters.values()))
