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

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.serializers import ModelSerializer

from testy.tests_description.models import TestCase, TestSuite
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.tests_representation.models import Parameter, Test, TestPlan
from testy.tests_representation.selectors.tests import TestSelector

logger = logging.getLogger(__name__)

_PROJECT_ID = 'project_id'
_ID = 'id'


class ParameterCopySerializer(ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('data', 'group_name')


class Command(BaseCommand):
    help = 'Copy test plan to required project and test plan'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dst-project-id',
            action='store',
            help='Project where to copy plan',
            required=True,
            type=int,
        )
        parser.add_argument(
            '--src-plan-id',
            action='store',
            help='Plan that you are copying',
            required=True,
            type=int,
        )
        parser.add_argument(
            '--dst-plan-id',
            action='store',
            help='Plan where to copy plan',
            type=int,
        )
        parser.add_argument(
            '--drop-results',
            action='store_true',
            help='Provide this flag if you do not want results to be copied',
            default=False,
        )
        parser.add_argument(
            '--included-statuses',
            nargs='+',
            help='Copy only tests with certain statuses',
        )

    def handle(self, *args, **options) -> None:
        dst_project_id = options.get('dst_project_id')
        src_plan_id = options.get('src_plan_id')
        dst_plan_id = options.get('dst_plan_id')
        drop_results = options.get('drop_results')
        included_statuses = options.get('included_statuses')
        self.copy_plan(dst_project_id, src_plan_id, dst_plan_id, drop_results, included_statuses)

    @transaction.atomic
    def copy_plan(
        self,
        dst_project_id,
        src_plan_id,
        dst_plan_id,
        drop_results: bool,
        included_statuses: list[int | str],
    ) -> None:
        plan_to_copy = get_object_or_404(TestPlan, pk=src_plan_id)

        tests_to_copy = TestSelector().test_list_with_last_status()
        tests_to_copy = TestSuiteSelector.annotate_suite_path(tests_to_copy, 'case__suite__path')

        plans_to_copy = plan_to_copy.get_descendants(
            include_self=True,
        ).prefetch_related(
            'parameters',
        ).order_by(
            'level',
        )

        if included_statuses:
            is_null = False

            if 'null' in included_statuses:
                is_null = True
                included_statuses.remove('null')

            tests_to_copy = self._exclude_statuses(tests_to_copy, plans_to_copy, included_statuses, is_null)
            plans_to_copy = TestPlan.objects.filter(
                pk__in=tests_to_copy.values_list('plan_id', flat=True),
            ).get_ancestors(
                include_self=True,
            ).prefetch_related(
                'parameters',
            ).order_by(
                'level',
            )
        else:
            tests_to_copy = Test.objects.filter(plan__in=plans_to_copy)

        same_project = plan_to_copy.project.id == dst_project_id

        cases_to_copy = TestCase.objects.filter(pk__in=tests_to_copy.values_list('case__id', flat=True))

        suites_to_copy = TestSuite.objects.filter(
            pk__in=cases_to_copy.values_list('suite__id', flat=True),
        ).get_ancestors(
            include_self=True,
        ).order_by(
            'level',
        )

        suite_mappings = self._get_suites_mapping(same_project, dst_project_id, suites_to_copy)

        case_mappings = self._get_cases_mapping(same_project, dst_project_id, cases_to_copy, suite_mappings)

        plan_mappings = {}
        for src_plan in plans_to_copy:
            params_data = ParameterCopySerializer(src_plan.parameters.all(), many=True).data
            copied_or_found_params = []
            for data in params_data:
                parameter, _ = Parameter.objects.get_or_create(**data, project_id=dst_project_id)
                copied_or_found_params.append(parameter)
            copied_plan = src_plan.model_clone(
                attrs_to_change={
                    _PROJECT_ID: dst_project_id,
                    'parent_id': dst_plan_id if plan_to_copy == src_plan else plan_mappings[src_plan.parent.id],
                },
            )
            copied_plan.parameters.set(copied_or_found_params)
            plan_mappings[src_plan.id] = copied_plan.id

        related_managers = [] if drop_results else ['results']
        for src_test in tests_to_copy:
            src_test.model_clone(
                related_managers=related_managers,
                attrs_to_change={
                    'case_id': case_mappings[src_test.case_id],
                    'plan_id': plan_mappings[src_test.plan_id],
                },
                common_attrs_to_change={
                    _PROJECT_ID: dst_project_id,
                },
            )
        TestPlan.objects.rebuild()
        TestSuite.objects.rebuild()

    @classmethod
    def _exclude_statuses(cls, tests, plans_to_copy, included_statuses, is_null: bool):
        q_filter = Q()
        if included_statuses:
            q_filter |= Q(last_status__in=list(map(int, included_statuses)))
        if is_null:
            q_filter |= Q(last_status__isnull=True)
        return tests.filter(
            q_filter,
            plan__in=plans_to_copy,
        )

    @classmethod
    def _get_suites_mapping(cls, same_project: bool, dst_project_id: int, suites_to_copy: QuerySet[TestSuite]):
        if same_project:
            return dict(
                zip(
                    suites_to_copy.values_list(_ID, flat=True),
                    suites_to_copy.values_list(_ID, flat=True),
                ),
            )

        suite_mappings = {}

        for src_suite in suites_to_copy:
            attrs = {_PROJECT_ID: dst_project_id}
            if parent := src_suite.parent:
                attrs['parent_id'] = suite_mappings[parent.id]
            copied_suite = src_suite.model_clone(
                attrs_to_change=attrs,
                related_managers=[],
            )
            suite_mappings[src_suite.id] = copied_suite.id
        return suite_mappings

    @classmethod
    def _get_cases_mapping(
        cls,
        same_project: bool,
        dst_project_id: int,
        cases_to_copy: QuerySet[TestCase],
        suite_mappings: dict[int, int],
    ):
        if same_project:
            return dict(
                zip(
                    cases_to_copy.values_list(_ID, flat=True),
                    cases_to_copy.values_list(_ID, flat=True),
                ),
            )
        case_mappings = {}
        for src_case in cases_to_copy:
            case_mappings[src_case.id] = src_case.model_clone(
                attrs_to_change={'suite_id': suite_mappings[src_case.suite_id]},
                common_attrs_to_change={_PROJECT_ID: dst_project_id},
            ).id
