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
from typing import TYPE_CHECKING, Any, Iterable

from django.db.models import F, Q, QuerySet

from testy.root.ltree.querysets import LtreeQuerySet
from testy.tests_representation.models import Test, TestPlan

if TYPE_CHECKING:
    from testy.tests_description.selectors.suites import TestSuiteSelector


class TestSelector:
    @classmethod
    def test_list(cls) -> QuerySet[Test]:
        return Test.objects.select_related('case').prefetch_related('results').annotate(
            test_suite_description=F('case__suite__description'),
        ).all().order_by('case__name')

    @classmethod
    def test_list_raw(cls) -> QuerySet[Test]:
        return Test.objects.all()

    @classmethod
    def test_list_by_testplan_ids(cls, plan_ids: Iterable[int]) -> QuerySet[Test]:
        return Test.objects.filter(plan__in=plan_ids)

    @classmethod
    def test_list_union(
        cls,
        plans: LtreeQuerySet[TestPlan],
        parent_id: int | None,
        suite_selector: 'type[TestSuiteSelector]',
        has_common_filters: bool,
    ) -> QuerySet[Test]:
        tests = Test.objects.all()
        lookup = Q(plan__in=plans.get_descendants(include_self=True))
        if parent_id is not None:
            lookup |= Q(plan=parent_id)
        if not has_common_filters:
            tests = tests.filter(lookup)
        tests = suite_selector.annotate_suite_path(tests, 'case__suite__path')
        return tests.annotate(assignee_username=F('assignee__username'))

    def test_list_with_last_status(
        self,
        qs: QuerySet[Test] | None = None,
        filter_condition: dict[str, Any] | None = None,
    ) -> QuerySet[Test]:
        if qs is None:
            qs = self.test_list_raw()
        if not filter_condition:
            filter_condition = {}
        return (
            qs
            .select_related('case', 'last_status')
            .prefetch_related('case__suite', 'case__labeled_items', 'case__labeled_items__label', 'assignee')
            .filter(**filter_condition)
            .annotate(
                test_suite_description=F('case__suite__description'),
                estimate=F('case__estimate'),
            )
            .order_by('case__suite', '-id')
        )

    @classmethod
    def test_list_for_bulk_operation(
        cls,
        queryset: QuerySet[Test],
        included_tests: list[Test] | None,
        excluded_tests: list[Test] | None,
    ) -> QuerySet[Test]:
        if included_tests:
            queryset = queryset.filter(pk__in=[test.pk for test in included_tests])
        if excluded_tests:
            queryset = queryset.exclude(pk__in=[test.pk for test in excluded_tests])
        return queryset

    @classmethod
    def test_list_by_ids(cls, ids: Iterable[int]) -> QuerySet[Test]:
        return Test.objects.filter(pk__in=ids)
