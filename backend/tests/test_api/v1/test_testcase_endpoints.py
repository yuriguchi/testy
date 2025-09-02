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
import re
from copy import deepcopy
from http import HTTPStatus

import allure
import pytest
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from tests import constants
from tests.commons import CustomAPIClient, RequestType, model_to_dict_via_serializer
from tests.error_messages import (
    FORBIDDEN_USER_TEST_CASE,
    FOUND_EMPTY_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG,
    INVALID_ESTIMATE_ERR_MSG,
    MISSING_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG,
    NEGATIVE_ESTIMATE_ERR_MSG,
    REQUIRED_FIELD_MSG,
    TOO_BIG_ESTIMATE_ERR_MSG,
    WEEK_ESTIMATE_ERR_MSG,
)
from tests.mock_serializers.v1 import TestCaseMockSerializer, TestMockSerializer
from testy.core.models import Attachment, Label, LabeledItem
from testy.tests_description.api.v1.serializers import TestCaseHistorySerializer
from testy.tests_description.models import TestCase, TestCaseStep

_ERRORS = 'errors'


@pytest.mark.django_db(reset_sequences=True)
@allure.parent_suite('Test cases')
@allure.suite('Integration tests')
@allure.sub_suite('Endpoints')
class TestCaseEndpoints:
    view_name_detail = 'api:v1:testcase-detail'
    view_name_list = 'api:v1:testcase-list'
    view_name_copy = 'api:v1:testcase-copy'
    view_name_history = 'api:v1:testcase-history'
    view_name_tests = 'api:v1:testcase-tests'
    view_restore_version = 'api:v1:testcase-restore-version'
    view_name_search = 'api:v1:testcase-search'
    view_name_delete_preview = 'api:v1:testcase-delete-preview'

    @allure.title('Test list display')
    def test_list(self, superuser_client, test_case_factory, project):
        ids = [test_case_factory(project=project).id for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
        expected = model_to_dict_via_serializer(
            TestCase.objects.filter(pk__in=ids),
            TestCaseMockSerializer,
            many=True,
            as_json=True,
        )
        response = superuser_client.send_request(self.view_name_list, query_params={'project': project.id})
        with allure.step('Validate response body'):
            assert response.json_strip(as_json=True) == expected

    @pytest.mark.parametrize('is_archive', [True, False], ids=['Archived case', 'Case'])
    def test_retrieve(self, request, superuser_client, test_case_factory, is_archive):
        allure.dynamic.title(f'Test retrive {request.node.callspec.id}')
        test_case = test_case_factory(is_archive=is_archive)
        expected_dict = model_to_dict_via_serializer(
            test_case,
            TestCaseMockSerializer,
            as_json=True,
        )
        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_case.pk},
        ).json_strip(as_json=True, is_paginated=False)
        with allure.step('Validate response body'):
            assert response == expected_dict, 'Actual model dict is different from expected'

    @pytest.mark.parametrize('is_archive', [0, 1], ids=['Test cases search', 'Test cases search with archive'])
    def test_cases_search(
        self,
        request,
        authorized_superuser_client: CustomAPIClient,
        test_case_factory,
        project,
        test_suite,
        is_archive,
    ):
        allure.dynamic.title(f'Test {request.node.callspec.id}')
        name_to_find = 'Cat can walk {0}'
        name_to_skip = 'Dog can bark'

        with allure.step('Generate instances to find'):
            for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
                test_case_factory(project=project, name=name_to_find.format(idx), suite=test_suite)

        with allure.step('Generate instance to skip'):
            test_case_factory(project=project, name=name_to_skip, suite=test_suite)

        with allure.step('Generate archived instances to validate they are not displayed'):
            test_case_factory(project=project, name=name_to_find.format(0), suite=test_suite, is_archive=True)
            test_case_factory(project=project, name=name_to_find.format(1), suite=test_suite, is_deleted=True)

        response_body = authorized_superuser_client.send_request(
            self.view_name_search,
            query_params={'search': 'cat', 'project': project.pk, 'is_archive': is_archive},
        ).json()
        expected_count = constants.NUMBER_OF_OBJECTS_TO_CREATE + is_archive
        with allure.step('Validate response body'):
            assert expected_count == len(response_body[0].get('test_cases')), 'Found more cases than expected'

    @allure.title('Test case creation')
    def test_creation(self, superuser_client, project, test_suite):
        expected_number_of_cases = 1
        case_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
            'suite': test_suite.id,
            'setup': constants.SETUP,
            'scenario': constants.SCENARIO,
            'teardown': constants.TEARDOWN,
            'estimate': constants.INPUT_ESTIMATE,
        }
        superuser_client.send_request(self.view_name_list, case_dict, HTTPStatus.CREATED, RequestType.POST)
        with allure.step('Validate object was created'):
            assert TestCase.objects.count() == expected_number_of_cases, f'Expected number of cases ' \
                                                                         f'"{expected_number_of_cases}"' \
                                                                         f'actual: "{TestCase.objects.count()}"'

    @pytest.mark.parametrize(
        'request_type',
        [RequestType.PATCH, RequestType.PUT],
        ids=['partial update', 'update'],
    )
    def test_update(self, superuser_client, test_case, request_type, request):
        allure.dynamic.title(f'Test {request.node.callspec.id}')
        new_name = 'new_expected_test_case_name'
        case_dict = {
            'id': test_case.id,
            'name': new_name,
            'project': test_case.project.id,
            'suite': test_case.suite.id,
            'scenario': test_case.scenario,
        }
        expected_count_versions = TestCase.objects.get(pk=test_case.id).history.count() + 1
        superuser_client.send_request(
            self.view_name_detail,
            case_dict,
            request_type=RequestType.PUT,
            reverse_kwargs={'pk': test_case.pk},
        )
        actual_name = TestCase.objects.get(pk=test_case.id).name
        with allure.step('Validate version created'):
            assert TestCase.objects.get(pk=test_case.id).history.count() == expected_count_versions
        with allure.step('Validate name was updated'):
            assert actual_name == new_name, f'Names do not match. Expected name "{actual_name}", actual: "{new_name}"'

    @allure.title('Test fields are required on update')
    def test_required_fields_on_update(self, superuser_client, test_case):
        new_name = 'new_expected_test_case_name'
        case_dict = {
            'id': test_case.id,
            'name': new_name,
        }
        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_case.pk},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.BAD_REQUEST,
            data=case_dict,
        )
        with allure.step('Validate error messages'):
            assert response.json()['project'][0] == REQUIRED_FIELD_MSG
            assert response.json()['suite'][0] == REQUIRED_FIELD_MSG
            assert response.json()['scenario'][0] == REQUIRED_FIELD_MSG

    @allure.title('Test deletion')
    def test_delete(self, superuser_client, test_case):
        with allure.step('Validate object was created'):
            assert TestCase.objects.count() == 1, 'Test case was not created'
        superuser_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': test_case.pk},
        )
        with allure.step('Validate object was deleted'):
            assert not TestCase.objects.count(), f'TestCase with id "{test_case.id}" was not deleted.'

    @pytest.mark.parametrize(
        'time_value, expected_value', [
            ('123', '2h 3m'),
            ('1d 1h 1m 1s', '1d 1h 1m 1s'),
            ('2:04:13:02.266', '2d 4h 13m 2s'),
            ('2 days, 4:13:02', '2d 4h 13m 2s'),
            ('2 days, 4:13:02.266', '2d 4h 13m 2s'),
            ('5hr34m56s', '5h 34m 56s'),
            ('5 hours, 34 minutes, 56 seconds', '5h 34m 56s'),
            ('365d', '365d'),
            ('366d', '366d'),
            (None, None),
        ],
    )
    def test_estimate_field_inputs(
        self,
        superuser_client,
        project,
        test_suite,
        time_value,
        expected_value,
    ):
        allure.dynamic.title(f'Test estimate field valid input {time_value}')
        case_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
            'suite': test_suite.id,
            'setup': constants.SETUP,
            'scenario': constants.SCENARIO,
            'teardown': constants.TEARDOWN,
            'estimate': time_value,
        }
        response = superuser_client.send_request(self.view_name_list, case_dict, HTTPStatus.CREATED, RequestType.POST)
        content = response.json()
        with allure.step('Validate estimate field formatting'):
            assert content['estimate'] == expected_value
        with allure.step('Validate estimate value'):
            if time_value:
                assert isinstance(TestCase.objects.get(pk=content['id']).estimate, int)

    @pytest.mark.parametrize(
        'time_value, error_message', [
            ('abc', INVALID_ESTIMATE_ERR_MSG),
            ('-123', NEGATIVE_ESTIMATE_ERR_MSG),
            ('-2d', NEGATIVE_ESTIMATE_ERR_MSG),
            ('1231241123112312312314124121', TOO_BIG_ESTIMATE_ERR_MSG),
            ('1w 1d', WEEK_ESTIMATE_ERR_MSG),
            ('1 week 1 day', WEEK_ESTIMATE_ERR_MSG),
            ('1.6 weeks 1 day', WEEK_ESTIMATE_ERR_MSG),
        ],
    )
    def test_estimate_invalid_input(
        self,
        superuser_client,
        project,
        test_suite,
        time_value,
        error_message,
    ):
        allure.dynamic.title(f'Test estimate field invalid input {time_value}')
        case_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
            'suite': test_suite.id,
            'setup': constants.SETUP,
            'scenario': constants.SCENARIO,
            'teardown': constants.TEARDOWN,
            'estimate': time_value,
        }
        response = superuser_client.send_request(
            self.view_name_list,
            case_dict,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        with allure.step('Validate error message'):
            assert response.json()[_ERRORS][0] == error_message

    @pytest.mark.parametrize(
        'user_fixture',
        ['superuser', 'user'],
        ids=['superuser', 'user'],
    )
    def test_cases_copy(
        self,
        request,
        api_client,
        test_case_factory,
        project,
        test_suite,
        membership_factory,
        member,
        user_fixture,
    ):
        allure.dynamic.title(f'Test cases copy from {request.node.callspec.id}')
        user = request.getfixturevalue(user_fixture)
        membership_factory(project=project, user=user, role=member)
        api_client.force_login(user)
        case1 = test_case_factory(project=project, suite=test_suite)
        case2 = test_case_factory(project=project, suite=test_suite)
        api_client.send_request(
            self.view_name_copy,
            data={
                'cases': [{'id': case1.id}, {'id': case2.id}],
                'dst_suite_id': test_suite.id,
            },
            request_type=RequestType.POST,
        )
        with allure.step('Validate suites copied'):
            assert TestCase.objects.filter(suite=test_suite).count() == 4

    @classmethod
    @allure.step('Set attachment references')
    def set_attachment_references(cls, instance: Model, fields: list[str], attachments_reference_to_change: str):
        for field in fields:
            setattr(
                instance,
                field,
                attachments_reference_to_change.format(
                    Attachment.objects.get(
                        content_type=ContentType.objects.get_for_model(type(instance)),
                        object_id=instance.id,
                    ).id,
                ),
            )
            instance.save()

    @pytest.mark.django_db(reset_sequences=True)
    @pytest.mark.parametrize(
        'factory_name, is_steps',
        [
            ('test_case_with_steps_factory', True),
            ('test_case_factory', False),
        ],
        ids=['steps enabled', 'steps disabled'],
    )
    def test_case_copy_with_relations_copy(
        self,
        superuser_client,
        attachment_factory,
        request,
        project,
        test_suite_factory,
        labeled_item_factory,
        factory_name,
        is_steps,
        label_factory,
    ):
        allure.dynamic.title(f'Test cases copy with related objects {request.node.callspec.id}')
        fields = ['setup', 'scenario', 'expected', 'description', 'teardown']
        case_factory = request.getfixturevalue(factory_name)
        attachments_reference_to_change = '/attachments/{0}/ Some cute cat description /attachments/4444/'
        replacement_case_name = 'Replacement case name'
        case1 = case_factory(project=project)
        case2 = case_factory(project=project)
        test_suite = test_suite_factory(project=project)
        src_instances = [case1, case2]
        for case in src_instances:
            with allure.step(f'Create relations for {case.name}'):
                # Generate generic relations
                with allure.step('Create labeled items'):
                    labeled_item_factory(content_object=case, label=label_factory(project=project))
                with allure.step('Create attachments'):
                    attachment_factory(content_object=case)
                # Set attachment references in fields where it can be done
                with allure.step('Set attachment references in text fields'):
                    self.set_attachment_references(case, fields, attachments_reference_to_change)

        with allure.step('Create attachments and related objects for steps'):
            for step in TestCaseStep.objects.all():
                attachment_factory(content_object=step)
                self.set_attachment_references(step, ['scenario', 'expected'], attachments_reference_to_change)
        # check number of objects before copying
        with allure.step('Validate no cases in suite before copying'):
            assert not TestCase.objects.filter(suite=test_suite).count()
        if is_steps:
            with allure.step('Validate number of steps'):
                assert TestCaseStep.objects.count() == constants.NUMBER_OF_OBJECTS_TO_CREATE * 2
        src_cases = model_to_dict_via_serializer(
            src_instances,
            TestCaseMockSerializer,
            nested_fields=['steps', 'labels'],
            many=True,
        )
        copied_cases = superuser_client.send_request(
            self.view_name_copy,
            data={
                'cases': [{'id': case1.id, 'new_name': replacement_case_name}, {'id': case2.id}],
                'dst_suite_id': test_suite.id,
            },
            request_type=RequestType.POST,
        ).json()
        # check number of objects after copying
        expected_number_of_cases = 4
        with allure.step('Validate number of cases after copying'):
            assert TestCase.objects.filter(suite=test_suite).count() == 2
        if is_steps:
            with allure.step('Validate number of steps after copying'):
                assert TestCaseStep.objects.count() == constants.NUMBER_OF_OBJECTS_TO_CREATE * expected_number_of_cases
        with allure.step('Validate number of labeled items'):
            assert LabeledItem.objects.count() == expected_number_of_cases
        with allure.step('Validate labeled items history_id'):
            history_ids = TestCase.history.filter(suite=test_suite).values_list('history_id', flat=True)
            assert LabeledItem.objects.filter(content_object_history_id__in=history_ids).exists()
        with allure.step('Validate number of labels'):
            assert Label.objects.count() == 2
        with allure.step('Validate replacement name for case'):
            assert copied_cases[0]['name'] == replacement_case_name
        with allure.step('Validate name for case without replacement name'):
            assert copied_cases[1]['name'] == src_cases[1]['name']
        for expected_case, actual_case in zip(src_cases, copied_cases):
            # validate copied contents that should not change
            with allure.step('Validate labels did not change'):
                assert expected_case['labels'] == actual_case['labels']
            with allure.step('Validate estimate did not change'):
                assert expected_case['estimate'] == actual_case['estimate']
            # validate copied fields that should be created from start
            assert expected_case['id'] == expected_case['id']
            assert expected_case['attachments'] != actual_case['attachments']
            # validate attachments reference changed on copy
            with allure.step('Validate attachment reference changed on copy'):
                for field_name in fields:
                    assert expected_case[field_name] != actual_case[field_name]
                    assert re.match(attachments_reference_to_change.format(r'\d+'), actual_case[field_name])
            # validate new steps created
            with allure.step('Validate steps are copied'):
                for expected_step, actual_step in zip(expected_case.get('steps', {}), actual_case.get('steps', {})):
                    assert expected_step['name'] == actual_step['name']
                    assert expected_step['id'] != actual_step['id']
                    # validate attachments reference in steps are changed
                    for key in ['scenario', 'expected']:
                        assert expected_step[key] != actual_step[key]
                        assert re.match(attachments_reference_to_change.format(r'\d+'), actual_step[key])

    @allure.title('Copy cases to another project forbidden')
    def case_copy_to_another_project_forbidden(
        self,
        superuser_client,
        project,
        test_suite,
        test_case_factory,
    ):
        case1 = test_case_factory(project=project)
        case2 = test_case_factory(project=project)
        src_instances = [case1, case2]
        # check number of objects before copying
        with allure.step('Validate no cases in suite before copying'):
            assert not TestCase.objects.filter(suite=test_suite).count()
        for instance in src_instances:
            with allure.step(f'Validate suite and case {instance.pk} have different projects'):
                assert instance.project.pk != test_suite.project.pk
        response_body = superuser_client.send_request(
            self.view_name_copy,
            data={
                'cases': [{'id': case1.id}, {'id': case2.id}],
                'dst_suite_id': test_suite.id,
            },
            expected_status=HTTPStatus.BAD_REQUEST,
            request_type=RequestType.POST,
        ).json()
        with allure.step('Validate error message'):
            assert response_body['detail'] == 'Cannot copy case to another project.'

    @allure.title('Test history is created')
    def test_history_create(self, superuser_client, project, test_suite, superuser):
        create_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
            'suite': test_suite.id,
            'setup': constants.SETUP,
            'scenario': constants.SCENARIO,
            'teardown': constants.TEARDOWN,
            'estimate': constants.INPUT_ESTIMATE,
        }
        response = superuser_client.send_request(self.view_name_list, create_dict, HTTPStatus.CREATED, RequestType.POST)
        case_id = response.json()['id']
        response = superuser_client.send_request(
            self.view_name_history,
            reverse_kwargs={'pk': case_id},
        )
        content = response.json()['results']
        with allure.step('Get history by case_id'):
            case_history_manager = TestCase.objects.get(pk=case_id).history
        expected_list = model_to_dict_via_serializer(
            case_history_manager.all(),
            TestCaseHistorySerializer,
            many=True,
        )
        with allure.step('Validate history content'):
            assert len(content) == len(expected_list), 'Extra histories for test case'
            history, *_ = content  # noqa: WPS472
            assert history['user']['username'] == superuser.username, 'Users did not match'
            assert history['action'] == expected_list[0]['action'], f'Wrong action {history["action"]}'

    @allure.title('Test extra history added')
    def test_history_update(self, superuser_client, test_case, project, test_suite):
        new_name = 'new_expected_test_case_name'
        case_dict = {
            'id': test_case.id,
            'name': new_name,
            'project': project.id,
            'suite': test_suite.id,
            'scenario': constants.SCENARIO,
        }

        superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_case.pk},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
            data=case_dict,
        )
        response = superuser_client.send_request(
            self.view_name_history,
            reverse_kwargs={'pk': test_case.id},
        )
        content = response.json()['results']
        with allure.step('Get history by case_id'):
            case_history_manager = TestCase.objects.get(pk=test_case.id).history
        expected_list = model_to_dict_via_serializer(
            case_history_manager.all().order_by('-history_id'),
            TestCaseHistorySerializer,
            many=True,
        )
        with allure.step('Validate history instances'):
            assert case_history_manager.count() == case_history_manager.count(), 'Histories did not match'
            for actual_elem, expected_elem in zip(content, expected_list):
                assert actual_elem == expected_elem

    @allure.title('Test list display by case')
    def test_list_tests(self, superuser_client, test_case, test_plan_factory, test_factory):
        plan = test_plan_factory()
        expected_dict = model_to_dict_via_serializer(
            [
                test_factory(
                    project=test_case.project,
                    case=test_case,
                    plan=plan,
                ) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)
            ],
            TestMockSerializer,
            many=True,
        )
        content = superuser_client.send_request(
            self.view_name_tests,
            reverse_kwargs={'pk': test_case.pk},
        ).json()['results']
        assert len(content) == len(expected_dict), 'Lengths did not match'
        with allure.step('Validate breadcrumbs content for each test'):
            for test in content:
                breadcrumbs = test.pop('breadcrumbs')
                assert breadcrumbs['id'] == plan.id
                assert breadcrumbs['title'] == plan.name
                assert breadcrumbs['parent'] is None
                assert test in expected_dict, f'Test {test} is not in response {content}'

    @allure.title('Test update without history')
    def test_update_without_new_version(
        self,
        superuser_client,
        superuser,
        test_case,
        project,
        test_suite,
    ):
        new_name = 'new_expected_test_case_name'
        case_dict = {
            'id': test_case.id,
            'name': new_name,
            'skip_history': True,
            'project': project.id,
            'suite': test_suite.id,
            'scenario': constants.SCENARIO,
        }
        with allure.step('Modify history so it was produced by requested user'):
            expected_version = TestCase.objects.get(pk=test_case.id).history.latest()
            expected_version.history_user = superuser
            expected_version.save()
        response_body = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_case.pk},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
            data=case_dict,
        ).json()
        expected_version.refresh_from_db()
        actual_case = TestCase.objects.get(pk=test_case.id)
        with allure.step('Validate name changed for test case'):
            assert actual_case.name == new_name, f'Username does not match. Expected name "{actual_case.name}", ' \
                                                 f'actual: "{new_name}"'
        with allure.step('Validate current_version display'):
            assert response_body['current_version'] == expected_version.history_id
        with allure.step('Validate previous history name changed'):
            assert actual_case.name == expected_version.name, 'Historical model was not updated'
        with allure.step('Validate scenario in history changed'):
            assert actual_case.scenario == expected_version.scenario

    @allure.title('Test skipping version as another user')
    def test_change_version_from_another_user(
        self,
        superuser_client,
        superuser,
        test_case,
        project,
        test_suite,
        user_factory,
    ):
        new_name = 'new_expected_test_case_name'
        case_dict = {
            'id': test_case.id,
            'name': new_name,
            'skip_history': True,
            'project': project.id,
            'suite': test_suite.id,
            'scenario': constants.SCENARIO,
        }
        with allure.step('Modify history so it was produced by requested user'):
            expected_version = TestCase.objects.get(pk=test_case.id).history.latest()
            expected_version.history_user = superuser
            expected_version.save()
        with allure.step('Create another user'):
            user = user_factory(is_superuser=True)
        superuser_client.force_login(user)
        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_case.pk},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.BAD_REQUEST,
            data=case_dict,
        )
        with allure.step('Validate error message'):
            assert response.json()[_ERRORS][0] == FORBIDDEN_USER_TEST_CASE

    @allure.title('Test restoring test case from version')
    def test_restore_version(self, superuser_client, test_case, attachment_factory):
        assert test_case.history.count(), 'History was not created'
        attachment = attachment_factory(content_object=test_case)
        version = test_case.history.last().history_id
        old_name = test_case.name
        new_name = 'new_test_case_name'
        case_dict = {
            'id': test_case.id,
            'name': new_name,
            'project': test_case.project.id,
            'suite': test_case.suite.id,
            'scenario': constants.SCENARIO,
            'attachments': [attachment.id],
        }
        superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_case.pk},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
            data=case_dict,
        )
        with allure.step('Validate name updated'):
            assert TestCase.objects.get(pk=test_case.id).name == new_name, 'Name was not updated'
        with allure.step('Validate attachment exists'):
            assert TestCase.objects.get(pk=test_case.id).attachments.count() == 1, 'Attachment was not set'
        new_version = TestCase.history.latest().history_id
        response = superuser_client.send_request(
            self.view_restore_version,
            reverse_kwargs={'pk': test_case.pk},
            request_type=RequestType.POST,
            expected_status=HTTPStatus.OK,
            data={'version': version},
        )
        with allure.step('Validate name was restored to previous'):
            assert TestCase.objects.get(pk=test_case.id).name == old_name, 'Name was not restored'
        with allure.step('Validate attachments are not present'):
            assert not response.json().get('attachments'), 'Attachment was not deleted after restore'

        response = superuser_client.send_request(
            self.view_restore_version,
            reverse_kwargs={'pk': test_case.pk},
            request_type=RequestType.POST,
            expected_status=HTTPStatus.OK,
            data={'version': new_version},
        )
        with allure.step('Validate name'):
            assert TestCase.objects.get(pk=test_case.id).name == new_name, 'Name was not restored to new name'
        with allure.step('Validate attachments are present'):
            assert len(response.json().get('attachments')) == 1, 'Attachment was not restored'

    @allure.title('Test case creation with custom attributes')
    def test_case_creation_with_custom_attributes(
        self,
        superuser_client,
        project,
        test_suite,
        custom_attribute_factory,
    ):
        custom_attribute_name = 'awesome_attribute'
        custom_attribute_value = 'some_value'
        expected_number_of_cases = 1
        with allure.step('Create custom attribute'):
            custom_attribute_factory(
                project=project,
                name=custom_attribute_name,
                applied_to={
                    'testcase': {
                        'is_required': True,
                    },
                },
            )
        case_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
            'suite': test_suite.id,
            'setup': constants.SETUP,
            'scenario': constants.SCENARIO,
            'teardown': constants.TEARDOWN,
            'estimate': constants.INPUT_ESTIMATE,
            'attributes': {custom_attribute_name: custom_attribute_value},
        }
        superuser_client.send_request(self.view_name_list, case_dict, HTTPStatus.CREATED, RequestType.POST)
        with allure.step('Validate number of cases'):
            assert TestCase.objects.count() == expected_number_of_cases, f'Expected number of cases ' \
                                                                         f'"{expected_number_of_cases}" ' \
                                                                         f'actual: "{TestCase.objects.count()}"'

    @allure.title('Test case cannot be created with blank required attributes')
    def test_blank_required_attr_validation(
        self,
        superuser_client,
        project,
        test_suite,
        custom_attribute_factory,
    ):
        custom_attribute_name = 'awesome_attribute'
        with allure.step('Create custom attribute'):
            custom_attribute_factory(
                project=project,
                name=custom_attribute_name,
                applied_to={
                    'testcase': {
                        'is_required': True,
                    },
                },
            )
        case_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
            'suite': test_suite.id,
            'setup': constants.SETUP,
            'scenario': constants.SCENARIO,
            'teardown': constants.TEARDOWN,
            'estimate': constants.INPUT_ESTIMATE,
            'attributes': {custom_attribute_name: ''},
        }
        response = superuser_client.send_request(
            self.view_name_list,
            case_dict,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        with allure.step('Validate error message'):
            assert response.json()[_ERRORS][0] == FOUND_EMPTY_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG.format(
                [custom_attribute_name],
            )

    @allure.title('Test case cannot be created without required attributes')
    def test_required_attr_not_provided(
        self,
        superuser_client,
        project,
        test_suite,
        custom_attribute_factory,
    ):
        with allure.step('Generate custom attribute'):
            custom_attribute = custom_attribute_factory(
                project=project,
                applied_to={
                    'testcase': {
                        'is_required': True,
                    },
                },
            )
        case_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
            'suite': test_suite.id,
            'setup': constants.SETUP,
            'scenario': constants.SCENARIO,
            'teardown': constants.TEARDOWN,
            'estimate': constants.INPUT_ESTIMATE,
            'attributes': {},
        }
        response = superuser_client.send_request(
            self.view_name_list,
            case_dict,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        with allure.step('Validate error message'):
            assert response.json()[_ERRORS][0] == MISSING_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG.format(
                [custom_attribute.name],
            )

    @allure.title('Test case created if required attr is not case specific')
    def test_creation_with_non_specific_attr_for_case(
        self,
        superuser_client,
        project,
        test_suite,
        allowed_content_types,
        custom_attribute_factory,
    ):
        expected_number_of_cases = 1
        test_case_content_type_id = ContentType.objects.get_for_model(TestCase).id
        allowed_content_types.remove(test_case_content_type_id)
        custom_attribute_factory(
            project=project,
            applied_to={
                'testresult': {
                    'is_required': True,
                },
            },
        )
        case_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
            'suite': test_suite.id,
            'setup': constants.SETUP,
            'scenario': constants.SCENARIO,
            'teardown': constants.TEARDOWN,
            'estimate': constants.INPUT_ESTIMATE,
            'attributes': {},
        }
        superuser_client.send_request(self.view_name_list, case_dict, HTTPStatus.CREATED, RequestType.POST)
        assert TestCase.objects.count() == expected_number_of_cases, f'Expected number of cases ' \
                                                                     f'"{expected_number_of_cases}"' \
                                                                     f'actual: "{TestCase.objects.count()}"'

    @pytest.mark.parametrize(
        'estimate, seconds, output_estimate',
        [
            ('16h', 60 * 60 * 8 * 2, '2d'),
            ('24h', 60 * 60 * 8 * 3, '3d'),
            ('2d', 60 * 60 * 8 * 2, '2d'),
            ('3d', 60 * 60 * 8 * 3, '3d'),
            ('29h', 3600 * 8 * 3 + 3600 * 5, '3d 5h'),
            ('3d 5h', 3600 * 8 * 3 + 3600 * 5, '3d 5h'),
            ('3:05:00:00', 3600 * 8 * 3 + 3600 * 5, '3d 5h'),
        ],
    )
    def test_correct_estimates(
        self,
        superuser_client,
        project,
        test_suite,
        estimate,
        seconds,
        output_estimate,
    ):
        allure.dynamic.title(f'Test correct estimates with estimate value: {estimate}')
        case_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
            'suite': test_suite.id,
            'setup': constants.SETUP,
            'scenario': constants.SCENARIO,
            'teardown': constants.TEARDOWN,
            'estimate': estimate,
        }
        superuser_client.send_request(self.view_name_list, case_dict, HTTPStatus.CREATED, RequestType.POST)
        test_case = TestCase.objects.last()
        with allure.step('Validate estimates seconds value'):
            assert test_case.estimate == seconds, 'Wrong seconds in database'
        response = superuser_client.send_request(self.view_name_detail, reverse_kwargs={'pk': test_case.id})
        with allure.step('Validate estimate human readable value'):
            assert response.json()['estimate'] == output_estimate, 'Wrong estimate value in response'

    def test_single_search_by_label(
        self,
        api_client,
        authorized_superuser,
        test_case_factory,
        project,
        labeled_item_factory,
        label_factory,
    ):
        first_label = label_factory(name='first')
        second_label = label_factory(name='second')
        with_first_label = []
        with_second_label = []
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            if idx % 2:
                test_case = test_case_factory(project=project)
                labeled_item_factory(content_object=test_case, label=first_label)
                with_first_label.append(test_case)
            else:
                test_case = test_case_factory(project=project)
                labeled_item_factory(content_object=test_case, label=second_label)
                with_second_label.append(test_case)

        for label, expected_instances in ((first_label, with_first_label), (second_label, with_second_label)):
            expected_output = model_to_dict_via_serializer(
                expected_instances,
                TestCaseMockSerializer,
                many=True,
                nested_fields_simple_list=['versions', 'labels'],
            )

            actual_data = api_client.send_request(
                self.view_name_list,
                query_params={'project': project.id, 'labels': label.id},
            ).json()['results']
            assert expected_output == actual_data

    @pytest.mark.parametrize('operation, labels_condition', [(operator.and_, 'and'), (operator.or_, 'or')])
    def test_multiple_search_by_label(
        self,
        api_client,
        authorized_superuser,
        test_case_factory,
        project,
        labeled_item_factory,
        label_factory,
        operation,
        labels_condition,
    ):
        first_label = label_factory(name='first')
        second_label = label_factory(name='second')
        with_first_label = set()
        with_second_label = set()
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            if idx % 2:
                test_case = test_case_factory(project=project)
                labeled_item_factory(content_object=test_case, label=first_label)
                with_first_label.add(test_case)
            if idx % 3:
                test_case = test_case_factory(project=project)
                labeled_item_factory(content_object=test_case, label=second_label)
                with_second_label.add(test_case)
        expected_output = model_to_dict_via_serializer(
            list(operation(with_first_label, with_second_label)),
            TestCaseMockSerializer,
            many=True,
            nested_fields_simple_list=['versions', 'labels'],
        )
        actual_data = api_client.send_request(
            self.view_name_list,
            query_params={
                'project': project.id,
                'labels': ','.join([str(first_label.pk), str(second_label.pk)]),
                'labels_condition': labels_condition,
            },
        ).json()['results']
        assert expected_output == actual_data

    @allure.title('Test labels are restored on version restore')
    def test_labels_restored(self, labeled_item_factory, label_factory, test_case, project, superuser_client):
        number_of_labels = 3
        version_to_restore = test_case.history.latest().history_id
        labels = [label_factory(project=project) for _ in range(number_of_labels)]
        with allure.step('Get body for request'):
            body = superuser_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': test_case.pk},
            ).json()
        with allure.step('Create labeled items'):
            for label in labels:
                labeled_item_factory(
                    content_object=test_case,
                    label=label,
                    content_object_history_id=version_to_restore,
                )
        with allure.step('Validate labels exist before deletion'):
            assert self.labels_count_from_api(superuser_client, test_case.pk) == number_of_labels
        with allure.step('Remove labels via api'):
            superuser_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': test_case.pk},
                data=body,
                request_type=RequestType.PUT,
            ).json()
        with allure.step('Validate labels removed'):
            assert not self.labels_count_from_api(superuser_client, test_case.pk)
        with allure.step('Get version without labels'):
            version_no_labels = test_case.history.latest().history_id
        with allure.step('Restore version'):
            superuser_client.send_request(
                self.view_restore_version,
                reverse_kwargs={'pk': test_case.pk},
                request_type=RequestType.POST,
                expected_status=HTTPStatus.OK,
                data={'version': version_to_restore},
            )
        with allure.step('Validate labels are restored on case without version provided'):
            assert self.labels_count_from_api(superuser_client, test_case.pk) == number_of_labels
        with allure.step('Validate labels count did not change on oldest version'):
            assert self.labels_count_from_api(superuser_client, test_case.pk, version_to_restore) == number_of_labels
        with allure.step('Validate labels count did not change on version without labels'):
            assert not self.labels_count_from_api(superuser_client, test_case.pk, version_no_labels)
        with allure.step('Validate labels are displayed with latest version'):
            latest_version = test_case.history.latest().history_id
            assert self.labels_count_from_api(superuser_client, test_case.pk, latest_version) == number_of_labels

    @allure.step('Get number of labels from response via api')
    def labels_count_from_api(self, superuser_client: CustomAPIClient, pk: int, version: int | None = None) -> int:
        query_params = {'version': version} if version else None
        return len(
            superuser_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': pk},
                query_params=query_params,
            ).json().get('labels'),
        )

    @allure.title('Test getting delete preview for archive test case')
    def test_delete_preview_for_archived_case(self, superuser_client, test_case_factory, use_dummy_cache_backend):
        test_case = test_case_factory(is_archive=True)
        superuser_client.send_request(
            self.view_name_delete_preview,
            reverse_kwargs={'pk': test_case.id},
            request_type=RequestType.GET,
            expected_status=HTTPStatus.OK,
        )


