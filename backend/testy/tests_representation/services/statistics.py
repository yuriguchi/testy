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
import operator
from datetime import datetime
from functools import reduce
from itertools import groupby
from typing import Any

from django.db.models import Case, Count, DateTimeField, F, FloatField, Q, QuerySet, Sum, Value, When
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone

from testy.core.models import Project
from testy.tests_description.models import TestCase
from testy.tests_representation.choices import UNTESTED_STATUS
from testy.tests_representation.exceptions import DateRangeIsAbsent
from testy.tests_representation.models import Test, TestPlan, TestResult
from testy.tests_representation.selectors.status import ResultStatusSelector
from testy.utilities.sql import DateTrunc
from testy.utilities.time import Period

_POINT = 'point'
_COUNT = 'count'
_COLOR = 'color'
_RESULT_STATUS_NAME = 'status__name'
_RESULT_STATUS_COLOR = 'status__color'
_STATUS = 'status'
_ESTIMATES = 'estimates'
_EMPTY_ESTIMATES = 'empty_estimates'
_PERIOD_DAY = 'period_day'
_ID = 'id'
_NAME = 'name'
_VALUE = 'value'
_LABEL = 'label'


class LabelProcessor:
    def __init__(
        self,
        parameters: dict[str, Any],
        outer_ref_prefix: str | None = 'case',
    ):
        self.labels = []
        self.not_labels = []
        for key in ('labels', 'not_labels'):
            raw_labels: str | list[int] = parameters.get(key)
            if not raw_labels:
                continue
            labels = tuple(raw_labels.split(',') if isinstance(raw_labels, str) else raw_labels)
            setattr(self, key, labels)

        self.operation = operator.and_ if parameters.get('labels_condition') == 'and' else operator.or_
        self.outer_ref_prefix = f'{outer_ref_prefix}__label__ids' if outer_ref_prefix else 'label__ids'

    def process_labels(
        self,
        instances: QuerySet[Test | TestResult | TestCase],
    ) -> QuerySet[Test | TestResult | TestCase]:
        positive_condition = self._make_condition(self.labels)
        negative_condition = self._make_condition(self.not_labels, is_negative=True)

        final_condition = self.operation(positive_condition, negative_condition)
        return instances.filter(final_condition)

    def _make_condition(self, labels: list[int], is_negative: bool = False) -> Q:
        if not labels:
            return Q()
        lookup_key = f'{self.outer_ref_prefix}__contains'
        lookups = [Q(**{lookup_key: [label_id]}) for label_id in labels]
        if is_negative:
            lookups = list(map(operator.inv, lookups))
        return reduce(self.operation, lookups)


class PieChartProcessor:
    def __init__(self, parameters: dict[str, Any]):
        seconds = Period.MINUTE.in_seconds(in_workday=True)
        if estimate_period := parameters.get('estimate_period'):
            estimate_period = next(
                (period for period in Period.list_of_workday() if period.name.lower() in estimate_period.lower()),
                Period.SECOND,
            )
            seconds = estimate_period.in_seconds(in_workday=True)
        self.seconds = seconds

    def process_statistic(
        self,
        parent_test_plans: QuerySet[TestPlan],
        label_processor: LabelProcessor,
        is_archive_condition: Q,
        project_id: int,
        is_whole_project: bool,
        root_only: bool = False,
    ):
        results = []
        total_estimate = Sum(
            Cast(F('case__estimate'), FloatField()) / self.seconds,
            output_field=FloatField(),
        )
        project = Project.objects.filter(id=project_id).first()
        general_filters = Q(project=project)
        if not is_whole_project:
            parent_test_plan = parent_test_plans.first()
            custom_filter = Q(plan=parent_test_plan)
            if not root_only:
                custom_filter |= Q(plan__path__descendant=parent_test_plan.path)
            general_filters &= custom_filter
        tests = (
            Test
            .objects
            .filter(
                general_filters,
                is_archive_condition,
                Q(plan__is_deleted=False),
            )
            .annotate(
                status=Coalesce(F('last_status_id'), Value(UNTESTED_STATUS.id)),
                status_name=Coalesce(F('last_status__name'), Value(UNTESTED_STATUS.name.upper())),
                status_color=Coalesce(F('last_status__color'), Value(UNTESTED_STATUS.color)),
                estimates=Coalesce(total_estimate, 0, output_field=FloatField()),
                is_empty_estimate=Case(
                    When(Q(case__estimate__isnull=True), then=1),
                    default=0,
                ),
                empty_estimates=Sum('is_empty_estimate'),
            )
            .values(
                _STATUS, 'status_color', 'status_name', _ESTIMATES, _EMPTY_ESTIMATES,
            )
            .annotate(count=Count(_ID, distinct=True))
            .order_by('-count')
        )
        if label_processor.labels or label_processor.not_labels:
            tests = label_processor.process_labels(tests)
        presented_statuses = set()
        for test in tests:
            results.append(
                {
                    _ID: test[_STATUS],
                    _LABEL: test['status_name'].upper(),
                    _COLOR: test['status_color'],
                    _VALUE: test['count'],
                    'estimates': round(test[_ESTIMATES], 2),
                    'empty_estimates': test[_EMPTY_ESTIMATES],
                },
            )
            presented_statuses.add(test[_STATUS])
        statuses = ResultStatusSelector.status_list(project=project).exclude(pk__in=presented_statuses)
        for status in statuses:
            results.append(
                {
                    _ID: status.pk,
                    _LABEL: status.name.upper(),
                    _COLOR: status.color,
                    _VALUE: 0,
                    _ESTIMATES: 0,
                    _EMPTY_ESTIMATES: 0,
                },
            )
        if None not in presented_statuses:
            results.append(
                {
                    _ID: UNTESTED_STATUS.id,
                    _LABEL: UNTESTED_STATUS.name.upper(),
                    _COLOR: UNTESTED_STATUS.color,
                    _VALUE: 0,
                    _ESTIMATES: 0,
                    _EMPTY_ESTIMATES: 0,
                },
            )
        return results


