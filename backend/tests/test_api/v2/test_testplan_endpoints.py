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
import itertools
from collections import defaultdict
from copy import deepcopy
from datetime import timedelta
from http import HTTPStatus
from operator import attrgetter
from typing import Any, Iterable
from unittest import mock

import allure
import pytest
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from django.forms import model_to_dict
from django.utils import timezone

from tests import constants
from tests.commons import RequestType, model_to_dict_via_serializer
from tests.error_messages import (
    DATE_RANGE_ERROR,
    FOUND_EMPTY_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG,
    MISSING_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG,
    PERMISSION_ERR_MSG,
)
from tests.mock_serializers.v2 import TestPlanOutputMockSerializer, TestPlanUnionMockSerializer, TestUnionMockSerializer
from testy.core.models import Label
from testy.tests_description.models import TestCase
from testy.tests_representation.choices import TestStatuses
from testy.tests_representation.models import Test, TestPlan, TestResult
from testy.tests_representation.selectors.status import ResultStatusSelector
from testy.tests_representation.validators import TestPlanCasesValidator
from testy.utilities.sql import get_max_level
from testy.utilities.tree import form_tree_prefetch_objects


@pytest.mark.django_db(reset_sequences=True, transaction=True)
@allure.parent_suite('Test plans')
@allure.suite('Integration tests')
@allure.sub_suite('Endpoints')
class TestPlanEndpoints:
    view_name_detail = 'api:v2:testplan-detail'
    view_name_list = 'api:v2:testplan-list'
    view_name_statistics = 'api:v2:testplan-statistics'
    view_name_project_statistics = 'api:v2:project-testplan-statistics'
    view_name_activity = 'api:v2:testplan-activity'
    view_name_case_ids = 'api:v2:testplan-cases'
    view_name_histogram = 'api:v2:testplan-histogram'
    view_name_project_histogram = 'api:v2:project-testplan-histogram'
    view_name_copy = 'api:v2:testplan-copy'
    view_name_labels = 'api:v2:testplan-labels'
    view_name_union = 'api:v2:testplan-union'

    @allure.title('Test list display')
    def test_list(self, superuser_client, several_test_plans_from_api, project):
        with allure.step('Generate data for tests'):
            expected_response = model_to_dict_via_serializer(
                TestPlan.objects.filter(pk__in=several_test_plans_from_api).order_by('name'),
                many=True,
                serializer_class=TestPlanOutputMockSerializer,
            )
        response = superuser_client.send_request(
            self.view_name_list,
            query_params={'project': project.id, 'ordering': 'id'},
        )
        assert response.json_strip() == expected_response

    @allure.title('Test detail display')
    def test_retrieve(self, superuser_client, test_plan_from_api):
        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_plan_from_api.get('id')},
        )
        actual_dict = response.json()
        with allure.step('Validate response is matching expected data'):
            assert actual_dict == test_plan_from_api, 'Actual model dict is different from expected'

    @pytest.mark.parametrize('number_of_param_groups, number_of_entities_in_group', [(1, 3), (2, 2), (3, 4)])
    def test_creation(
        self,
        superuser_client,
        combined_parameters,
        project,
        attachment_factory,
        number_of_param_groups,
        number_of_entities_in_group,
    ):
        parameters, expected_number_of_plans = combined_parameters
        allure_title = 'Test plan creation with number of label groups: {0}, with number of labels: {1}'
        allure.dynamic.title(allure_title.format(number_of_param_groups, number_of_entities_in_group))
        testplan_dict = {
            'name': 'Test plan',
            'due_date': constants.END_DATE,
            'started_at': constants.DATE,
            'parameters': parameters,
            'project': project.id,
            'attachments': [attachment_factory(content_type=None, object_id=None).id],
        }
        response = superuser_client.send_request(
            self.view_name_list,
            testplan_dict,
            HTTPStatus.CREATED,
            RequestType.POST,
        )
        response_body = response.json()
        actual_parameters_combinations = []
        with allure.step('Validate parameters on test plan'):
            for plan in response_body:
                params_from_plan = plan.get('parameters').sort()
                assert params_from_plan not in actual_parameters_combinations, 'Found duplicate params in TestPlans'
                actual_parameters_combinations.append(plan.get('parameters'))
        with allure.step('Validate number of plans'):
            assert TestPlan.objects.count() == expected_number_of_plans, f'Expected number of test plans ' \
                                                                         f'"{expected_number_of_plans}"' \
                                                                         f'actual: "{TestPlan.objects.count()}"'
        with allure.step('Validate attachments exist'):
            for test_plan in TestPlan.objects.all():
                assert test_plan.attachments.exists()

    @allure.title('Test due date validation')
    def test_due_date_restrictions(self, project, superuser_client):
        with allure.step('Set due date >= started_at'):
            testplan_dict = {
                'name': 'Test plan',
                'due_date': constants.DATE,
                'started_at': constants.DATE,
                'project': project.id,
            }
        response = superuser_client.send_request(
            self.view_name_list,
            testplan_dict,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        endpoint_plans = response.json()
        with allure.step('Validate error message from response'):
            assert endpoint_plans['errors'][0] == DATE_RANGE_ERROR

    @pytest.mark.parametrize('number_of_param_groups, number_of_entities_in_group', [(1, 3), (2, 2), (3, 4)])
    @allure.title('Test tests generated on test plan creation')
    def test_tests_generated_on_create(self, superuser_client, combined_parameters, test_case_factory, project):
        number_of_cases = 5
        case_ids = [test_case_factory(project=project).id for _ in range(number_of_cases)]
        parameters, expected_number_of_plans = combined_parameters
        number_of_tests = number_of_cases * expected_number_of_plans
        testplan_dict = {
            'name': 'Test plan',
            'due_date': constants.END_DATE,
            'started_at': constants.DATE,
            'parameters': parameters,
            'test_cases': case_ids,
            'project': project.id,
        }
        response = superuser_client.send_request(
            self.view_name_list,
            testplan_dict,
            HTTPStatus.CREATED,
            RequestType.POST,
        )
        test_plans = response.json()
        pk = test_plans[0].get('id')
        with allure.step('Validate number of created tests'):
            assert Test.objects.count() == number_of_tests
        with allure.step('Validate number of cases'):
            assert TestCase.objects.count() == number_of_cases

        update_dict = {
            'test_cases': case_ids[:-1],
        }
        superuser_client.send_request(
            self.view_name_detail,
            update_dict,
            HTTPStatus.OK,
            RequestType.PATCH,
            reverse_kwargs={'pk': pk},
        )
        with allure.step('Validate number of tests after update'):
            assert Test.objects.count() == number_of_tests - 1, 'More then one test was deleted by updating'

    @pytest.mark.parametrize(
        'slice_num, expected_number, validation_msg',
        [
            (None, 5, 'Validate number of tests did not change'),
            (1, 1, 'Validate number of tests decreased'),
            (0, 0, 'Validate no tests found'),
        ],
        ids=['Update with same cases', 'Update to one case', 'Update to 0 cases'],
    )
    @allure.title('Test number of tests updated on test plan update')
    def test_tests_generated_deleted_on_partial_update(
        self,
        superuser_client,
        test_plan_from_api,
        test_case_factory,
        slice_num,
        expected_number,
        validation_msg,
    ):
        number_of_cases = 5
        case_ids = [test_case_factory().id for _ in range(number_of_cases)]
        assert not Test.objects.count()
        assert TestCase.objects.count() == number_of_cases
        with allure.step(f'Create test plan with {number_of_cases} test cases'):
            superuser_client.send_request(
                self.view_name_detail,
                data={'test_cases': case_ids},
                expected_status=HTTPStatus.OK,
                request_type=RequestType.PATCH,
                reverse_kwargs={'pk': test_plan_from_api.get('id')},
            )
        with allure.step(f'Update test plan with {number_of_cases} test cases'):
            superuser_client.send_request(
                self.view_name_detail,
                data={'test_cases': case_ids[:slice_num]},
                expected_status=HTTPStatus.OK,
                request_type=RequestType.PATCH,
                reverse_kwargs={'pk': test_plan_from_api.get('id')},
            )
        with allure.step(validation_msg):
            assert Test.objects.count() == expected_number

    @allure.title('Test test plan deletion')
    def test_delete(self, superuser_client, test_plan_factory):
        test_plan = test_plan_factory()
        assert TestPlan.objects.count() == 1, 'Test case was not created'
        superuser_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': test_plan.pk},
        )
        with allure.step('Validate test plan does not exist'):
            assert not TestPlan.objects.count()

    @allure.title('Test test plan is editable only for admin after being archived')
    def test_archived_editable_for_admin_only(self, api_client, test_plan_factory, user):
        api_client.force_login(user)
        plan = test_plan_factory(is_archive=True)
        response = api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': plan.pk},
            request_type=RequestType.PATCH,
            expected_status=HTTPStatus.FORBIDDEN,
            data={},
        )
        with allure.step('Validate error message from response'):
            assert response.json()['detail'] == PERMISSION_ERR_MSG

    def test_parameter_filter(
        self,
        superuser_client,
        test_plan_with_parameters_factory,
        parameter_factory,
        project,
    ):
        with allure.step('Create parameters that will be presented in every test plan'):
            common_group = [parameter_factory(project=project) for _ in range(3)]
        with allure.step('Add different parameters to group 1 and 2'):
            group_1 = deepcopy(common_group)
            group_2 = deepcopy(common_group)
            group_1.append(parameter_factory())
            group_2.append(parameter_factory())
        group_mapping = {
            'common': common_group,
            'group_1': group_1,
            'group_2': group_2,
        }
        plan_mapping = defaultdict(list)
        with allure.step('Generate testplans with different parameter groups'):
            for key, group in group_mapping.items():
                plan = test_plan_with_parameters_factory(parameters=group, project=project)
                plan_mapping['common'].append(plan.id)
                if key == 'common':
                    continue
                plan_mapping[key].append(plan.id)
        for key, group in group_mapping.items():
            with allure.step(f'Validate filter by {key} group returns all objects'):
                response = superuser_client.send_request(
                    self.view_name_list,
                    query_params={
                        'project': project.id,
                        'parameters': ','.join([str(elem.id) for elem in group]),
                    },
                )
                actual_data = [elem['id'] for elem in response.json_strip()]
                assert actual_data == plan_mapping[key]

    def test_parameter_filter_invalid_values(
        self,
        superuser_client,
        test_plan_with_parameters_factory,
        parameter_factory,
        project,
    ):
        with allure.step('Create parameters that will be presented in every test plan'):
            parameters = [parameter_factory(project=project) for _ in range(3)]
        with allure.step('Create plan'):
            test_plan_with_parameters_factory(parameters=parameters, project=project)
        with allure.step('Validate filter by non-existent group returns empty response'):
            response = superuser_client.send_request(
                self.view_name_list,
                query_params={
                    'project': project.id,
                    'parameters': '20000',
                },
            )
            assert not response.json_strip(), 'Test plan displayed with non-existent parameter.'
        with allure.step('Validate incorrect parameter'):
            response = superuser_client.send_request(
                self.view_name_list,
                query_params={
                    'project': project.id,
                    'parameters': ','.join([str(elem.id) for elem in parameters]) + ',2000',
                },
            )
            assert not response.json_strip(), 'If incorrect id is in filter no plans will be returned.'

    @pytest.mark.parametrize('is_query_param', [True, False])
    def test_statistics(
        self,
        superuser_client,
        project,
        test_plan_factory,
        test_factory,
        test_case_factory,
        test_result_factory,
        result_status_factory,
        is_query_param,
    ):
        allure.dynamic.title(f'Test plans statistics view with pk in {"query" if is_query_param else "url"}')
        view_name = self.view_name_project_statistics if is_query_param else self.view_name_statistics
        test_plan = test_plan_factory(project=project)
        number_of_statuses = {
            0: 6,
            1: 12,
            2: 3,
            3: 10,
            4: 0,
            5: 1,
            6: 15,
            7: 1,
        }
        estimates = {
            1: 60,
            2: 3600,
            5: 57780,
        }
        estimates_in_minutes = {
            1: 1.0,
            2: 60.0,
            5: 963.0,
        }
        statuses = [result_status_factory(project=project) for _ in range(len(number_of_statuses))]
        for status_key, status in enumerate(statuses):
            for idx in range(number_of_statuses[status_key]):
                estimate = estimates.get(status_key, None)
                test_case = test_case_factory(estimate=estimate)
                if idx % 2 == 0:
                    test_result_factory(
                        test=test_factory(plan=test_plan, case=test_case, project=project),
                        status=status,
                        project=project,
                    )
                else:
                    test_result_factory(
                        test=test_factory(plan=test_plan, case=test_case, project=project),
                        status=status,
                        project=project,
                        is_archive=True,
                    )
        response_body = superuser_client.send_request(
            view_name,
            reverse_kwargs=None if is_query_param else {'pk': test_plan.id},
            query_params={'parent': test_plan.id} if is_query_param else None,
        ).json()
        label_to_stat = {}
        estimates_to_stat = {}
        empty_estimates = {}
        colors = {}
        for elem in response_body:
            for dict_obj, key in zip(
                [label_to_stat, estimates_to_stat, empty_estimates, colors],
                ['value', 'estimates', 'empty_estimates', 'color'],
            ):
                dict_obj[elem['label'].lower()] = elem[key]
        for status_key, status in enumerate(statuses):
            if not number_of_statuses[status_key] and status.name.lower() not in label_to_stat:
                continue
            with allure.step(f'Validate number of statuses for {status_key}'):
                assert number_of_statuses[status_key] == label_to_stat[status.name.lower()], f'Statistics for ' \
                                                                                             f'{status.name} is wrong'
                assert status.color == colors[status.name.lower()], f'Wrong color of status {status.name}'
                if status_key not in estimates:
                    assert empty_estimates[status.name.lower()] == label_to_stat[status.name.lower()], \
                        'Wrong empty estimates'
                    assert estimates_to_stat[status.name.lower()] == 0, f'Incorrect estimate for status {status.name}'
                else:
                    assert empty_estimates[status.name.lower()] == 0, 'Estimates is more than 0'
                    expected = estimates_in_minutes[status_key] * number_of_statuses[status_key]
                    assert estimates_to_stat[status.name.lower()] == expected, \
                        f'Estimate not equal for status {status.name}'

    @pytest.mark.parametrize(
        'view_name',
        ['api:v1:testplan-statistics', 'api:v1:testplan-histogram'],
        ids=['pie chart', 'histogram'],
    )
    @pytest.mark.parametrize(
        'label_query, error_message',
        [(',123', 'Empty value is not allowed.'), ('asd', 'Enter a number.')],
        ids=['with empty query value', 'with character query value'],
    )
    def test_statistics_with_invalid_query(
            self,
            superuser_client,
            test_plan,
            label_query,
            error_message,
            request,
            view_name,
    ):
        allure.dynamic.title(f'Test statistics endpoints: {request.node.callspec.id}')
        content = superuser_client.send_request(
            view_name,
            reverse_kwargs={'pk': test_plan.id},
            query_params={'labels': label_query},
            expected_status=HTTPStatus.BAD_REQUEST,
        ).json()
        assert error_message in content

    @pytest.mark.parametrize(
        'root_only, parent_count',
        [(True, 0), (False, 1)],
    )
    def test_root_only_statistics(
        self,
        api_client,
        authorized_superuser,
        project,
        test_plan_factory,
        test_factory,
        result_status_factory,
        test_case,
        test_result_factory,
        root_only,
        parent_count,
    ):
        parent_test_plan = test_plan_factory(project=project)
        child_test_plan = test_plan_factory(parent=parent_test_plan, project=project)
        result = test_result_factory(
            test=test_factory(
                plan=child_test_plan,
                case=test_case,
                project=project,
            ),
            project=project,
            status=result_status_factory(project=project),
        )
        for test_plan in [parent_test_plan, child_test_plan]:
            test_plan.refresh_from_db()
            count = 1 if test_plan.parent else parent_count
            content = api_client.send_request(
                self.view_name_statistics,
                reverse_kwargs={'pk': test_plan.pk},
                query_params={'root_only': root_only},
            ).json()
            results = next(
                (obj for obj in content if obj['label'] == result.status.name.upper()),
            )
            assert results['value'] == count

    @pytest.mark.parametrize('is_query_param', [True, False], ids=['pk in query', 'pk in url'])
    @pytest.mark.parametrize(
        'estimate, period, expected_value',
        [
            (3600, 'minutes', '60.0'),
            (21_600, 'hours', '6.0'),
            (28_800, 'days', '1.0'),
        ],
        ids=[
            'estimate = 1h to minutes',
            'estimate = 6h to hours',
            'estimate = 8h to days',
        ],
    )
    def test_statistics_estimates_period(
        self,
        superuser_client,
        project,
        test_plan_factory,
        test_factory,
        test_case_factory,
        test_result_factory,
        estimate,
        period,
        expected_value,
        request,
        result_status_factory,
        is_query_param,
    ):
        allure.dynamic.title(f'Test plans statics by estimate periods {request.node.callspec.id}')
        view_name = self.view_name_project_statistics if is_query_param else self.view_name_statistics
        test_plan = test_plan_factory(project=project)
        test_case = test_case_factory(estimate=estimate, project=project)
        status = result_status_factory(project=project)
        test_result_factory(
            test=test_factory(plan=test_plan, case=test_case, project=project),
            status=status,
            project=project,
        )
        query_params = {'estimate_period': period}
        if is_query_param:
            query_params['parent'] = test_plan.id
        content = superuser_client.send_request(
            view_name,
            reverse_kwargs=None if is_query_param else {'pk': test_plan.id},
            query_params=query_params,
        ).json()
        actual_results = next(
            (obj for obj in content if obj['label'] == status.name.upper()),
        )
        with allure.step('Validate estimate value'):
            assert str(actual_results['estimates']) == expected_value, (
                f'Estimate did not match: expected {expected_value},'
                f' got: {actual_results["estimates"]}'
            )

    @allure.title('Test statistics changed after cases update on test plan')
    def test_statistics_after_plan_cases_updated(
        self,
        project,
        superuser_client,
        test_plan_factory,
        test_case_factory,
    ):
        test_plan = test_plan_factory(project=project)
        number_of_cases = 5
        new_number_of_cases = 3
        estimates = {'seconds': 104_520, 'minutes': 1742}
        untested_label = TestStatuses.UNTESTED.label.lower()
        with allure.step(f'Generate {number_of_cases} test cases'):
            case_ids = [
                test_case_factory(estimate=estimates['seconds'], project=project).id for _ in range(number_of_cases)
            ]
            assert TestCase.objects.count() == number_of_cases
        with allure.step('Add cases to test plan'):
            superuser_client.send_request(
                self.view_name_detail,
                data={'test_cases': case_ids},
                expected_status=HTTPStatus.OK,
                request_type=RequestType.PATCH,
                reverse_kwargs={'pk': test_plan.id},
            )
        with allure.step('Request statics'):
            content = superuser_client.send_request(
                self.view_name_statistics,
                reverse_kwargs={'pk': test_plan.id},
            ).json()
        label_to_stat = {}
        estimates_to_stat = {}
        with allure.step('Validate statistics before update'):
            for elem in content:
                label_to_stat[elem['label'].lower()] = elem['value']
                estimates_to_stat[elem['label'].lower()] = elem['estimates']

            assert label_to_stat[untested_label] == number_of_cases, 'Incorrect statistics before update'
            assert estimates_to_stat[untested_label] == estimates['minutes'] * number_of_cases, \
                'Incorrect estimate before update'
        with allure.step(f'Update test plan with {new_number_of_cases} cases'):
            superuser_client.send_request(
                self.view_name_detail,
                data={'test_cases': case_ids[:new_number_of_cases]},
                expected_status=HTTPStatus.OK,
                request_type=RequestType.PATCH,
                reverse_kwargs={'pk': test_plan.id},
            )
        with allure.step('Validate statistics after update'):

            content = superuser_client.send_request(
                self.view_name_statistics,
                reverse_kwargs={'pk': test_plan.id},
            ).json()
            label_to_stat = {}
            estimates_to_stat = {}
            for elem in content:
                label_to_stat[elem['label'].lower()] = elem['value']
                estimates_to_stat[elem['label'].lower()] = elem['estimates']

            assert label_to_stat[untested_label] == new_number_of_cases, 'Incorrect statistics after update'
            assert estimates_to_stat[untested_label] == estimates['minutes'] * new_number_of_cases, \
                'Incorrect estimate after update'

    @pytest.mark.parametrize(
        'label_names, not_label_names, labels_condition, number_of_items',
        [
            (('blue_bank', 'green_bank'), None, 'or', 7),
            (('blue_bank', 'green_bank'), None, 'and', 2),
            (('blue_bank',), ('green_bank',), 'or', 8),
            (('blue_bank',), ('green_bank',), 'and', 3),
            (('blue_bank', 'red_bank'), ('green_bank',), 'or', 8),
            (('blue_bank', 'red_bank'), ('green_bank',), 'and', 0),
            (None, ('blue_bank',), 'or', 5),
            (None, ('blue_bank', 'green_bank'), 'or', 8),
            (None, ('blue_bank', 'green_bank'), 'and', 3),
        ],
    )
    def test_statistic_with_labels(
        self,
        superuser_client,
        cases_with_labels,
        label_names,
        not_label_names,
        labels_condition,
        number_of_items,
    ):
        title = 'Test statistics for{0}{1} with condition {2}'
        allure.dynamic.title(
            title.format(
                ' ' + ', '.join(label_names) if label_names else '',
                ' ' + ', '.join(not_label_names) if not_label_names else '',
                labels_condition,
            ),
        )
        labels, cases, test_plan, _ = cases_with_labels
        query_params = {}
        if label_names:
            query_params['labels'] = self._label_query_params(label_names)
        if not_label_names:
            query_params['not_labels'] = self._label_query_params(not_label_names)
        query_params['labels_condition'] = labels_condition
        content = superuser_client.send_request(
            self.view_name_statistics,
            reverse_kwargs={'pk': test_plan.id},
            query_params=query_params,
        ).json()
        if number_of_items or content:
            assert content[0]['value'] == number_of_items

    @pytest.mark.parametrize('is_query_param', [True, False], ids=['pk in query', 'pk in url'])
    @pytest.mark.parametrize(
        'attribute, attr_values',
        [
            (None, None),
            ('run_id', ['first_value', 'second_value']),
        ],
        ids=['by date', 'by attribute'],
    )
    def test_histogram(
        self,
        superuser_client,
        project,
        test_plan_factory,
        test_factory,
        test_result_factory,
        attribute,
        attr_values,
        request,
        result_status_factory,
        is_query_param,
    ):
        allure.dynamic.title(f'Test histogram aggregation {request.node.callspec.id}')
        view_name = self.view_name_project_histogram if is_query_param else self.view_name_histogram
        test_plan = test_plan_factory(project=project)
        number_of_statuses = {
            0: 6,
            1: 12,
            2: 4,
            3: 10,
            4: 0,
            6: 16,
            7: 1,
            8: 11,
        }
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=1)
        if attribute:
            expected_results = [{'point': attr_value} for attr_value in attr_values]
        else:
            expected_results = [
                {'point': start_date.strftime('%Y-%m-%d')},
                {'point': end_date.strftime('%Y-%m-%d')},
            ]
        statuses = list(ResultStatusSelector().status_list_raw())
        statuses.extend([
            result_status_factory(project=project)
            for _ in range(len(number_of_statuses) - len(statuses))
        ])
        for status_key, status in zip(number_of_statuses, statuses):
            count = int(number_of_statuses[status_key] / 2)
            for _ in range(count):
                attributes = {attribute: attr_values[0]} if attribute else {}
                test_result_factory(
                    test=test_factory(plan=test_plan, project=project),
                    status=status,
                    created_at=start_date,
                    attributes=attributes,
                    project=project,
                )
            expected_results[0][status.pk] = {
                'label': status.name.lower(),
                'color': status.color,
                'count': count,
            }
            for _ in range(count):
                attributes = {attribute: attr_values[1]} if attribute else {}
                test_result_factory(
                    test=test_factory(plan=test_plan, project=project),
                    status=status,
                    created_at=end_date,
                    attributes=attributes,
                    project=project,
                )
            expected_results[1][status.pk] = {
                'label': status.name.lower(),
                'color': status.color,
                'count': count,
            }
        query_params = {
            'start_date': start_date.date(),
            'end_date': end_date.date(),
            'attribute': attribute if attribute else '',
        }
        if is_query_param:
            query_params['parent'] = test_plan.id
        content = superuser_client.send_request(
            view_name,
            reverse_kwargs=None if is_query_param else {'pk': test_plan.id},
            query_params=query_params,
            expected_status=HTTPStatus.OK,
        ).json()
        assert len(expected_results) == len(content), 'Expected result did not match result'
        for idx in range(len(expected_results)):
            for key, value in expected_results[idx].items():
                point = expected_results[idx]['point']
                value_from_response = content[idx][str(key)]
                assert value == value_from_response, (
                    f'Expect in point = {point}, '
                    f'{key} = {value}, get value = {value_from_response}'
                )

    @pytest.mark.parametrize(
        'label_names, not_label_names, labels_condition, number_of_items',
        [
            (('blue_bank', 'green_bank'), None, 'or', 7),
            (('blue_bank', 'green_bank'), None, 'and', 2),
            (('blue_bank',), ('green_bank',), 'or', 8),
            (('blue_bank',), ('green_bank',), 'and', 3),
            (('blue_bank', 'red_bank'), ('green_bank',), 'or', 8),
            (('blue_bank', 'red_bank'), ('green_bank',), 'and', 0),
            (None, ('blue_bank',), 'or', 5),
            (None, ('blue_bank', 'green_bank'), 'or', 8),
            (None, ('blue_bank', 'green_bank'), 'and', 3),
        ],
    )
    def test_histogram_with_labels(
        self,
        superuser_client,
        cases_with_labels,
        label_names,
        not_label_names,
        labels_condition,
        number_of_items,
    ):
        labels, cases, test_plan, status = cases_with_labels
        now_date = timezone.now().date()
        query_params = {
            'start_date': now_date,
            'end_date': now_date,
            'labels_condition': labels_condition,
        }
        title = 'Test statistics for{0}{1} with condition {2}'
        allure.dynamic.title(
            title.format(
                ' ' + ', '.join(label_names) if label_names else '',
                ' ' + ', '.join(not_label_names) if not_label_names else '',
                labels_condition,
            ),
        )
        if label_names:
            query_params['labels'] = self._label_query_params(label_names)
        if not_label_names:
            query_params['not_labels'] = self._label_query_params(not_label_names)
        content = superuser_client.send_request(
            self.view_name_histogram,
            reverse_kwargs={'pk': test_plan.id},
            query_params=query_params,
            expected_status=HTTPStatus.OK,
        ).json()
        assert len(content), 'Get empty histogram data'
        actual_result_value = content[-1][str(status.pk)]
        assert actual_result_value == {'count': number_of_items, 'color': status.color, 'label': status.name.lower()}, \
            f'Expected {number_of_items} results, got {actual_result_value}'

    @pytest.mark.parametrize(
        'root_only, parent_count',
        [(True, 0), (False, 1)],
    )
    def test_root_only_histogram(
        self,
        api_client,
        authorized_superuser,
        project,
        test_plan_factory,
        test_factory,
        result_status_factory,
        test_case,
        test_result_factory,
        root_only,
        parent_count,
    ):
        parent_test_plan = test_plan_factory(project=project)
        child_test_plan = test_plan_factory(parent=parent_test_plan, project=project)
        result_status = result_status_factory(project=project)
        test_result_factory(
            test=test_factory(
                plan=child_test_plan,
                case=test_case,
                project=project,
            ),
            project=project,
            status=result_status,
        )
        now_date = timezone.now().date()
        query_params = {
            'start_date': now_date,
            'end_date': now_date,
            'root_only': root_only,
        }
        for test_plan in [parent_test_plan, child_test_plan]:
            test_plan.refresh_from_db()
            count = 1 if test_plan.parent else parent_count
            content = api_client.send_request(
                self.view_name_histogram,
                reverse_kwargs={'pk': test_plan.pk},
                query_params=query_params,
            ).json()[0]
            assert content[str(result_status.id)]['count'] == count

    @allure.title('Test plan cannot be parent to itself')
    def test_child_parent_logic(self, superuser_client, test_plan_factory):
        parent = test_plan_factory()
        child = test_plan_factory(parent=parent)
        superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': parent.id},
            data={'parent': child.id},
            request_type=RequestType.PATCH,
            expected_status=HTTPStatus.BAD_REQUEST,
        )

    def test_search(
        self,
        api_client,
        authorized_superuser,
        test_plan_with_parameters_factory,
        parameter_factory,
        project,
    ):
        parameters = [parameter_factory(project=project) for _ in range(2)]
        search_name = 'search_name'
        with allure.step('Create plan that will be found'):
            found_plan = test_plan_with_parameters_factory(project=project, parameters=parameters, name=search_name)
        with allure.step('Create plan that will not be found'):
            test_plan_with_parameters_factory(project=project)
        expected_output = model_to_dict_via_serializer(
            [found_plan],
            TestPlanOutputMockSerializer,
            many=True,
            as_json=True,
        )
        with allure.step('Validate only valid options are returned'):
            actual_data = api_client.send_request(
                self.view_name_list,
                query_params={'project': project.id, 'treesearch': search_name, 'ordering': 'id'},
            ).json_strip(as_json=True)
            assert actual_data == expected_output

    @allure.title('Test plan activity view')
    def test_activity(
        self,
        superuser_client,
        test_plan_factory,
        test_factory,
        test_result_factory,
        user_factory,
        result_status_factory,
    ):
        parent_plan = test_plan_factory()
        inner_plan = test_plan_factory(parent=parent_plan)
        plan = test_plan_factory(parent=inner_plan)
        test = test_factory(plan=plan)
        users_list = []
        result_list = []
        status1 = result_status_factory(project=test.project)
        status2 = result_status_factory(project=test.project)
        with allure.step('Create results by "Vasily Testovich{idx}" users'):
            for idx in range(int(constants.NUMBER_OF_OBJECTS_TO_CREATE / 2)):
                user = user_factory(first_name='Vasily', last_name=f'Testovich{idx}')
                users_list.append(user)
                result_list.append(test_result_factory(user=user, status=status1, test=test))
        with allure.step('Create results by "Yana Albertovna{idx}" users with shifted result date'):
            for idx in range(int(constants.NUMBER_OF_OBJECTS_TO_CREATE / 2)):
                user = user_factory(first_name='Yana', last_name=f'Albertovna{idx}')
                users_list.append(user)
                result = test_result_factory(user=user, status=status2, test=test)
                with mock.patch(
                    'django.utils.timezone.now',
                    return_value=result.created_at + timezone.timedelta(days=3),
                ):
                    result.save()
        body = superuser_client.send_request(
            self.view_name_activity,
            reverse_kwargs={'pk': parent_plan.id},
        ).json_strip()
        with allure.step('Validate results are split in 2 dates'):
            assert len(body) == 2, 'We expect history events in two different dates.'
        with allure.step('Validate breadcrumbs titles'):
            for date in body.values():
                for action in date:
                    assert action['breadcrumbs']['title'] == plan.name
                    assert action['breadcrumbs']['parent']['title'] == inner_plan.name
                    assert action['breadcrumbs']['parent']['parent']['title'] == parent_plan.name

    def test_activity_filters(
        self,
        superuser_client,
        generate_historical_objects,
    ):
        parent_plan, users_list, test_list, status_list = generate_historical_objects
        conditions = [
            ('history_user',
             [
                 (users_list[0].pk, 1),
                 (f'{users_list[0].pk},{users_list[2].pk},{users_list[4].pk},{users_list[6].pk}', 4), ('0', 0),
             ],
             ),
            ('test', [(test_list[0].pk, 5), (test_list[1].pk, 10), ('0', 0)]),
            ('status',
             [
                 (status_list[0].pk, 5), (status_list[1].pk, 10), (f'{status_list[0].pk},{status_list[1].pk}', 15),
                 ('0', 0),
             ],
             ),
            ('history_type', [('~', 5), ('%2B', 10), ('~,%2B', 15), ('ASD', 0)]),
        ]
        for filter_name, filter_values in conditions:
            allure.dynamic.title(f'Test filter by {filter_name}')
            for filter_value in filter_values:
                with allure.step(f'Validate filter by {filter_value}'):
                    args, number_of_objects = filter_value
                    response = superuser_client.send_request(
                        self.view_name_activity,
                        reverse_kwargs={'pk': parent_plan.id},
                        query_params={filter_name: args},
                    ).json()
                    assert number_of_objects == response['count']

    @pytest.mark.parametrize('ordering', ['history_user', 'test__case__name', 'history_date', 'history_type'])
    def test_activity_ordering(self, superuser_client, generate_historical_objects, ordering):
        allure.dynamic.title(f'Test ordering by {ordering}')
        parent_plan, _, _, _ = generate_historical_objects
        for sign in ['', '-']:
            with allure.step(f'Validate {"asc" if sign else "desc"} ordering'):
                results = TestResult.history.filter().order_by('history_date', f'{sign}{ordering}')
                results = list(results)
                content = superuser_client.send_request(
                    self.view_name_activity,
                    reverse_kwargs={'pk': parent_plan.id},
                    query_params={'ordering': f'history_date,{sign}{ordering}'},
                ).json()
                response_results = []
                for elem in content['results'].values():
                    response_results.extend(elem)
                for result, response_result in zip(results, response_results):
                    assert result.id == response_result['id'], 'Wrong order returned.'

    @pytest.mark.parametrize(
        'search_data, number_of_objects',
        [
            ('v.testovich', 5),
            ('v.testovich0', 1),
            ('testovich', 15),
            ('TestCaseName', 15),
            ('non-existent', 0),
        ],
    )
    def test_activity_search_filter(
        self, superuser_client, generate_historical_objects, search_data,
        number_of_objects,
    ):
        allure.dynamic.title(f'Test activity search filter by {search_data}')
        parent_plan, _, _, _ = generate_historical_objects
        response = superuser_client.send_request(
            self.view_name_activity,
            reverse_kwargs={'pk': parent_plan.id},
            query_params={'search': search_data},
        ).json()
        assert response['count'] == number_of_objects, 'Number of found objects did not match.'

    @pytest.mark.parametrize('nesting_level', [0, 1])
    def test_archived_parent_forbidden(self, superuser_client, test_plan_factory, nesting_level):
        allure.dynamic.title(f'Test choosing archived plan as parent is forbidden for nesting level {nesting_level}')
        plan_to_update = test_plan_factory()
        parent = test_plan_factory(is_archive=True)
        for _ in range(nesting_level):
            parent = test_plan_factory(parent=parent)
        superuser_client.send_request(
            self.view_name_list,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.BAD_REQUEST,
        )
        superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': plan_to_update.pk},
            request_type=RequestType.PATCH,
            data={'parent': parent.pk},
            expected_status=HTTPStatus.BAD_REQUEST,
        )

    @allure.title('Test case ids display by test plan')
    def test_cases_by_plan_id(self, superuser_client, test_factory, test_plan_factory):
        root_plan = test_plan_factory()
        inner_plan_lvl_1 = test_plan_factory(parent=root_plan)
        inner_plan_2_lvl_1 = test_plan_factory(parent=root_plan)
        inner_plan_lvl_2 = test_plan_factory(parent=inner_plan_lvl_1)
        plans = [
            root_plan,
            inner_plan_lvl_1,
            inner_plan_2_lvl_1,
            inner_plan_lvl_2,
        ]
        expected_qs = [
            Test.objects.all(),
            Test.objects.filter(plan=inner_plan_lvl_1) | Test.objects.filter(plan=inner_plan_lvl_2),
            Test.objects.filter(plan=inner_plan_2_lvl_1),
            Test.objects.filter(plan=inner_plan_lvl_2),
        ]
        for plan in plans:
            test_factory(plan=plan)
        with allure.step('Validate nested plans cases displayed'):
            for plan, expected_qs in zip(plans, expected_qs):
                case_ids = superuser_client.send_request(
                    self.view_name_case_ids,
                    reverse_kwargs={'pk': plan.id},
                ).json()['case_ids']
                assert sorted(case_ids) == sorted(test.case.id for test in expected_qs.order_by('case__id'))
        with allure.step('Validate nested plans cases not displayed with include_children=False'):
            for plan in plans:
                case_ids = superuser_client.send_request(
                    self.view_name_case_ids,
                    reverse_kwargs={'pk': plan.id},
                    query_params={'include_children': False},
                ).json()['case_ids']
                assert sorted(case_ids) == sorted(
                    (test.case.id for test in Test.objects.filter(plan=plan).order_by('case__id')),
                )

    @pytest.mark.parametrize('to_plan', [True, False])
    def test_plan_copying_with_dst_plan(
        self,
        superuser_client,
        test_result_factory,
        test_plan_factory,
        attachment_factory,
        project,
        test_factory,
        to_plan,
    ):
        title = 'Test plan copying {0}'
        allure.dynamic.title(
            title.format('destination plan specified' if to_plan else 'destination plan not specified'),
        )
        tests_to_copy = []
        plans_to_copy = []
        excluded_fields_plan = ['tree_id', 'id', 'parent', 'finished_at']
        root_plan = test_plan_factory(project=project)
        plans_to_copy.append(root_plan)
        tests_to_copy.append(test_factory(project=project, plan=root_plan))
        nested_plan = test_plan_factory(project=project, parent=root_plan)
        plans_to_copy.append(nested_plan)
        tests_to_copy.append(test_factory(project=project, plan=nested_plan))
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            plan = test_plan_factory(project=project, parent=nested_plan)
            plans_to_copy.append(plan)
            if idx % 2:
                test = test_factory(project=project, plan=plan)
                result = test_result_factory(test=test, project=project)
                assert test.last_status.id == result.id, 'Last status was not set'
                tests_to_copy.append(test)
            else:
                test_factory(project=project, plan=plan, is_archive=True)
        plan_ct = ContentType.objects.get_for_model(TestPlan)
        for plan in plans_to_copy:
            attachment_factory(object_id=plan.id, content_type=plan_ct)
        payload = {
            'plans': [
                {
                    'plan': root_plan.pk,
                },
            ],
            'keep_assignee': True,
        }
        if to_plan:
            dst_plan = test_plan_factory(project=project)
            payload['dst_plan'] = dst_plan.pk
        copied_plans_from_resp = superuser_client.send_request(
            self.view_name_copy,
            request_type=RequestType.POST,
            data=payload,
        ).json()
        copied_plans_ids = [plan['id'] for plan in copied_plans_from_resp]
        copied_plans = list(TestPlan.objects.filter(Q(pk__in=copied_plans_ids)))
        for plan in copied_plans:
            assert plan.attachments.count() == 1, 'Attachment was not copied'
        copied_tests = list(Test.objects.filter(plan__pk__in=copied_plans_ids, is_archive=False))
        self._validate_copied_objects(
            sorted(plans_to_copy, key=attrgetter('name')),
            sorted(copied_plans, key=attrgetter('name')),
            excluded_fields=excluded_fields_plan,
        )
        self._validate_copied_objects(
            sorted(tests_to_copy, key=attrgetter('id')),
            sorted(copied_tests, key=attrgetter('id')),
            excluded_fields=['id', 'plan', 'last_status'],
        )
        assert not any(copied_test.last_status for copied_test in copied_tests), (
            'The status of the copied test is not empty'
        )

    @pytest.mark.parametrize('attribute_name', ['name', 'started_at', 'due_date'])
    def test_plan_copying_attr_changed(
        self,
        superuser_client,

        test_plan_factory,
        project,
        attribute_name,
    ):
        plan_to_copy = test_plan_factory(project=project)
        plan_payload = {
            'plan': plan_to_copy.pk,
        }
        if attribute_name == 'name':
            plan_payload['new_name'] = 'New name'
        else:
            plan_payload[attribute_name] = timezone.now().isoformat()
        copied_plan_id = superuser_client.send_request(
            self.view_name_copy,
            request_type=RequestType.POST,
            data={
                'plans': [
                    plan_payload,
                ],
            },
        ).json()[0]['id']
        assert getattr(plan_to_copy, attribute_name) != getattr(TestPlan.objects.get(pk=copied_plan_id), attribute_name)

    def test_plan_not_keep_assignee(
        self,
        superuser_client,

        test_plan_factory,
        project,
        test_factory,
    ):
        plan_to_copy = test_plan_factory(project=project)
        test_to_copy = test_factory(plan=plan_to_copy)
        copied_plan_id = superuser_client.send_request(
            self.view_name_copy,
            request_type=RequestType.POST,
            data={
                'plans': [
                    {
                        'plan': plan_to_copy.pk,
                    },
                ],
                'keep_assignee': False,
            },
        ).json()[0]['id']
        copied_test = Test.objects.filter(plan__pk=copied_plan_id).first()
        assert test_to_copy.assignee != copied_test.assignee
        assert copied_test.assignee is None

    def test_plan_copying_to_itself(
        self,
        superuser_client,
        test_plan_factory,
        project,
    ):
        plan_to_copy = test_plan_factory(project=project)
        plan_payload = {
            'plan': plan_to_copy.pk,
        }
        superuser_client.send_request(
            self.view_name_copy,
            request_type=RequestType.POST,
            data={
                'plans': [plan_payload],
                'dst_plan': plan_to_copy.pk,
            },
            expected_status=HTTPStatus.OK,
        ).json()
        plan_to_copy.refresh_from_db()
        assert plan_to_copy.get_descendants(include_self=False).count()

    def test_copy_plan_not_keeping_comments(
        self,
        superuser_client,

        test_plan_factory,
        project,
        test_factory,
        comment_test_factory,
        comment_test_plan_factory,
    ):
        plan_to_copy = test_plan_factory(project=project)
        comment_test_plan_factory(content_object=plan_to_copy)
        test_to_copy = test_factory(plan=plan_to_copy)
        comment_test_factory(content_object=test_to_copy)
        copied_plan_id = superuser_client.send_request(
            self.view_name_copy,
            request_type=RequestType.POST,
            data={
                'plans': [
                    {
                        'plan': plan_to_copy.pk,
                    },
                ],
                'keep_assignee': False,
            },
        ).json()[0]['id']
        copied_plan = TestPlan.objects.get(pk=copied_plan_id)
        copied_test = Test.objects.filter(plan__pk=copied_plan_id).first()
        assert not copied_plan.comments.all()
        assert not copied_test.comments.all()

    @pytest.mark.parametrize(
        'attribute, attr_values, to_str',
        [
            ('run_id', ['first_value', 'second_value', 14], True),
            ('run_id', [125, 98, 14], False),
            ('run_id', ['125', '98', '14'], False),
        ],
        ids=['str attribute', 'decimal attribute', 'str as decimal attribute'],
    )
    def test_histogram_ordering(
        self,
        request,
        superuser_client,
        project,
        test_plan_factory,
        test_factory,
        test_result_factory,
        attribute,
        attr_values,
        to_str,
        result_status_factory,
    ):
        allure.dynamic.title(f'Test ordering histogram by {request.node.callspec.id}')
        test_plan = test_plan_factory(project=project)
        with allure.step('Create expected attribute ordering'):
            if to_str:
                expected_ordering = sorted(attr_values, key=str)
            else:
                expected_ordering = sorted(attr_values, key=int)
        with allure.step('Create test results with attributes'):
            for idx in range(len(attr_values)):
                test_result_factory(
                    test=test_factory(plan=test_plan, project=project),
                    status=result_status_factory(project=test_plan.project),
                    attributes={attribute: attr_values[idx]},
                    project=project,
                )
        content = superuser_client.send_request(
            self.view_name_histogram,
            reverse_kwargs={'pk': test_plan.id},
            query_params={
                'start_date': (timezone.now() - timezone.timedelta(days=1)).date(),
                'end_date': (timezone.now() + timezone.timedelta(days=1)).date(),
                'attribute': attribute,
            },
            expected_status=HTTPStatus.OK,
        ).json()
        with allure.step('Compare expected ordering with actual'):
            assert expected_ordering == [obj['point'] for obj in content], 'Wrong ordering'

    @allure.title('Test test plan creation with archived cases')
    def test_creation_with_archive_cases(
        self,
        superuser_client,
        project,
        test_case_factory,
    ):
        test_cases = [test_case_factory(is_archive=True).pk for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
        testplan_dict = {
            'name': 'Test plan',
            'due_date': constants.END_DATE,
            'started_at': constants.DATE,
            'test_cases': test_cases,
            'project': project.id,
        }
        response = superuser_client.send_request(
            self.view_name_list,
            testplan_dict,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        with allure.step('validate response'):
            assert TestPlanCasesValidator.err_msg.format(test_cases) in response.json()['errors']

    @allure.title('Test test plan labels endpoint')
    def test_testplan_labels(
        self,
        superuser_client,
        project,
        test_plan,
        test_case_factory,
        labeled_item_factory,
        test_factory,
    ):
        test_label_mapping = {}
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            case = test_case_factory(project=project)
            test = test_factory(plan=test_plan, case=case, project=project)
            test_label_mapping[test.id] = labeled_item_factory(content_object=case).label_id
        response_body = superuser_client.send_request(
            self.view_name_labels,
            reverse_kwargs={'pk': test_plan.id},
        ).json()
        assert len(response_body) == len(test_label_mapping)
        deleted_test_ids = list(test_label_mapping.keys())[:constants.NUMBER_OF_OBJECTS_TO_CREATE // 2]
        Test.objects.filter(pk__in=deleted_test_ids).delete()
        response_body = superuser_client.send_request(
            self.view_name_labels,
            reverse_kwargs={'pk': test_plan.id},
        ).json()
        for test_id, label_id in test_label_mapping.items():
            current_test = next((label for label in response_body if label['id'] == label_id), None)
            if test_id in deleted_test_ids:
                assert not current_test, 'Label from deleted list in response'
            else:
                assert current_test, 'Label not in response'

    @pytest.mark.parametrize('is_parametrized', [False, True], ids=['not parametrized', 'parametrized'])
    def test_plan_creation_with_custom_attributes(
        self,
        superuser_client,
        project,
        custom_attribute_factory,
        is_parametrized,
        request,
        parameter_factory,
    ):
        allure.dynamic.title(f'Test {request.node.callspec.id} plan creation with custom attributes')
        parameters_count = 3
        custom_attribute_name = 'awesome_attribute'
        custom_attribute_value = 'some_value'
        with allure.step('Create custom attribute'):
            custom_attribute_factory(
                project=project,
                name=custom_attribute_name,
                applied_to={
                    'testplan': {
                        'is_required': True,
                    },
                },
            )
        attributes = {custom_attribute_name: custom_attribute_value}
        payload = {
            'name': constants.TEST_PLAN_NAME,
            'project': project.id,
            'due_date': constants.END_DATE,
            'started_at': constants.DATE,
            'attributes': {custom_attribute_name: custom_attribute_value},
            'parameters': [parameter_factory().id for _ in range(parameters_count)] if is_parametrized else [],
        }
        superuser_client.send_request(self.view_name_list, payload, HTTPStatus.CREATED, RequestType.POST)
        with allure.step('Validate plan attributes'):
            for plan in TestPlan.objects.all():
                assert plan.attributes == attributes

    @pytest.mark.parametrize('is_parametrized', [False, True], ids=['not parametrized', 'parametrized'])
    def test_blank_required_attr_validation(
        self,
        superuser_client,
        project,
        custom_attribute_factory,
        is_parametrized,
        request,
        parameter_factory,
    ):
        allure.dynamic.title(f'Test {request.node.callspec.id} plan cannot be created with blank required attributes')
        parameters_count = 3
        custom_attribute_name = 'awesome_attribute'
        with allure.step('Create custom attribute'):
            custom_attribute_factory(
                project=project,
                name=custom_attribute_name,
                applied_to={
                    'testplan': {
                        'is_required': True,
                    },
                },
            )
        payload = {
            'name': constants.TEST_PLAN_NAME,
            'project': project.id,
            'due_date': constants.END_DATE,
            'started_at': constants.DATE,
            'attributes': {custom_attribute_name: ''},
            'parameters': [parameter_factory().id for _ in range(parameters_count)] if is_parametrized else [],
        }
        response = superuser_client.send_request(
            self.view_name_list,
            payload,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        with allure.step('Validate error message'):
            assert response.json()['errors'][0] == FOUND_EMPTY_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG.format(
                [custom_attribute_name],
            )

    @pytest.mark.parametrize('is_parametrized', [False, True], ids=['not parametrized', 'parametrized'])
    def test_required_attr_not_provided(
        self,
        superuser_client,
        project,
        custom_attribute_factory,
        is_parametrized,
        request,
        parameter_factory,
    ):
        allure.dynamic.title(f'Test {request.node.callspec.id} plan cannot be created without required attributes')
        parameters_count = 3
        with allure.step('Generate custom attribute'):
            custom_attribute = custom_attribute_factory(
                project=project,
                applied_to={
                    'testplan': {
                        'is_required': True,
                    },
                },
            )
        payload = {
            'name': constants.TEST_PLAN_NAME,
            'project': project.id,
            'due_date': constants.END_DATE,
            'started_at': constants.DATE,
            'attributes': {},
            'parameters': [parameter_factory().id for _ in range(parameters_count)] if is_parametrized else [],
        }
        response = superuser_client.send_request(
            self.view_name_list,
            payload,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        with allure.step('Validate error message'):
            assert response.json()['errors'][0] == MISSING_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG.format(
                [custom_attribute.name],
            )

    @pytest.mark.parametrize('attribute_key', ['attributes', 'any_attributes'], ids=['attributes', 'any_attributes'])
    def test_searching_by_attr_key(
        self,
        superuser_client,
        test_plan_factory,
        project,
        attribute_key,
        request,
    ):
        allure.dynamic.title(f'Test plans searching by attribute key with query {request.node.callspec.id}')
        plans = {
            'attr_1': [],
            'attr_2': [],
        }
        all_combinations = set()
        attr_names = list(plans.keys())
        with allure.step('Generate attribute combinations'):
            for r in range(1, len(attr_names) + 1):
                for combo in itertools.combinations(attr_names, r):
                    all_combinations.add(combo)

        with allure.step('Create test plans with attrs'):
            for attr_name in attr_names:
                for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
                    test_plan = test_plan_factory(project=project, attributes={attr_name: 1})
                    plans[attr_name].append(test_plan.id)

        with allure.step('Validate plan searching by attribute combinations'):
            for combo in all_combinations:
                response = superuser_client.send_request(
                    self.view_name_list,
                    query_params={'project': project.id, attribute_key: ','.join(combo)},
                )
                if len(combo) == 1:
                    for plan in response.json()['results']:
                        assert plan['id'] in plans[combo[0]]
                else:
                    number_of_plans = (
                        len(attr_names) * constants.NUMBER_OF_OBJECTS_TO_CREATE
                        if attribute_key == 'any_attributes' else 0
                    )
                    assert response.json()['count'] == number_of_plans

    def test_plan_union(self, test_plan_factory, test_factory, project, authorized_superuser_client):
        roots = []
        child_plans = defaultdict(list)
        for _ in range(3):
            plan = test_plan_factory(project=project)
            child_plan = model_to_dict_via_serializer(
                test_plan_factory(project=project, parent=plan),
                TestPlanUnionMockSerializer,
                refresh_instances=True,
            )
            child_test = model_to_dict_via_serializer(
                test_factory(project=project, plan=plan),
                TestUnionMockSerializer,
                refresh_instances=True,
            )
            child_plans[plan.pk].append(child_plan)
            child_plans[plan.pk].append(child_test)
            roots.append(plan)
        for root in roots:
            parent_id = root.pk
            response_data = authorized_superuser_client.send_request(
                self.view_name_union,
                query_params={'parent': parent_id, 'project': project.pk},
            ).json_strip()
            assert child_plans[parent_id] == response_data

    @pytest.mark.parametrize('descending', [True, False], ids=['Descending', 'Ascending'])
    @pytest.mark.parametrize('order_by', ['id', 'started_at', 'created_at', 'name', 'assignee_username', 'suite_path'])
    def test_plan_union_order_by_filter(
        self,
        test_plan_factory,
        test_factory,
        project,
        authorized_superuser_client,
        order_by,
        descending,
        user_factory,
        test_case_factory,
        test_suite_factory,
    ):
        title = f'Validate union endpoint using order by {order_by} {"descending" if descending else "ascending"}'
        allure.dynamic.title(title)
        started_at = timezone.now()
        root_plan = test_plan_factory(project=project, started_at=started_at)
        expected_plans = []
        with allure.step('Generate and sort plans'):
            for idx in range(3):
                started_at += timedelta(hours=1)
                plan = model_to_dict_via_serializer(
                    test_plan_factory(project=project, parent=root_plan, name=str(idx), started_at=started_at),
                    TestPlanUnionMockSerializer,
                    refresh_instances=True,
                )
                expected_plans.append(plan)
            expected_plans.sort(key=lambda elem: elem.get(order_by, elem['id']), reverse=descending)
        with allure.step('Generate and sort tests'):
            expected_tests = []
            for idx in range(3):
                suite = test_suite_factory(name=str(idx))
                test = model_to_dict_via_serializer(
                    test_factory(
                        case=test_case_factory(name=str(idx), suite=suite),
                        project=project,
                        plan=root_plan,
                        assignee=user_factory(username=str(idx)),
                    ),
                    TestUnionMockSerializer,
                    refresh_instances=True,
                )
                expected_tests.append(test)
            expected_tests.sort(key=lambda elem: elem.get(order_by, elem['id']), reverse=descending)
        expected_plans.extend(expected_tests)
        response_data = authorized_superuser_client.send_request(
            self.view_name_union,
            query_params={
                'project': project.pk,
                'parent': root_plan.pk,
                'ordering': f'-{order_by},-id' if descending else f'{order_by},id',
            },
        ).json_strip()
        with allure.step('Validate ordering'):
            assert expected_plans == response_data

    @allure.title('Test plan union search filter')
    def test_plan_union_search(
        self,
        test_plan_factory,
        test_factory,
        project,
        authorized_superuser_client,
        test_case_factory,
    ):
        found_name = 'Cat plan'
        root_plan = test_plan_factory(project=project)
        found_plan = test_plan_factory(project=project, parent=root_plan, name=found_name)
        container_plan = test_plan_factory(project=project, parent=root_plan)
        test_plan_factory(project=project, parent=container_plan, name=found_name)
        expected_data = [
            model_to_dict_via_serializer(
                found_plan,
                TestPlanUnionMockSerializer,
                refresh_instances=True,
            ),
            model_to_dict_via_serializer(
                container_plan,
                TestPlanUnionMockSerializer,
                refresh_instances=True,
            ),
            model_to_dict_via_serializer(
                test_factory(project=project, plan=root_plan, case=test_case_factory(name=found_name)),
                TestUnionMockSerializer,
                refresh_instances=True,
            ),
        ]
        response_data = authorized_superuser_client.send_request(
            self.view_name_union,
            query_params={
                'project': project.pk,
                'parent': root_plan.pk,
                'treesearch': found_name,
                'ordering': 'id',
            },
        ).json_strip()
        with allure.step('Validate expected data'):
            assert expected_data == response_data

    @allure.title('Test labels filter on test plan union')
    @pytest.mark.parametrize(
        'label_indexes, not_labels_indexes, labels_condition, number_of_items',
        [
            ((0, 1), None, 'or', 7),
            ((0, 1), None, 'and', 2),
            ((0,), (1,), 'or', 8),
            ((0,), (1,), 'and', 3),
            ((0, 2), (1,), 'or', 8),
            ((0, 2), (1,), 'and', 0),
            (None, (0,), 'or', 5),
            (None, (0, 1), 'or', 8),
            (None, (0, 1), 'and', 3),
        ],
    )
    def test_union_plan_filter_by_labels(
        self,
        authorized_superuser_client,
        cases_with_labels,
        label_indexes,
        not_labels_indexes,
        labels_condition,
        number_of_items,
        project,
        test_plan_factory,
    ):
        labels, _, test_plan, _ = cases_with_labels
        query_params = {'parent': test_plan.id, 'project': project.id}
        if label_indexes:
            query_params['labels'] = ','.join([str(labels[i].id) for i in label_indexes])
        if not_labels_indexes:
            query_params['not_labels'] = ','.join([str(labels[i].id) for i in not_labels_indexes])
        query_params['labels_condition'] = labels_condition
        with allure.step('Send get request with label filter to union endpoint'):
            content = authorized_superuser_client.send_request(
                self.view_name_union,
                query_params=query_params,
            ).json()
        with allure.step('Validate number of tests'):
            assert content.get('count') == number_of_items
        with allure.step('Move plans to deeper nesting to validate nested filtering works'):
            root_plan = test_plan_factory(project=project)
            found_plan = test_plan_factory(project=project, parent=root_plan)
            test_plan_factory(project=project, parent=root_plan)
            test_plan.parent = found_plan
            test_plan.save()
        with allure.step('Send request after nesting data deeper'):
            query_params['parent'] = root_plan.pk
            content = authorized_superuser_client.send_request(
                self.view_name_union,
                query_params=query_params,
            ).json()
        with allure.step('Validate number of plans'):
            if number_of_items:
                assert content.get('count') == 1
            else:
                assert content.get('count') == 0

    def test_union_filter_by_status(
        self,
        authorized_superuser_client,
        test_plan_factory,
        project,
        test_factory,
        test_result_factory,
        result_status_factory,
    ):
        root_plan = test_plan_factory(project=project)
        found_status = result_status_factory()
        not_found_status = result_status_factory()

        found_plan = test_plan_factory(project=project, parent=root_plan)
        found_test = test_factory(project=project, plan=root_plan)

        nested_test = test_factory(project=project, plan=found_plan)
        test_result_factory(test=found_test, status=found_status, project=project)
        test_result_factory(test=nested_test, status=found_status, project=project)

        expected_data = [
            model_to_dict_via_serializer(
                found_plan,
                TestPlanUnionMockSerializer,
                refresh_instances=True,
            ),
            model_to_dict_via_serializer(
                found_test,
                TestUnionMockSerializer,
                refresh_instances=True,
            ),
        ]

        for _ in range(3):
            test = test_factory(project=project, plan=root_plan)
            test_result_factory(project=project, test=test, status=not_found_status)

        for _ in range(3):
            test_plan_factory(parent=root_plan, project=project)

        content = authorized_superuser_client.send_request(
            self.view_name_union,
            query_params={'project': project.pk, 'parent': root_plan.pk, 'last_status': found_status.pk},
        ).json_strip()
        assert expected_data == content

    @allure.title('Test plans statistic for whole project')
    def test_whole_project_statistics(
        self,
        superuser_client,
        project,
        test_plan_factory,
        test_factory,
        test_case_factory,
        test_result_factory,
        result_status_factory,
    ):
        len_plans = 3
        test_plans = [test_plan_factory(project=project) for _ in range(len_plans)]
        number_of_statuses = {
            0: 6,
            1: 12,
            2: 3,
            3: 10,
            4: 0,
            5: 1,
            6: 15,
            7: 1,
        }
        estimates = {
            1: 60,
            2: 3600,
            5: 57780,
        }
        estimates_in_minutes = {
            1: 1.0,
            2: 60.0,
            5: 963.0,
        }
        statuses = [result_status_factory(project=project) for _ in range(len(number_of_statuses))]
        for status_key, status in enumerate(statuses):
            for idx in range(number_of_statuses[status_key]):
                estimate = estimates.get(status_key, None)
                test_case = test_case_factory(estimate=estimate, project=project)

                if idx % 2 == 0:
                    test_result_factory(
                        test=test_factory(plan=test_plans[idx % len_plans], case=test_case, project=project),
                        status=status,
                        project=project,
                    )
                else:
                    test_result_factory(
                        test=test_factory(plan=test_plans[idx % len_plans], case=test_case, project=project),
                        status=status,
                        is_archive=True,
                        project=project,
                    )
        response_body = superuser_client.send_request(
            self.view_name_project_statistics,
            query_params={'project': project.id},
        ).json()
        label_to_stat = {}
        estimates_to_stat = {}
        empty_estimates = {}
        colors = {}
        for elem in response_body:
            for dict_obj, key in zip(
                [label_to_stat, estimates_to_stat, empty_estimates, colors],
                ['value', 'estimates', 'empty_estimates', 'color'],
            ):
                dict_obj[elem['label'].lower()] = elem[key]
        for status_key, status in enumerate(statuses):
            if not number_of_statuses[status_key] and status.name.lower() not in label_to_stat:
                continue
            with allure.step(f'Validate number of statuses for {status_key}'):
                assert number_of_statuses[status_key] == label_to_stat[status.name.lower()], f'Statistics for ' \
                                                                                             f'{status.name} is wrong'
                assert status.color == colors[status.name.lower()], f'Wrong color of status {status.name}'
                if status_key not in estimates:
                    assert empty_estimates[status.name.lower()] == label_to_stat[status.name.lower()], \
                        'Wrong empty estimates'
                    assert estimates_to_stat[status.name.lower()] == 0, f'Incorrect estimate for status {status.name}'
                else:
                    assert empty_estimates[status.name.lower()] == 0, 'Estimates is more than 0'
                    expected = estimates_in_minutes[status_key] * number_of_statuses[status_key]
                    assert estimates_to_stat[status.name.lower()] == expected, \
                        f'Estimate not equal for status {status.name}'

    @pytest.mark.parametrize(
        'attribute, attr_values',
        [
            (None, None),
            ('run_id', ['first_value', 'second_value']),
        ],
        ids=['by date', 'by attribute'],
    )
    def test_whole_project_histogram(
        self,
        superuser_client,
        test_plan_factory,
        test_factory,
        test_result_factory,
        attribute,
        request,
        attr_values,
        project,
        result_status_factory,
    ):
        len_plans = 3
        allure.dynamic.title(f'Test histogram aggregation {request.node.callspec.id}')
        test_plans = [test_plan_factory(project=project) for _ in range(len_plans)]
        number_of_statuses = {
            0: 6,
            1: 12,
            2: 4,
            3: 10,
            4: 0,
            6: 16,
            7: 1,
            8: 11,
        }
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=1)
        if attribute:
            expected_results = [{'point': attr_value} for attr_value in attr_values]
        else:
            expected_results = [
                {'point': start_date.strftime('%Y-%m-%d')},
                {'point': end_date.strftime('%Y-%m-%d')},
            ]
        statuses = list(ResultStatusSelector().status_list_raw())
        statuses.extend([
            result_status_factory(project=project)
            for _ in range(len(number_of_statuses) - len(statuses))
        ])
        for status_key, status in zip(number_of_statuses, statuses):
            count = int(number_of_statuses[status_key] / 2)
            for idx in range(count):
                attributes = {attribute: attr_values[0]} if attribute else {}
                test_result_factory(
                    test=test_factory(plan=test_plans[idx % len_plans], project=project),
                    status=status,
                    created_at=start_date,
                    project=project,
                    attributes=attributes,
                )
            expected_results[0][status.pk] = {
                'label': status.name.lower(),
                'color': status.color,
                'count': count,
            }
            for idx in range(count):
                attributes = {attribute: attr_values[1]} if attribute else {}
                test_result_factory(
                    test=test_factory(plan=test_plans[idx % len_plans], project=project),
                    status=status,
                    created_at=end_date,
                    attributes=attributes,
                    project=project,
                )
            expected_results[1][status.pk] = {
                'label': status.name.lower(),
                'color': status.color,
                'count': count,
            }
        query_params = {
            'start_date': start_date.date(),
            'end_date': end_date.date(),
            'attribute': attribute if attribute else '',
            'project': project.pk,
        }
        content = superuser_client.send_request(
            self.view_name_project_histogram,
            query_params=query_params,
            expected_status=HTTPStatus.OK,
        ).json()
        assert len(expected_results) == len(content), 'Expected result did not match result'
        for idx in range(len(expected_results)):
            for key, value in expected_results[idx].items():
                point = expected_results[idx]['point']
                value_from_response = content[idx][str(key)]
                assert value == value_from_response, (
                    f'Expect in point = {point}, '
                    f'{key} = {value}, get value = {value_from_response}'
                )

    @pytest.mark.parametrize('search_param', ('search', 'treesearch'), ids=['search param', 'treesearch param'])
    def test_tree_search_and_search(
        self,
        authorized_superuser_client,
        test_plan_factory,
        project,
        search_param,
    ):
        allure.dynamic.title(f'Search test plan by {search_param}')
        search_name = 'search_name'
        parent_test_plan = test_plan_factory(project=project)
        child_test_plan = test_plan_factory(project=project, parent=parent_test_plan, name=search_name)
        if search_param == 'treesearch':
            query_params = {search_param: search_name, 'parent': 'null'}
            search_id = parent_test_plan.id
        else:
            query_params = {search_param: search_name}
            search_id = child_test_plan.id
        actual_test_plans = authorized_superuser_client.send_request(
            self.view_name_list,
            query_params={'project': project.id, 'ordering': 'id', **query_params},
        ).json_strip(as_json=False)
        assert len(actual_test_plans) == 1, 'Found extra plan'
        assert actual_test_plans[0]['id'] == search_id, 'Found incorrect plan'

    @classmethod
    @allure.step('Validate copied objects')
    def _validate_copied_objects(
        cls,
        src_instances: list[Any],
        copied_instances: list[Any],
        excluded_fields: Iterable[str],
    ) -> None:
        err_msg = 'Value for field {0} did not change for instance {1}'
        assert len(src_instances) == len(copied_instances)
        for src_instance, copied_instance in zip(src_instances, copied_instances):
            src_data = model_to_dict(src_instance, exclude=excluded_fields)
            copied_data = model_to_dict(copied_instance, exclude=excluded_fields)
            assert src_data == copied_data, f'Invalid data copied for {type(src_instance[0])}'

        for src_instance, copied_instance in zip(src_instances, copied_instances):
            for field in excluded_fields:
                src_val = getattr(src_instance, field)
                copied_val = getattr(copied_instance, field)
                if src_val is None:
                    continue
                assert src_val != copied_val, err_msg.format(field, type(src_instance[0]))

    @classmethod
    def _label_query_params(cls, label_names: Iterable[str]) -> str:
        return ','.join(map(str, Label.objects.filter(name__in=label_names).values_list('id', flat=True)))

    @allure.step('Limit testplans by only expected and their ancestors')
    @classmethod
    def _get_search_qs_by_expected(cls, expected_plans: Iterable[TestPlan]) -> QuerySet[TestPlan]:
        pref_qs = TestPlan.objects.filter(pk__in=(plan.id for plan in expected_plans)).get_ancestors(include_self=True)
        max_level = get_max_level(TestPlan)
        return deepcopy(pref_qs).filter(parent=None).prefetch_related(
            *form_tree_prefetch_objects(
                'child_test_plans',
                'child_test_plans',
                max_level,
                queryset=pref_qs,
            ),
        )
