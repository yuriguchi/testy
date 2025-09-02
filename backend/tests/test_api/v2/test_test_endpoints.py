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
from contextlib import contextmanager
from http import HTTPStatus
from operator import itemgetter
from unittest import mock
from unittest.mock import Mock

import allure
import pytest

from tests import constants
from tests.commons import RequestType, model_to_dict_via_serializer
from tests.error_messages import PERMISSION_ERR_MSG, REQUIRED_FIELD_MSG
from tests.mock_serializers.v2 import TestMockSerializer
from testy.core.models import Project
from testy.tests_representation.models import Test
from testy.tests_representation.validators import BulkUpdateExcludeIncludeValidator, MoveTestsSameProjectValidator
from testy.users.models import Membership, Role, User


@pytest.mark.django_db
@pytest.mark.usefixtures('mock_tests_channel_layer')
class TestTestEndpoints:
    view_name_list = 'api:v2:test-list'
    view_name_detail = 'api:v2:test-detail'
    view_name_bulk_update = 'api:v2:test-bulk-update'

    def test_list(self, api_client, authorized_superuser, test_factory, project):
        expected_instances = model_to_dict_via_serializer(
            [test_factory(project=project) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)],
            TestMockSerializer,
            many=True,
            refresh_instances=True,
        )
        response = api_client.send_request(self.view_name_list, query_params={'project': project.id})
        assert response.json_strip() == expected_instances

    def test_retrieve(self, api_client, authorized_superuser, test):
        expected_dict = model_to_dict_via_serializer(test, TestMockSerializer, refresh_instances=True)
        response = api_client.send_request(self.view_name_detail, reverse_kwargs={'pk': test.pk})
        actual_dict = response.json()
        assert actual_dict == expected_dict, 'Actual model dict is different from expected'

    def test_partial_update(self, api_client, authorized_superuser, test, user):
        result_dict = {
            'id': test.id,
            'assignee': user.id,
        }
        api_client.send_request(
            self.view_name_detail,
            result_dict,
            request_type=RequestType.PATCH,
            reverse_kwargs={'pk': test.pk},
        )
        result_user = Test.objects.get(pk=test.id).assignee
        assert result_user == user, f'Test user does not match. Expected user "{user}", ' \
                                    f'actual: "{result_user}"'

    @pytest.mark.parametrize('expected_status', [HTTPStatus.OK, HTTPStatus.BAD_REQUEST])
    def test_update(self, api_client, authorized_superuser, expected_status, test, user, test_case, test_plan):
        result_dict = {
            'id': test.id,
            'assignee': user.id,
        }
        if expected_status == HTTPStatus.OK:
            result_dict['case'] = test_case.id
            result_dict['plan'] = test_plan.id

        response = api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test.pk},
            request_type=RequestType.PUT,
            expected_status=expected_status,
            data=result_dict,
        )
        if expected_status == HTTPStatus.OK:
            result_user = Test.objects.get(pk=test.id).assignee
            assert result_user == user, f'Test user does not match. Expected user "{user}", ' \
                                        f'actual: "{result_user}"'
        else:
            assert response.json()['case'][0] == REQUIRED_FIELD_MSG
            assert response.json()['plan'][0] == REQUIRED_FIELD_MSG

    def test_test_cannot_be_deleted(self, api_client, authorized_superuser, test):
        assert Test.objects.count() == 1, 'Test was not created'
        api_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.METHOD_NOT_ALLOWED,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': test.pk},
        )
        assert Test.objects.count(), f'Test with id "{test.id}" was not deleted.'

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    def test_archived_editable_for_admin_only(self, api_client, authorized_superuser, test_factory, user, request_type):
        api_client.force_login(user)
        test = test_factory(is_archive=True)
        response = api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test.pk},
            request_type=request_type,
            expected_status=HTTPStatus.FORBIDDEN,
            data={},
        )
        assert response.json()['detail'] == PERMISSION_ERR_MSG

    @pytest.mark.parametrize('field_name', ['id', 'name', 'is_archive', 'last_status'])
    @pytest.mark.parametrize('descending', [True, False], ids=['desc', 'asc'])
    def test_ordering_pagination(
        self, api_client, authorized_superuser, test_factory, test_result_factory, field_name,
        descending, project, result_status_factory,
    ):
        number_of_pages = 2
        number_of_objects = constants.NUMBER_OF_OBJECTS_TO_CREATE_PAGE * number_of_pages
        tests = [test_factory(is_archive=idx % 2, project=project) for idx in range(number_of_objects)]
        status_list = [
            result_status_factory(project=project),
            result_status_factory(project=project),
            result_status_factory(project=project),
        ]
        for idx, expected_instance in enumerate(tests):
            status = status_list[idx % 3]
            expected_instance.last_status = status
            expected_instance.name = expected_instance.case.name
            test_result_factory(test=expected_instance, status=status)
        if field_name == 'last_status':
            field = 'last_status_id'
        else:
            field = field_name
        expected_instances = model_to_dict_via_serializer(
            sorted(tests, key=lambda instance: getattr(instance, field), reverse=descending),
            TestMockSerializer,
            many=True,
            refresh_instances=True,
        )

        for page_number in range(1, number_of_pages + 1):
            response = api_client.send_request(
                self.view_name_list,
                query_params={
                    'ordering': f'{"-" if descending else ""}{field_name}',
                    'is_archive': True,
                    'page': page_number,
                    'project': project.id,
                },
            )
            response_dict = response.json()['results']

            assert len(response_dict) == constants.NUMBER_OF_OBJECTS_TO_CREATE_PAGE
            for expected_instance, actual_instance in zip(
                expected_instances[:99] if page_number == 1 else expected_instances[100:],
                response.json()['results'],
            ):
                assert expected_instance[field_name] == actual_instance[field_name]

    def test_search(self, api_client, authorized_superuser, test_factory, test_case_factory, project):
        number_of_cases = 2
        test_cases = [test_case_factory(), test_case_factory()]
        tests = [[], []]
        expected_instances = []
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            if idx % 2:
                tests[0].append(test_factory(case=test_cases[0], project=project))
            else:
                tests[1].append(test_factory(case=test_cases[1], project=project))

        for idx in range(number_of_cases):
            expected_instances.append(
                model_to_dict_via_serializer(tests[idx], TestMockSerializer, many=True, refresh_instances=True),
            )

        for idx in range(number_of_cases):
            response = api_client.send_request(
                self.view_name_list,
                query_params={
                    'search': test_cases[idx].name,
                    'is_archive': True,
                    'project': project.id,
                },
            )
            response_dict = response.json()['results']
            assert sorted(expected_instances[idx], key=itemgetter('id')) == sorted(response_dict, key=itemgetter('id'))

    def test_last_status_filter(
        self,
        api_client,
        authorized_superuser, test_factory,
        test_result_factory,
        project,
        result_status_factory,
    ):
        expected_instances = []
        result_statuses = [result_status_factory(project=project) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
        for status in result_statuses:
            test = test_factory(project=project)
            test.last_status = status
            test_result_factory(test=test, status=status)
            expected_instances.append(
                model_to_dict_via_serializer(test, TestMockSerializer, many=False, refresh_instances=True),
            )

        for expected_instance, status in zip(expected_instances, result_statuses):
            response = api_client.send_request(
                self.view_name_list,
                query_params={
                    'last_status': status.pk,
                    'project': project.id,
                },
            )
            assert response.json()['results'] == [expected_instance], f'Filter by {status.name} unexpected json'

    @pytest.mark.parametrize('page_size', [1, 2, 5])
    def test_page_size(self, api_client, authorized_superuser, test_factory, page_size, project):
        expected_number_of_pages = constants.NUMBER_OF_OBJECTS_TO_CREATE // page_size
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test_factory(project=project)
        response = api_client.send_request(
            self.view_name_list,
            query_params={'page_size': page_size, 'project': project.id},
        )
        assert expected_number_of_pages == response.json()['pages']['total']

    def test_suite_path(
        self,
        api_client,
        authorized_superuser,
        test_factory,
        test_suite_factory,
        project,
        test_case_factory,
    ):
        parent = None
        expected_suites = []
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            parent = test_suite_factory(parent=parent, project=project)
            parent.refresh_from_db()
            expected_suites.append(parent)
        test_case = test_case_factory(suite=expected_suites[-1])
        test = test_factory(case=test_case)
        expected_dict = model_to_dict_via_serializer(test, TestMockSerializer, refresh_instances=True)
        response = api_client.send_request(self.view_name_detail, reverse_kwargs={'pk': test.pk})
        actual_dict = response.json()
        assert '/'.join(suite.name for suite in expected_suites) == actual_dict['suite_path'], 'Wrong suite path'
        assert actual_dict == expected_dict, 'Actual model dict is different from expected'

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
    def test_list_with_labels(
        self,
        api_client,
        authorized_superuser,
        cases_with_labels,
        label_indexes,
        not_labels_indexes,
        labels_condition,
        number_of_items,
        project,
    ):
        labels, cases, test_plan, _ = cases_with_labels
        query_params = {'plan': test_plan.id, 'project': project.id}
        if label_indexes:
            query_params['labels'] = ','.join([str(labels[i].id) for i in label_indexes])
        if not_labels_indexes:
            query_params['not_labels'] = ','.join([str(labels[i].id) for i in not_labels_indexes])
        query_params['labels_condition'] = labels_condition
        content = api_client.send_request(
            self.view_name_list,
            query_params=query_params,
        ).json()
        assert content.get('count') == number_of_items

    @pytest.mark.parametrize('payload_key', ['included_tests', 'excluded_tests'])
    @pytest.mark.parametrize('update_key', ['plan', 'assignee'])
    @mock.patch('testy.root.celery.app.send_task', new=Mock())
    def test_bulk_update_tests(
        self,
        api_client,
        authorized_superuser,
        project,
        test_plan_factory,
        test_factory,
        user,
        update_key,
        payload_key,
    ):

        first_plan = test_plan_factory(project=project)
        if update_key == 'plan':
            update_value = test_plan_factory(project=project).pk
        elif update_key == 'assignee':
            update_value = user.pk
        payload = {update_key: update_value}
        tests_pk = []
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test = test_factory(project=project, plan=first_plan)
            tests_pk.append(test.pk)
        tests_in_payload = tests_pk[:constants.NUMBER_OF_OBJECTS_TO_CREATE // 2]
        api_client.send_request(
            self.view_name_bulk_update,
            {'current_plan': first_plan.pk, payload_key: tests_in_payload, **payload},
            HTTPStatus.OK,
            RequestType.PUT,
        )
        if payload_key == 'included_tests':
            affected_tests_pks = tests_pk[:constants.NUMBER_OF_OBJECTS_TO_CREATE // 2]
        else:
            affected_tests_pks = tests_pk[constants.NUMBER_OF_OBJECTS_TO_CREATE // 2:]
        expected_count = constants.NUMBER_OF_OBJECTS_TO_CREATE // 2
        actual_count = Test.objects.filter(pk__in=affected_tests_pks, **payload).count()
        assert actual_count == expected_count

    @mock.patch('testy.root.celery.app.send_task', new=Mock())
    def test_bulk_update_plan_forbidden(
        self,
        api_client,
        authorized_superuser,
        project,
        test_plan_factory,
        test_factory,
    ):
        test_plan = test_plan_factory()
        second_plan = test_plan_factory(project=project)

        tests_pk = []
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            tests_pk.append(test_factory(plan=test_plan, project=test_plan.project).pk)
        assert test_plan.project != second_plan.project
        response = api_client.send_request(
            self.view_name_bulk_update,
            {'plan': second_plan.pk, 'included_tests': tests_pk, 'current_plan': test_plan.pk},
            HTTPStatus.BAD_REQUEST,
            RequestType.PUT,
        )
        assert MoveTestsSameProjectValidator.err_msg.format(second_plan.project.name) in response.json()['errors']

    @mock.patch('testy.root.celery.app.send_task', new=Mock())
    def test_bulk_update_plan_both_include_exclude(
        self,
        api_client,
        authorized_superuser,
        test_plan,
        test_factory,
    ):
        include = []
        exclude = []
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            include.append(test_factory(plan=test_plan, project=test_plan.project).pk)
            exclude.append(test_factory(plan=test_plan, project=test_plan.project).pk)
        response = api_client.send_request(
            self.view_name_bulk_update,
            {'included_tests': include, 'excluded_tests': exclude, 'current_plan': test_plan.pk},
            HTTPStatus.BAD_REQUEST,
            RequestType.PUT,
        )
        assert BulkUpdateExcludeIncludeValidator.err_msg in response.json()['errors']

    @mock.patch('testy.root.celery.app.send_task', new=Mock())
    @pytest.mark.parametrize(
        'filter_keys',
        [
            ('search',),
            ('last_status',),
            ('labels',),
            ('not_labels',),
            ('assignee',),
            ('unassigned',),
            ('suite',),
            ('suite', 'search'),
            ('suite', 'labels'),
            ('suite', 'last_status'),
            ('suite', 'last_status', 'labels'),
            ('suite', 'labels', 'assignee', 'last_status'),
        ],
    )
    def test_bulk_update_tests_with_filters(
        self,
        api_client,
        authorized_superuser,
        project,
        test_plan_factory,
        test_factory,
        user_factory,
        test_suite_factory,
        test_case_factory,
        labeled_item_factory,
        filter_keys,
        test_result_factory,
        result_status_factory,
    ):
        case_name_for_search = 'case_name_for_search'
        status_for_search = result_status_factory(project=project)
        suite_for_search = test_suite_factory()
        case = test_case_factory(suite=suite_for_search, name=case_name_for_search)
        assignee = user_factory()
        new_assignee_id = user_factory().id
        labels_for_search = []
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            labeled_item = labeled_item_factory(content_object=case)
            labels_for_search.append(str(labeled_item.label.id))
        filter_parameters = {
            'unassigned': True,
            'assignee': str(new_assignee_id),
            'search': case_name_for_search,
            'labels': labels_for_search,
            'not_labels': labels_for_search,
            'suite': str(suite_for_search.id),
            'last_status': str(status_for_search.pk),
        }
        first_plan = test_plan_factory(project=project)
        tests_pk = []
        negative_tests_pk = []
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            if idx % 2:
                test = test_factory(
                    project=project,
                    plan=first_plan,
                    case=case,
                    assignee=assignee,
                )
                test_result_factory(test=test, status=status_for_search)
                tests_pk.append(test.pk)
            else:
                negative_tests_pk.append(test_factory().pk)

        response_body = api_client.send_request(
            self.view_name_bulk_update,
            {
                'current_plan': first_plan.pk,
                'filter_conditions': {filter_key: filter_parameters[filter_key] for filter_key in filter_keys},
                'include_tests': tests_pk + negative_tests_pk,
                'assignee': new_assignee_id,
            },
            HTTPStatus.OK,
            RequestType.PUT,
        ).json()
        if 'not_labels' in filter_keys:
            affected_tests_pks = negative_tests_pk
        else:
            affected_tests_pks = tests_pk
        for actual_test in response_body:
            assert actual_test['id'] in affected_tests_pks, f'Missing test {actual_test["id"]}'
            assert actual_test['assignee'] == new_assignee_id, f'Assignee was not changed: {actual_test["assignee"]}'

    def test_foreign_assignee_not_allowed(
        self,
        user,
        test_factory,
        project_factory,
        member,
        authorized_client,
        authorized_superuser_client,
    ):
        project = project_factory(is_private=True)
        test = test_factory(project=project)
        authorized_superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test.pk},
            data={'assignee': user.id},
            request_type=RequestType.PATCH,
            expected_status=HTTPStatus.BAD_REQUEST,
        )
        with self._role(project, user, member):
            authorized_superuser_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': test.pk},
                data={'assignee': user.id},
                request_type=RequestType.PATCH,
                expected_status=HTTPStatus.OK,
            )

    def test_external_assignation_user_to_public_project(
        self,
        external,
        user,
        test_factory,
        project_factory,
        authorized_client,
        authorized_superuser_client,
    ):

        project = project_factory()
        test = test_factory(project=project)
        with self._role(None, user, external):
            authorized_superuser_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': test.pk},
                data={'assignee': user.id},
                request_type=RequestType.PATCH,
                expected_status=HTTPStatus.BAD_REQUEST,
            )

    @mock.patch('testy.root.celery.app.send_task', new=Mock())
    def test_bulk_assignation_validation(
        self,
        authorized_superuser_client,
        project_factory,
        test_plan_factory,
        test_factory,
        user,
        member,
    ):
        project = project_factory(is_private=True)
        plan = test_plan_factory(project=project)
        tests_pk = []
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test = test_factory(project=project, plan=plan)
            tests_pk.append(test.pk)
        authorized_superuser_client.send_request(
            self.view_name_bulk_update,
            data={'current_plan': plan.pk, 'assignee': user.pk},
            expected_status=HTTPStatus.BAD_REQUEST,
            request_type=RequestType.PUT,
        )
        with self._role(project, user, member):
            authorized_superuser_client.send_request(
                self.view_name_bulk_update,
                data={'current_plan': plan.pk, 'assignee': user.pk},
                expected_status=HTTPStatus.OK,
                request_type=RequestType.PUT,
            )

    @contextmanager
    def _role(self, project: Project, user: User, role: Role):
        with allure.step(f'Sending request as user: {user} with role: {role} for {project}'):
            membership = Membership.objects.create(project=project, user=user, role=role)
            try:
                yield
            finally:
                membership.hard_delete()