class HistogramProcessor:
    def __init__(self, parameters: dict[str, Any]) -> None:
        self.attribute = parameters.get('attribute', None)
        self.period = []
        for key in ('start_date', 'end_date'):
            value = parameters.get(key, None)
            if not value:
                raise DateRangeIsAbsent
            date = datetime.strptime(value, '%Y-%m-%d')
            if key == 'end_date':
                date += timezone.timedelta(days=1)
            self.period.append(
                timezone.make_aware(date),
            )

        self.all_dates = {
            self.period[0] + timezone.timedelta(days=n_day) for n_day in range(
                (self.period[1] - self.period[0]).days,
            )
        }

    def fill_empty_points(self, result: list[dict[str, Any]], test_plan_statuses: QuerySet):
        for unused_date in self.all_dates:
            item = {_POINT: unused_date.date()}
            item.update(
                {
                    status[_STATUS]: {
                        _LABEL: status[_RESULT_STATUS_NAME].lower(),
                        _COUNT: 0,
                        _COLOR: status[_RESULT_STATUS_COLOR],
                    }
                    for status in test_plan_statuses
                },
            )
            result.append(item)
        return result

    def group_by_date(self, instance):
        return instance.get(_PERIOD_DAY, None)

    def group_by_attribute(self, instance):
        key_name = f'attributes__{self.attribute}'
        return instance.get(key_name, None)

    def process_statistic(  # noqa: WPS231
        self,
        parent_test_plans: QuerySet[TestPlan],
        label_processor: LabelProcessor,
        is_archive_condition: Q,
        project_id: int,
        is_whole_project: bool,
        root_only: bool = False,
    ) -> list[dict[str, Any]]:
        query_kwargs = self._get_query_kwargs()
        project = Project.objects.filter(id=project_id).first()
        general_filters = Q(project=project)
        if not is_whole_project:
            parent_test_plan = parent_test_plans.first()
            custom_filter = Q(test__plan=parent_test_plan)
            if not root_only:
                custom_filter |= Q(test__plan__path__descendant=parent_test_plan.path)
            general_filters &= custom_filter

        test_results_formatted = (
            TestResult
            .objects
            .filter(
                general_filters,
                is_archive_condition,
                Q(test__plan__is_deleted=False),
                Q(created_at__range=self.period),
                *query_kwargs.get('filter_condition', []),
            )
            .annotate(**query_kwargs.get('annotate_condition', {}))
            .values(*query_kwargs.get('values_list', []))
            .annotate(status_count=Count(_ID))
            .order_by(query_kwargs.get('order_condition', _ID))
            .distinct()
        )
        if label_processor.labels or label_processor.not_labels:
            test_results_formatted = label_processor.process_labels(test_results_formatted)

        group_func = self.group_by_attribute if self.attribute else self.group_by_date
        grouped_data = groupby(test_results_formatted, group_func)
        result = []
        test_plan_statuses = (
            ResultStatusSelector()
            .status_list(project=project)
            .annotate(status=F(_ID), status__name=F('name'), status__color=F(_COLOR))
            .values(_STATUS, _RESULT_STATUS_NAME, _RESULT_STATUS_COLOR)
        )
        for group_key, group_values in grouped_data:
            if not self.attribute:
                self.all_dates.remove(group_key)

            histogram_bar_data = {
                obj[_STATUS]: {
                    _LABEL: obj[_RESULT_STATUS_NAME].lower(),
                    _COUNT: obj['status_count'],
                    _COLOR: obj[_RESULT_STATUS_COLOR],
                }
                for obj in group_values
            }
            empty_statuses = {
                empty_status[_STATUS]: {
                    _LABEL: empty_status[_RESULT_STATUS_NAME].lower(),
                    _COUNT: 0,
                    _COLOR: empty_status[_RESULT_STATUS_COLOR],
                }
                for empty_status in test_plan_statuses.exclude(pk__in=histogram_bar_data.keys())
            }
            histogram_bar_data.update(empty_statuses)
            histogram_bar_data[_POINT] = group_key if self.attribute else group_key.date()
            result.append(histogram_bar_data)

        if not self.attribute:
            result = self.fill_empty_points(result, test_plan_statuses)

        is_decimal_attribute = all(str(obj[_POINT]).isdecimal() for obj in result)
        if self.attribute and is_decimal_attribute:
            return sorted(result, key=lambda obj: int(obj[_POINT]))

        return sorted(result, key=lambda obj: str(obj[_POINT]))

    def _get_query_kwargs(self):
        query_kwargs = {}
        if self.attribute:
            query_kwargs['order_condition'] = f'attributes__{self.attribute}'
            query_kwargs['values_list'] = (
                f'attributes__{self.attribute}',
                _STATUS,
                _RESULT_STATUS_NAME,
                _RESULT_STATUS_COLOR,
            )
            query_kwargs['filter_condition'] = [Q(attributes__has_key=self.attribute)]

        else:
            query_kwargs['order_condition'] = _PERIOD_DAY
            query_kwargs['values_list'] = (_PERIOD_DAY, _STATUS, _RESULT_STATUS_NAME, _RESULT_STATUS_COLOR)
            query_kwargs['annotate_condition'] = {
                _PERIOD_DAY: DateTrunc(
                    'day',
                    'created_at',
                    output_field=DateTimeField(),
                ),
            }
        return query_kwargs
