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
from http import HTTPStatus

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from tests import constants, error_messages
from tests.commons import RequestType, model_to_dict_via_serializer
from tests.error_messages import (
    ATTRIBUTES_PARAMETER_NOT_PASSED,
    CREATE_RESULT_IN_ARCHIVE_TEST,
    FOUND_EMPTY_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG,
    MISSING_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG,
    PERMISSION_ERR_MSG,
    UPDATE_ARCHIVE_RESULT,
)
from testy.core.choices import CustomFieldType
from testy.tests_representation.api.v1.serializers import TestResultSerializer
from testy.tests_representation.models import TestResult

_ERRORS = 'errors'


@pytest.mark.django_db
class TestResultEndpoints:
    view_name_list = 'api:v1:testresult-list'
    view_name_detail = 'api:v1:testresult-detail'
    project_view_name_detail = 'api:v1:project-detail'
    plan_view_name_detail = 'api:v1:testplan-detail'
    view_name_attributes = 'api:v1:testresult-attributes'

    def test_list(self, api_client, authorized_superuser, test_result_factory, project, result_status_factory):
        test_results = []
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test_results.append(test_result_factory(project=project, status=result_status_factory(project=project)))

        expected_instances = model_to_dict_via_serializer(
            test_results,
            TestResultSerializer,
            many=True,
            fields_to_add={'latest': True},
        )

        response = api_client.send_request(self.view_name_list, query_params={'project': project.id})

        for instance_dict in response.json():
            assert instance_dict in expected_instances, f'{instance_dict} was not found in expected instances.'

    def test_retrieve(self, api_client, authorized_superuser, test_result):
        expected_dict = model_to_dict_via_serializer(test_result, TestResultSerializer, fields_to_add={'latest': True})
        response = api_client.send_request(self.view_name_detail, reverse_kwargs={'pk': test_result.pk})
        actual_dict = response.json()
        assert actual_dict == expected_dict, 'Actual model dict is different from expected'

    def test_partial_update(self, api_client, authorized_superuser, test_result, user, result_status_factory):
        update_dict = {
            'user': user.id,
            'status': result_status_factory(project=test_result.project).pk,
            'comment': 'new_comment',
        }
        api_client.send_request(
            self.view_name_detail,
            update_dict,
            request_type=RequestType.PATCH,
            reverse_kwargs={'pk': test_result.pk},
        )
        actual_dict = model_to_dict_via_serializer(TestResult.objects.get(pk=test_result.id), TestResultSerializer)
        for key in update_dict.keys():
            assert update_dict[key] == actual_dict[key], f'Field "{key}" was not updated.'

    def test_update(self, api_client, authorized_superuser, test_result, user, result_status_factory):
        update_dict = {
            'id': test_result.id,
            'test': test_result.test.id,
            'user': user.id,
            'status': result_status_factory(project=test_result.project).pk,
            'comment': 'new_comment',
        }
        api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_result.pk},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
            data=update_dict,
        )
        actual_dict = model_to_dict_via_serializer(TestResult.objects.get(pk=test_result.id), TestResultSerializer)
        for key in update_dict.keys():
            assert update_dict[key] == actual_dict[key], f'Field "{key}" was not updated.'

    def test_add_results_to_test(self, api_client, authorized_superuser, user, test_factory, result_status_factory):
        tests = [test_factory(), test_factory()]
        for test in tests:
            result_dict = {
                'status': result_status_factory(project=test.project).pk,
                'user': user.id,
                'comment': constants.TEST_COMMENT,
                'test': test.id,
            }
            api_client.send_request(
                'api:v1:testresult-list',
                expected_status=HTTPStatus.CREATED,
                request_type=RequestType.POST,
                data=result_dict,
            )
        assert TestResult.objects.count() == 2, 'Expected number of results was not created.'
        assert TestResult.objects.filter(test=tests[0]).count() == 1, f'Only 1 result should be on a test "{tests[0]}"'
        assert TestResult.objects.filter(test=tests[1]).count() == 1, f'Only 1 result should be on a test "{tests[1]}"'

    def test_deleted_status_forbidden(
        self, user, api_client, authorized_superuser, test,
        test_result, result_status_factory,
    ):
        result_dict = {
            'status': result_status_factory(project=test_result.project, is_deleted=True).pk,
            'user': user.id,
            'comment': constants.TEST_COMMENT,
            'test': test.id,
        }
        api_client.send_request(
            self.view_name_list,
            expected_status=HTTPStatus.BAD_REQUEST,
            request_type=RequestType.POST,
            data=result_dict,
        )
        for update_type in (RequestType.PATCH, RequestType.PUT):
            api_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': test_result.pk},
                expected_status=HTTPStatus.BAD_REQUEST,
                request_type=update_type,
                data=result_dict,
            )

    def test_null_status_not_allowed(self, user, api_client, authorized_superuser, test, test_result):
        result_dict = {
            'user': user.id,
            'comment': constants.TEST_COMMENT,
            'test': test.id,
            'status': None,
        }
        api_client.send_request(
            self.view_name_list,
            expected_status=HTTPStatus.BAD_REQUEST,
            request_type=RequestType.POST,
            data=result_dict,
        )
        for update_type in (RequestType.PATCH, RequestType.PUT):
            api_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': test_result.pk},
                expected_status=HTTPStatus.BAD_REQUEST,
                request_type=update_type,
                data=result_dict,
            )

    def test_blank_status_not_allowed(self, user, api_client, authorized_superuser, test, test_result):
        result_dict = {
            'user': user.id,
            'comment': constants.TEST_COMMENT,
            'test': test.id,
        }
        api_client.send_request(
            self.view_name_list,
            expected_status=HTTPStatus.BAD_REQUEST,
            request_type=RequestType.POST,
            data=result_dict,
        )
        api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_result.pk},
            expected_status=HTTPStatus.BAD_REQUEST,
            request_type=RequestType.PUT,
            data=result_dict,
        )

    def test_get_results_by_test(
        self, api_client, test_result_factory, test_factory, authorized_superuser,
        project, result_status_factory,
    ):
        test1 = test_factory()
        test2 = test_factory()
        dicts_test1 = []
        dicts_test2 = []
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            latest = idx == constants.NUMBER_OF_OBJECTS_TO_CREATE - 1
            dicts_test1.append(
                model_to_dict_via_serializer(
                    test_result_factory(test=test1, project=project, status=result_status_factory(project=project)),
                    TestResultSerializer,
                    fields_to_add={'latest': latest},
                ),
            )
            dicts_test2.append(
                model_to_dict_via_serializer(
                    test_result_factory(test=test2, project=project, status=result_status_factory(project=project)),
                    TestResultSerializer,
                    fields_to_add={'latest': latest},
                ),
            )

        response_test1 = api_client.send_request(
            'api:v1:testresult-list',
            expected_status=HTTPStatus.OK,
            request_type=RequestType.GET,
            query_params={'test': test1.id, 'project': project.id},
        )
        response_test2 = api_client.send_request(
            'api:v1:testresult-list',
            expected_status=HTTPStatus.OK,
            request_type=RequestType.GET,
            query_params={'test': test2.id, 'project': project.id},
        )
        actual_results1 = response_test1.json()
        actual_results2 = response_test2.json()
        assert actual_results1 and actual_results2
        assert len(actual_results1) == len(actual_results2)
        for result_test1, result_test2 in zip(actual_results1, actual_results2):
            assert result_test1 in dicts_test1, 'Response is different from expected one'
            assert result_test2 in dicts_test2, 'Response is different from expected one'

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT, RequestType.DELETE, RequestType.POST])
    def test_result_permissions(
        self, api_client, authorized_superuser, test_result_factory, user,
        request_type, project_factory, test_factory, result_status_factory,
    ):
        api_client.force_login(user)
        project = project_factory(is_archive=True)
        status = result_status_factory(project=project)
        if request_type == RequestType.POST:
            test = test_factory(project=project)
            response = api_client.send_request(
                self.view_name_list,
                request_type=request_type,
                expected_status=HTTPStatus.FORBIDDEN,
                data={
                    'status': status.pk,
                    'user': user.id,
                    'comment': constants.TEST_COMMENT,
                    'test': test.id,
                },
            )
        else:
            result = test_result_factory(project=project_factory(is_archive=True), status=status)
            response = api_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': result.pk},
                request_type=request_type,
                expected_status=HTTPStatus.FORBIDDEN,
                data={},
            )

        assert response.json()['detail'] == PERMISSION_ERR_MSG

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    @pytest.mark.parametrize('invalid_by', ['time', 'version'])
    def test_result_update_constraints(
        self, api_client, authorized_superuser, test_case, test_factory, invalid_by,
        request_type, result_status_factory,
    ):
        test = test_factory(case=test_case)
        update_dict = {
            'status': result_status_factory(project=test.project).pk,
            'comment': 'new_comment',
        }
        result_id = api_client.send_request(
            self.view_name_list,
            data={
                'project': test.project.id,
                'test': test.id,
                'status': result_status_factory(project=test.project).pk,
                'comment': 'Src comment',
            },
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
        ).json()['id']

        if invalid_by == 'time':
            result = TestResult.objects.get(pk=result_id)
            result.created_at = timezone.now() - timezone.timedelta(
                hours=test.project.settings.get('result_edit_limit'), minutes=1,
            )
            result.save()
        else:
            old_version = test_case.history.first().history_id
            api_client.send_request(
                'api:v1:testcase-detail',
                data={
                    'project': test.case.project.id,
                    'suite': test.case.suite.id,
                    'name': test.case.name,
                    'scenario': 'new_scenario',
                },
                request_type=RequestType.PUT,
                reverse_kwargs={'pk': test_case.pk},
                expected_status=HTTPStatus.OK,
            )
            assert old_version != test_case.history.first().history_id, 'Test case version did not change'

        api_client.send_request(
            self.view_name_detail,
            data=update_dict,
            reverse_kwargs={'pk': result_id},
            request_type=RequestType.PATCH,
            expected_status=HTTPStatus.BAD_REQUEST,
        )

    def test_result_related_instance_change_allows_update(
        self,
        api_client,
        authorized_superuser,
        test_case,
        test_factory,
        project,
        user,
        result_status_factory,
    ):
        test = test_factory(case=test_case, project=project)
        result_id = api_client.send_request(
            self.view_name_list,
            data={
                'project': test.project.id,
                'test': test.id,
                'status': result_status_factory(project=project).pk,
                'comment': 'Src comment',
            },
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
        ).json()['id']
        project.name = 'New project name'
        project.save()
        test.assignee = user
        test.save()
        api_client.send_request(
            self.view_name_detail,
            data={
                'comment': 'new_comment',
            },
            reverse_kwargs={'pk': result_id},
            request_type=RequestType.PATCH,
            expected_status=HTTPStatus.OK,
        )

    @pytest.mark.parametrize(
        'view_name, query_param_key', [
            (project_view_name_detail, 'project'),
            (plan_view_name_detail, 'test_plan'),
        ],
    )
    def test_soft_delete(
            self, api_client, authorized_superuser, test_result_factory, project, test_factory, test_plan,
            view_name, query_param_key, result_status_factory,
    ):
        test = test_factory(project=project, plan=test_plan)
        parent_id = locals()[query_param_key].id
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test_result_factory(test=test, project=project, status=result_status_factory(project=project))
        response = api_client.send_request(self.view_name_list, query_params={'project': project.id})
        assert len(response.json()) == constants.NUMBER_OF_OBJECTS_TO_CREATE
        api_client.send_request(
            view_name,
            reverse_kwargs={'pk': parent_id},
            request_type=RequestType.DELETE,
            expected_status=HTTPStatus.NO_CONTENT,
        )
        assert not len(TestResult.objects.all()), 'Test results were not cascade deleted'
        assert len(TestResult.deleted_objects.all()) == constants.NUMBER_OF_OBJECTS_TO_CREATE

    @pytest.mark.parametrize(
        'view_name, query_param_key', [
            (project_view_name_detail, 'project'),
            (plan_view_name_detail, 'test_plan'),
        ],
    )
    def test_restore(
        self, api_client, authorized_superuser, test_result_factory, project, test_factory, test_plan,
        view_name, query_param_key, result_status_factory,
    ):
        test = test_factory(project=project, plan=test_plan)
        parent_id = locals()[query_param_key].id
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test_result_factory(test=test, project=project, status=result_status_factory(project=project))
        response = api_client.send_request(self.view_name_list, query_params={'project': project.id})
        assert len(response.json()) == constants.NUMBER_OF_OBJECTS_TO_CREATE
        api_client.send_request(
            view_name,
            reverse_kwargs={'pk': parent_id},
            request_type=RequestType.DELETE,
            expected_status=HTTPStatus.NO_CONTENT,
        )
        assert not len(TestResult.objects.all()), 'Test results were not cascade deleted'
        assert len(TestResult.deleted_objects.all()) == constants.NUMBER_OF_OBJECTS_TO_CREATE

    def test_test_result_created_if_all_required_custom_attributes_are_filled(
        self, api_client, authorized_superuser, project, user, test_factory,
        result_status_factory, custom_attribute_factory,
    ):
        custom_attribute_name = 'awesome_attribute'
        custom_attribute_value = 'some_value'
        expected_number_of_results = 1
        status = result_status_factory(project=project)
        custom_attribute_factory(
            name=custom_attribute_name,
            project=project,
            applied_to={
                'testresult': {
                    'is_required': True,
                },
            },
        )
        test = test_factory(project=project)
        result_dict = {
            'status': status.pk,
            'user': user.id,
            'comment': constants.TEST_COMMENT,
            'test': test.id,
            'attributes': {custom_attribute_name: custom_attribute_value},
        }
        api_client.send_request(
            self.view_name_list, expected_status=HTTPStatus.CREATED, request_type=RequestType.POST, data=result_dict,
        )

        assert TestResult.objects.count() == expected_number_of_results, f'Expected number of cases ' \
                                                                         f'"{expected_number_of_results}" ' \
                                                                         f'actual: "{TestResult.objects.count()}"'

    def test_test_result_is_not_created_if_required_attribute_exists_but_is_empty(
        self, api_client, authorized_superuser, allowed_content_types, project, user, test_factory,
        result_status_factory,
    ):
        custom_attribute_name = 'awesome_attribute'
        status = result_status_factory(project=project)

        api_client.send_request(
            'api:v1:customattribute-list',
            expected_status=HTTPStatus.CREATED,
            request_type=RequestType.POST,
            data={
                'name': custom_attribute_name,
                'project': project.pk,
                'type': CustomFieldType.TXT,
                'content_types': allowed_content_types,
                'is_required': True,
                'status_specific': None,
            },
        )
        test = test_factory(project=project)
        result_dict = {
            'status': status.pk,
            'user': user.id,
            'comment': constants.TEST_COMMENT,
            'test': test.id,
            'attributes': {custom_attribute_name: ''},
        }
        response = api_client.send_request(self.view_name_list, result_dict, HTTPStatus.BAD_REQUEST, RequestType.POST)
        assert response.json()[_ERRORS][0] == FOUND_EMPTY_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG.format(
            [custom_attribute_name],
        )

    def test_test_result_not_created_if_required_custom_attribute_missing(
        self, api_client, authorized_superuser, custom_attribute_factory, project, user, test_factory,
        result_status_factory,
    ):
        status = result_status_factory(project=project)
        custom_attribute = custom_attribute_factory(
            project=project,
            applied_to={
                'testresult': {
                    'is_required': True,
                    'status_specific': [status.pk],
                },
            },
        )
        test = test_factory(project=project)
        result_dict = {
            'status': status.pk,
            'user': user.id,
            'comment': constants.TEST_COMMENT,
            'test': test.id,
            'attributes': {},
        }
        response = api_client.send_request(self.view_name_list, result_dict, HTTPStatus.BAD_REQUEST, RequestType.POST)
        assert response.json()[_ERRORS][0] == MISSING_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG.format([custom_attribute.name])

    def test_status_specific_validation(
        self,
        api_client,
        authorized_superuser,
        custom_attribute_factory,
        project,
        user,
        test_factory,
        result_status_factory,
    ):
        status = result_status_factory(project=project)
        custom_attribute = custom_attribute_factory(
            project=project,
            applied_to={
                'testresult': {
                    'is_required': True,
                    'status_specific': [status.pk],
                },
            },
        )
        test = test_factory(project=project)
        result_dict = {
            'status': result_status_factory(project=project).pk,
            'user': user.id,
            'comment': constants.TEST_COMMENT,
            'test': test.id,
            'attributes': {},
        }
        api_client.send_request(self.view_name_list, result_dict, HTTPStatus.CREATED, RequestType.POST)
        result_dict['status'] = status.pk
        response = api_client.send_request(self.view_name_list, result_dict, HTTPStatus.BAD_REQUEST, RequestType.POST)
        assert response.json()[_ERRORS][0] == MISSING_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG.format([custom_attribute.name])

    def test_test_result_is_created_if_the_required_custom_attribute_is_not_test_result_specific(
        self, api_client, authorized_superuser, custom_attribute_factory, project, user, test_factory,
        allowed_content_types, result_status_factory,
    ):
        expected_number_of_results = 1
        test_result_content_type_id = ContentType.objects.get_for_model(TestResult).id
        allowed_content_types.remove(test_result_content_type_id)
        status = result_status_factory(project=project)
        custom_attribute_factory(
            project=project,
            applied_to={
                'testcase': {
                    'is_required': True,
                    'status_specific': [status.pk],
                },
            },
        )
        test = test_factory(project=project)
        result_dict = {
            'status': status.pk,
            'user': user.id,
            'comment': constants.TEST_COMMENT,
            'test': test.id,
            'attributes': {},
        }
        api_client.send_request(self.view_name_list, result_dict, HTTPStatus.CREATED, RequestType.POST)
        assert TestResult.objects.count() == expected_number_of_results, f'Expected number of cases ' \
                                                                         f'"{expected_number_of_results}" ' \
                                                                         f'actual: "{TestResult.objects.count()}"'

    def test_creation_in_archive_test(
        self, api_client, authorized_superuser, test_factory, user, result_status_factory,
    ):
        test = test_factory(is_archive=True)
        result_dict = {
            'status': result_status_factory(project=test.project).pk,
            'user': user.id,
            'comment': constants.TEST_COMMENT,
            'test': test.id,
        }
        response = api_client.send_request(
            'api:v1:testresult-list',
            expected_status=HTTPStatus.BAD_REQUEST,
            request_type=RequestType.POST,
            data=result_dict,
        )
        assert response.json()['errors'][0] == CREATE_RESULT_IN_ARCHIVE_TEST

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    @pytest.mark.parametrize(
        'is_test_archive, is_result_archive',
        [(True, False), (False, True), (True, True)],
    )
    def test_update_archive_result(
        self,
        api_client,
        authorized_superuser,
        test_factory,
        test_result_factory,
        user,
        request_type,
        is_test_archive,
        is_result_archive,
        result_status_factory,
    ):
        test = test_factory(is_archive=is_test_archive)
        test_result = test_result_factory(
            is_archive=is_result_archive, test=test, status=result_status_factory(project=test.project),
        )
        update_dict = {
            'id': test_result.id,
            'test': test.id,
            'user': user.id,
            'status': result_status_factory(project=test.project).pk,
            'comment': 'new_comment',
        }
        response = api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_result.pk},
            request_type=request_type,
            expected_status=HTTPStatus.BAD_REQUEST,
            data=update_dict,
        )
        assert response.json()['errors'][0] == UPDATE_ARCHIVE_RESULT

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    def test_result_update_forbidden(
        self,
        api_client,
        authorized_superuser,
        test_case,
        test_factory,
        request_type,
        project_factory,
        test_result_factory,
        result_status_factory,
    ):

        project = project_factory(settings={'is_result_editable': False})
        test = test_factory(case=test_case, project=project)
        result = test_result_factory(project=project, test=test, status=result_status_factory(project=project))
        update_dict = {
            'status': result_status_factory(project=project).pk,
            'comment': 'new_comment',
        }
        response = api_client.send_request(
            self.view_name_detail,
            data=update_dict,
            reverse_kwargs={'pk': result.id},
            request_type=RequestType.PATCH,
            expected_status=HTTPStatus.BAD_REQUEST,
        )
        assert response.json()['errors'][0] == error_messages.RESULTS_ARE_NOT_EDITABLE

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    def test_result_with_steps_update_forbidden(
        self,
        api_client,
        authorized_superuser,
        test_case,
        test_factory,
        request_type,
        project_factory,
        test_result_with_steps_factory,
        result_status_factory,
    ):
        project = project_factory(settings={'is_result_editable': False})
        test = test_factory(case=test_case, project=project)
        result = test_result_with_steps_factory(
            project=project, test=test, status=result_status_factory(project=project),
        )
        step_to_update = result.steps_results.first()
        update_dict = {
            'steps_results': [
                {
                    'id': step_to_update.id,
                    'status': result_status_factory(project=project).pk,
                },
            ],
        }
        response = api_client.send_request(
            self.view_name_detail,
            data=update_dict,
            reverse_kwargs={'pk': result.id},
            request_type=RequestType.PATCH,
            expected_status=HTTPStatus.BAD_REQUEST,
        )
        assert response.json()['errors'][0] == error_messages.RESULTS_ARE_NOT_EDITABLE

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    @pytest.mark.parametrize('hours_for_editing', [3600, 7200, 14400])
    def test_result_update_with_any_hours(
        self,
        api_client,
        authorized_superuser,
        test_case,
        test_factory,
        request_type,
        project_factory,
        test_result_factory,
        hours_for_editing,
        result_status_factory,
    ):

        project = project_factory(settings={'is_result_editable': True, 'result_edit_limit': hours_for_editing})
        test = test_factory(case=test_case, project=project)
        now = timezone.now()
        created_at = now - timezone.timedelta(seconds=hours_for_editing) + timezone.timedelta(minutes=1)
        result = test_result_factory(
            project=project, test=test, created_at=created_at, status=result_status_factory(project=project),
        )

        update_dict = {
            'status': result_status_factory(project=project).pk,
            'comment': 'new_comment',
        }

        api_client.send_request(
            self.view_name_detail,
            data=update_dict,
            reverse_kwargs={'pk': result.id},
            request_type=RequestType.PATCH,
            expected_status=HTTPStatus.OK,
        )
        result.refresh_from_db()
        assert result.status.pk == update_dict['status']
        assert result.comment == update_dict['comment']

    def test_delete_by_attributes(self, api_client, authorized_superuser, test, test_result_factory):
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test_result_factory(test=test, attributes={'delete_me': bool(idx % 2)})
        api_client.send_request(
            self.view_name_attributes,
            request_type=RequestType.DELETE,
            expected_status=HTTPStatus.NO_CONTENT,
            query_params={'plan': test.plan.pk, 'attribute_name': 'delete_me', 'attribute_value': True},
        )
        test_results = TestResult.objects.filter(test=test)
        assert test_results.count() == constants.NUMBER_OF_OBJECTS_TO_CREATE // 2
        assert test_results.filter(attributes__delete_me=True).count() == 0, 'Not all results were deleted'

    @pytest.mark.parametrize('deleted_attribute', ['plan', 'attribute_name', 'attribute_value'])
    def test_failed_delete_by_attributes(
        self,
        api_client,
        authorized_superuser,
        test,
        test_result_factory,
        deleted_attribute,
    ):
        query_params = {'plan': test.plan.pk, 'attribute_name': 'delete_me', 'attribute_value': True}
        query_params.pop(deleted_attribute)
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test_result_factory(test=test, attributes={'delete_me': bool(idx % 2)})
        response = api_client.send_request(
            self.view_name_attributes,
            request_type=RequestType.DELETE,
            expected_status=HTTPStatus.BAD_REQUEST,
            query_params=query_params,
        )
        assert response.json()['errors'][0] == ATTRIBUTES_PARAMETER_NOT_PASSED