@pytest.mark.django_db(reset_sequences=True)
@allure.parent_suite('Test cases with steps')
@allure.suite('Integration tests')
@allure.sub_suite('Endpoints')
class TestCaseWithStepsEndpoints:
    view_name_detail = 'api:v1:testcase-detail'
    view_name_list = 'api:v1:testcase-list'
    view_restore_version = 'api:v1:testcase-restore-version'
    view_name_copy = 'api:v1:testcase-copy'

    @allure.title('Test detail display')
    def test_retrieve(self, superuser_client, test_case_with_steps):
        expected_dict = model_to_dict_via_serializer(
            test_case_with_steps,
            TestCaseMockSerializer,
            nested_fields=['steps'],
            nested_fields_simple_list=['versions'],
        )
        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_case_with_steps.id},
        )
        with allure.step('Validate response body'):
            assert response.json() == expected_dict, 'Expected and actual dict did not match'

    @allure.title('Test list display')
    def test_list(self, superuser_client, test_case_with_steps_factory, project):
        expected_instances = []
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            expected_instances.append(test_case_with_steps_factory(project=project))
        expected_instances = model_to_dict_via_serializer(
            expected_instances,
            TestCaseMockSerializer,
            many=True,
            nested_fields=['steps'],
            nested_fields_simple_list=['versions'],
        )

        response = superuser_client.send_request(self.view_name_list, query_params={'project': project.id})
        with allure.step('Validate response body'):
            assert response.json()['results'] == sorted(expected_instances, key=lambda instance: instance['name'])

    @pytest.mark.parametrize('steps_number', [0, 1, 2, 10], ids=['No steps', '1 step', '2 steps', '10 steps'])
    def test_create(self, superuser_client, test, steps_number):
        allure.dynamic.title(f'Test case creation with {steps_number} steps')
        test_case_json = {
            'test': test.id,
            'project': test.project.id,
            'suite': test.case.suite.id,
            'scenario': constants.SCENARIO,
            'name': 'Test case name',
            'is_steps': True,
            'steps': [
                {
                    'name': f'Valuable step {idx}',
                    'scenario': f'{constants.SCENARIO}{idx}',
                    'expected': f'{constants.EXPECTED}{idx}',
                } for idx in range(steps_number)
            ],
        }
        if not steps_number:
            with allure.step('Validate case with steps requires steps'):
                superuser_client.send_request(
                    self.view_name_list,
                    data=test_case_json,
                    request_type=RequestType.POST,
                    expected_status=HTTPStatus.BAD_REQUEST,
                    additional_error_msg='No error messages on zero steps when is_steps=True',
                )
            return
        created_case_id = superuser_client.send_request(
            self.view_name_list,
            data=test_case_json,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
        ).json()['id']
        actual_case = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': created_case_id},
        ).json()
        with allure.step('Validate steps number'):
            assert len(test_case_json['steps']) == steps_number, 'Wrong number of steps were created'
        self._validate_steps_content(test_case_json['steps'], actual_case['steps'])

    @pytest.mark.parametrize('field_to_update', ['name', 'scenario', 'expected', 'sort_order'])
    def test_update(self, superuser_client, test_case_with_steps, field_to_update):
        allure.dynamic.title(f'Test case step {field_to_update} field updated correctly')
        update_dict = model_to_dict_via_serializer(
            test_case_with_steps,
            TestCaseMockSerializer,
            nested_fields=['steps'],
            nested_fields_simple_list=['versions'],
        )
        for step, new_content in zip(update_dict['steps'], range(constants.NUMBER_OF_OBJECTS_TO_CREATE, 0, -1)):
            step[field_to_update] = str(new_content)

        superuser_client.send_request(
            self.view_name_detail,
            data=update_dict,
            reverse_kwargs={'pk': update_dict['id']},
            request_type=RequestType.PUT,
        )
        actual_data = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': update_dict['id']},
        ).json()
        expected_steps = reversed(update_dict['steps']) if field_to_update == 'sort_order' else update_dict['steps']
        self._validate_steps_content(expected_steps, actual_data['steps'])

    @allure.title('Test update steps replaces steps')
    def test_update_steps_replacement(self, superuser_client, test_case_with_steps):
        update_dict = model_to_dict_via_serializer(
            test_case_with_steps,
            TestCaseMockSerializer,
            nested_fields=['steps'],
            nested_fields_simple_list=['versions'],
        )
        new_number_of_steps = 3
        old_steps = deepcopy(update_dict['steps'])
        with allure.step('Generate new steps'):
            update_dict['steps'] = [
                {
                    'name': f'Valuable step {idx}',
                    'scenario': f'{constants.SCENARIO}{idx}',
                    'expected': f'{constants.EXPECTED}{idx}',
                } for idx in range(new_number_of_steps)
            ]
        superuser_client.send_request(
            self.view_name_detail,
            data=update_dict,
            reverse_kwargs={'pk': update_dict['id']},
            request_type=RequestType.PUT,
        )
        actual_data = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': update_dict['id']},
        ).json()
        with allure.step('Validate number of steps changed'):
            assert len(old_steps) != len(actual_data['steps']), 'Expected number of steps did not match actual'
        with allure.step('Validate old steps removed'):
            for step in old_steps:
                assert step not in actual_data['steps'], 'Old steps were not removed.'

    @pytest.mark.parametrize('number_of_steps', [0, 1, 2, 10], ids=['No steps', '1 step', '2 steps', '10 steps'])
    def test_update_steps_addition(self, superuser_client, test_case_with_steps, number_of_steps):
        allure.dynamic.title(f'Test new steps added on update {number_of_steps} steps')
        update_dict = model_to_dict_via_serializer(
            test_case_with_steps,
            TestCaseMockSerializer,
            nested_fields=['steps'],
            nested_fields_simple_list=['versions'],
        )
        old_steps = deepcopy(update_dict['steps'])
        with allure.step('Add new steps to already existing ones'):
            new_steps = [
                {
                    'name': f'Valuable step {idx}',
                    'scenario': f'{constants.SCENARIO}{idx}',
                    'expected': f'{constants.EXPECTED}{idx}',
                } for idx in range(number_of_steps)
            ]
            update_dict['steps'].extend(new_steps)
        actual_data = superuser_client.send_request(
            self.view_name_detail,
            data=update_dict,
            reverse_kwargs={'pk': update_dict['id']},
            request_type=RequestType.PUT,
        ).json()
        with allure.step('Validate old steps are kept'):
            for step in old_steps:
                assert step in actual_data['steps'], 'Old step was removed by adding new steps.'
        with allure.step('Validate number of steps'):
            assert len(actual_data['steps']) == len(old_steps) + number_of_steps, \
                'New steps were not added.'

    @allure.title('Validate patch request not allowed')
    def test_patch_not_allowed(self, superuser_client, test_case):
        superuser_client.send_request(
            self.view_name_detail,
            data={},
            reverse_kwargs={'pk': test_case.id},
            request_type=RequestType.PATCH,
            expected_status=HTTPStatus.METHOD_NOT_ALLOWED,
            additional_error_msg='User was able to patch test case.',
        )

    @allure.title('Test search')
    def test_search(self, superuser_client, test_case_factory, project):
        expected_cases = []
        search_name = 'search_name'
        with allure.step('Create cases that will be found'):
            for _ in range(int(constants.NUMBER_OF_OBJECTS_TO_CREATE / 2)):
                expected_cases.append(
                    test_case_factory(name=search_name, project=project),
                )
        with allure.step('Create cases that will not be found'):
            for _ in range(int(constants.NUMBER_OF_OBJECTS_TO_CREATE / 2)):
                test_case_factory(project=project)

        expected_output = model_to_dict_via_serializer(expected_cases, TestCaseMockSerializer, many=True, as_json=True)
        actual_data = superuser_client.send_request(
            self.view_name_list,
            query_params={'project': project.id, 'search': search_name},
        ).json_strip(as_json=True)

        with allure.step('Validate response body'):
            assert actual_data == expected_output

        actual_data = superuser_client.send_request(
            self.view_name_list,
            query_params={
                'project': project.id,
                'search': 'non-existent',
            },
        ).json()['results']
        assert not actual_data, 'Non-existent search argument got output.'

    @pytest.mark.parametrize(
        'is_case_attachment, is_steps_attachment',
        [
            [False, False],
            [True, False],
            [False, True],
            [True, True],
        ],
    )
    def test_restore_version_with_steps(
        self,
        superuser_client,
        attachment_factory,
        is_case_attachment,
        is_steps_attachment,
        test,
    ):
        title = 'Test restore case version with attachment for{0}{1}'
        allure.dynamic.title(
            title.format(
                ' case' if is_case_attachment else '',
                ' steps' if is_steps_attachment else '',
            ),
        )
        test_case_json = {
            'test': test.id,
            'project': test.project.id,
            'suite': test.case.suite.id,
            'scenario': constants.SCENARIO,
            'name': 'Test case name',
            'is_steps': True,
            'attachments': [attachment_factory(content_type=None, object_id=None).id] if is_case_attachment else [],
            'steps': [
                {
                    'name': f'Valuable step {idx}',
                    'scenario': f'{constants.SCENARIO}{idx}',
                    'expected': f'{constants.EXPECTED}{idx}',
                    'attachments': [attachment_factory(content_type=None, object_id=None).id]
                    if is_steps_attachment else [],
                } for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)
            ],
        }
        created_case_id = superuser_client.send_request(
            self.view_name_list,
            data=test_case_json,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
        ).json()['id']

        test_case = TestCase.objects.get(pk=created_case_id)
        version = test_case.history.latest().history_id
        assert bool(test_case.attachments.count()) == is_case_attachment
        for step in test_case.steps.all():
            assert bool(step.attachments.count()) == is_steps_attachment

        old_name = test_case.name
        new_name = 'new_test_case_name'
        case_dict = {
            'id': test_case.id,
            'name': new_name,
            'project': test_case.project.id,
            'suite': test_case.suite.id,
            'scenario': constants.SCENARIO,
            'is_steps': False,
            'steps': [],
            'attachments': [],
        }
        superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_case.id},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
            data=case_dict,
        )
        updated_test_case = TestCase.objects.get(pk=test_case.id)

        with allure.step('Validate name updated'):
            assert updated_test_case.name == new_name, 'Name was not updated'
        with allure.step('Validate steps deleted'):
            assert updated_test_case.steps.count() == 0, 'Steps were not deleted'
        with allure.step('Validate cases count'):
            assert updated_test_case.attachments.count() == 0
        with allure.step('Validate steps count'):
            for step in updated_test_case.steps.all():
                assert bool(step.attachments.count()) == is_steps_attachment
        for step in updated_test_case.steps.all():
            assert bool(step.attachments.count()) == is_steps_attachment

        for idx in range(1, 10):
            previous_version = test_case.history.latest().history_id

            content = superuser_client.send_request(
                self.view_restore_version,
                reverse_kwargs={'pk': test_case.pk},
                request_type=RequestType.POST,
                expected_status=HTTPStatus.OK,
                data={'version': version},
            ).json()
            restored_test_case = TestCase.objects.get(pk=test_case.id)
            expected_name = old_name if idx % 2 else new_name
            expected_case_value = idx % 2 if is_case_attachment else 0
            expected_step_value = idx % 2 if is_steps_attachment else 0
            expected_step_count = constants.NUMBER_OF_OBJECTS_TO_CREATE if idx % 2 else 0
            with allure.step('Validate name restored'):
                assert restored_test_case.name == expected_name, 'Name was not restored'
            with allure.step('Validate number of attachments'):
                assert restored_test_case.attachments.count() == expected_case_value
            with allure.step('Validate steps count'):
                assert len(content.get('steps')) == expected_step_count, \
                    'Steps were not restored after restore'
            for step in restored_test_case.steps.all():
                assert step.attachments.count() == expected_step_value
            version = previous_version

    @allure.title('Test attachments on steps restored')
    def test_restore_steps_attachments(self, superuser_client, attachment_factory, test):
        test_case_json = {
            'test': test.id,
            'project': test.project.id,
            'suite': test.case.suite.id,
            'scenario': constants.SCENARIO,
            'name': 'Test case name',
            'is_steps': True,
            'steps': [
                {
                    'name': f'Valuable step {idx}',
                    'scenario': f'{constants.SCENARIO}{idx}',
                    'expected': f'{constants.EXPECTED}{idx}',
                    'attachments': [attachment_factory(content_type=None, object_id=None).id],
                } for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)
            ],
        }

        created_case_id = superuser_client.send_request(
            self.view_name_list,
            data=test_case_json,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
        ).json()['id']

        with allure.step('Remove attachments from response payload'):
            for step in test_case_json['steps']:
                step.pop('attachments')
        test_case = TestCase.objects.get(pk=created_case_id)
        version = test_case.history.latest().history_id
        with allure.step('Validate attachments count'):
            for step in test_case.steps.all():
                assert step.attachments.count() == 1

        with allure.step('Remove attachments from steps via api'):
            superuser_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': test_case.pk},
                request_type=RequestType.PUT,
                expected_status=HTTPStatus.OK,
                data=test_case_json,
            )
        with allure.step('Validate attachments were removed'):
            for step in test_case.steps.all():
                assert step.attachments.count() == 0

        with allure.step('Validate attachments count changes on version restore'):
            for idx in range(1, 10):
                previous_version = test_case.history.latest().history_id
                superuser_client.send_request(
                    self.view_restore_version,
                    reverse_kwargs={'pk': test_case.pk},
                    request_type=RequestType.POST,
                    expected_status=HTTPStatus.OK,
                    data={'version': version},
                )
                for step in test_case.steps.all():
                    assert step.attachments.count() == idx % 2
                version = previous_version

    @pytest.mark.parametrize('field_to_update', ['name', 'scenario', 'expected', 'sort_order'])
    def test_update_without_new_version(
        self,
        superuser_client,
        superuser,
        test_case_with_steps,
        field_to_update,
    ):
        allure.dynamic.title(f'Test update without new version for field {field_to_update}')
        update_dict = model_to_dict_via_serializer(
            test_case_with_steps,
            TestCaseMockSerializer,
            nested_fields=['steps'],
            nested_fields_simple_list=['versions'],
        )
        update_dict['skip_history'] = True
        with allure.step('Change history user on case and steps'):
            version = TestCase.objects.get(pk=test_case_with_steps.id).history.latest()
            version.history_user = superuser
            version.save()
            for step in test_case_with_steps.steps.all():
                step.history.all().update(history_user=superuser)

        expected_count_case_versions = TestCase.objects.get(pk=test_case_with_steps.id).history.count()
        expected_count_step_versions = 1
        for step, new_content in zip(update_dict['steps'], range(constants.NUMBER_OF_OBJECTS_TO_CREATE, 0, -1)):
            step[field_to_update] = str(new_content)
        superuser_client.send_request(
            self.view_name_detail,
            data=update_dict,
            reverse_kwargs={'pk': update_dict['id']},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
        )
        actual_data = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': update_dict['id']},
        ).json()
        expected_steps = reversed(update_dict['steps']) if field_to_update == 'sort_order' else update_dict['steps']
        self._validate_steps_content(expected_steps, actual_data['steps'])
        with allure.step('Validate versions count'):
            assert len(actual_data['versions']) == expected_count_case_versions, 'New version of test case was created'
        for step in TestCase.objects.get(pk=test_case_with_steps.id).steps.all():
            assert step.history.count() == expected_count_step_versions, (
                f'New version of step '
                f'id={step.id} was created'
            )

    @allure.title('Test another user cannot update test case with skipping history')
    def test_update_as_another_user(
        self,
        superuser_client,
        test_case_with_steps,
    ):
        update_dict = model_to_dict_via_serializer(
            test_case_with_steps,
            TestCaseMockSerializer,
            nested_fields=['steps'],
            nested_fields_simple_list=['versions'],
        )
        update_dict['skip_history'] = True
        response = superuser_client.send_request(
            self.view_name_detail,
            data=update_dict,
            reverse_kwargs={'pk': update_dict['id']},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.BAD_REQUEST,
        )
        with allure.step('Validate error message'):
            assert response.json()[_ERRORS][0] == FORBIDDEN_USER_TEST_CASE

    @allure.title('Regression migrating back steps')
    def test_migrating_steps(self, authorized_client, project, test_suite_factory):
        suite = test_suite_factory(project=project)
        copied_case_name = 'copied_case'
        payload = {
            'name': 'Case',
            'attributes': {},
            'attachments': [],
            'is_steps': True,
            'steps': [
                {'name': '1', 'scenario': '1', 'expected': '', 'sort_order': 1, 'attachments': []},
                {'name': '2', 'scenario': '2', 'expected': '', 'sort_order': 2, 'attachments': []},
            ],
            'project': project.pk,
            'suite': suite.pk,
        }
        with allure.step('Create test case with steps via api'):
            src_case_id = authorized_client.send_request(
                self.view_name_list,
                data=payload,
                request_type=RequestType.POST,
                expected_status=HTTPStatus.CREATED,
            ).json()['id']
        with allure.step('Bump version of test case via update'):
            authorized_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': src_case_id},
                data=payload,
                request_type=RequestType.PUT,
            )
        with allure.step('Create copy of test case via api'):
            authorized_client.send_request(
                self.view_name_copy,
                data={'cases': [{'id': src_case_id, 'new_name': copied_case_name}]},
                request_type=RequestType.POST,
            )
        copied_case = TestCase.objects.filter(name=copied_case_name).first()
        with allure.step('Bump copied case version'):
            authorized_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': copied_case.pk},
                data=payload,
                request_type=RequestType.PUT,
            )
        restore_ver = copied_case.history.all().order_by('history_date').first().history_id
        authorized_client.send_request(
            self.view_restore_version,
            reverse_kwargs={'pk': copied_case.pk},
            request_type=RequestType.POST,
            expected_status=HTTPStatus.OK,
            data={'version': restore_ver},
        )
        with allure.step('Get copied case via api'):
            resp_body = authorized_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': copied_case.pk},
            ).json()
        with allure.step('Validate steps did not migrate'):
            assert len(resp_body['steps']) == 2
        resp_body = authorized_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': src_case_id},
        ).json()
        assert len(resp_body['steps']) == 2

    @classmethod
    @allure.step('Validate steps content')
    def _validate_steps_content(cls, expected, actual):
        fields_to_validate = ['name', 'scenario', 'expected']
        for expected_step, actual_step in zip(expected, actual):
            for field_name in fields_to_validate:
                assert expected_step[field_name] == actual_step[field_name], f'Field "{field_name}" ' \
                                                                             f'content does not match expected\n' \
                                                                             f'Actual content: ' \
                                                                             f'{actual_step[field_name]}'
