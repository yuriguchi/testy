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
from http import HTTPStatus

import pytest

from tests import constants
from tests.commons import model_to_dict_via_serializer
from tests.mock_serializers.v1 import TestCaseMockSerializer, TestMockSerializer
from testy.tests_description.api.v1.serializers import TestSuiteSerializer
from testy.tests_representation.api.v1.serializers import (
    ParameterSerializer,
    TestPlanOutputSerializer,
    TestResultSerializer,
)


@pytest.mark.django_db
class TestCommonFeatures:
    project_list_view = 'api:v1:project-list'
    plan_list_view = 'api:v1:testplan-list'
    test_list_view = 'api:v1:test-list'
    result_list_view = 'api:v1:testresult-list'

    @pytest.mark.parametrize(
        'factory_name, view_name, serializer_class, is_paginated', [
            ('test_case_factory', 'api:v1:testcase-list', TestCaseMockSerializer, True),
            ('test_suite_factory', 'api:v1:testsuite-list', TestSuiteSerializer, True),
            ('test_plan_factory', 'api:v1:testplan-list', TestPlanOutputSerializer, True),
            ('test_factory', 'api:v1:test-list', TestMockSerializer, True),
            ('parameter_factory', 'api:v1:parameter-list', ParameterSerializer, False),
            ('test_result_factory', 'api:v1:testresult-list', TestResultSerializer, False),
        ], ids=['Test case', 'Test suite', 'Test plan', 'Test', 'Parameter', 'Test result'],
    )
    def test_project_filter(
        self, api_client, authorized_superuser, factory_name, project_factory, view_name,
        serializer_class, request, is_paginated,
    ):
        factory = request.getfixturevalue(factory_name)
        project1 = project_factory()
        project2 = project_factory()
        parent_to_expected_list = [
            (project1, [factory(project=project1) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]),
            (project2, [factory(project=project2) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]),
        ]
        for project, expected_instances in parent_to_expected_list:
            response = api_client.send_request(
                view_name,
                expected_status=HTTPStatus.OK,
                query_params={
                    'project': project.id,
                },
            )
            expected_dictionaries = (
                model_to_dict_via_serializer(expected_instances, serializer_class, many=True)
                .sort(key=operator.itemgetter('id'))
            )
            data = response.json()
            actual_data = (data['results'] if is_paginated else data).sort(key=operator.itemgetter('id'))
            assert actual_data == expected_dictionaries

    @pytest.mark.parametrize(
        'factory_name, filter_name_factory_pair, view_name, serializer_class, is_paginated',
        [
            ('test_case_factory', ('suite', 'test_suite_factory'), 'api:v1:testcase-{0}', TestCaseMockSerializer, True),
            ('test_factory', ('plan', 'test_plan_factory'), 'api:v1:test-{0}', TestMockSerializer, True),
            ('test_result_factory', ('test', 'test_factory'), 'api:v1:testresult-{0}', TestResultSerializer, False),
        ],
        ids=['Test case', 'Test suite', 'Test result'],
    )
    def test_filter_classes(
        self, api_client, authorized_superuser, project, factory_name, filter_name_factory_pair,
        view_name, serializer_class, request, is_paginated,
    ):

        filter_name, parent_factory_name = filter_name_factory_pair
        factory = request.getfixturevalue(factory_name)
        filter_factory = request.getfixturevalue(parent_factory_name)
        parent_object1 = filter_factory()
        parent_object2 = filter_factory()
        list_view_name = view_name.format('list')
        detail_view_name = view_name.format('detail')
        expected_instances_parent_1 = []
        expected_instances_parent_2 = []

        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            expected_instances_parent_1.append(
                factory(project=project, **{filter_name: parent_object1}),
            )
            expected_instances_parent_2.append(
                factory(project=project, **{filter_name: parent_object2}),
            )

        api_client.send_request(
            detail_view_name,
            expected_status=HTTPStatus.OK,
            reverse_kwargs={'pk': expected_instances_parent_1[0].id},
        )
        parent_to_expected_list = [
            (parent_object1, expected_instances_parent_1),
            (parent_object2, expected_instances_parent_2),
        ]
        for parent_object, expected_instances in parent_to_expected_list:
            response = api_client.send_request(
                list_view_name,
                expected_status=HTTPStatus.OK,
                query_params={
                    'project': project.id,
                    filter_name: parent_object.id,
                },
            )
            expected_dictionaries = (
                model_to_dict_via_serializer(expected_instances, serializer_class, many=True)
                .sort(key=operator.itemgetter('id'))
            )
            data = response.json()
            actual_data = (data['results'] if is_paginated else data).sort(key=operator.itemgetter('id'))
            assert actual_data == expected_dictionaries

    @pytest.mark.parametrize('is_archive_flag', [None, 0, 1], ids=['No flag', 'Negative flag', 'Positive flag'])
    @pytest.mark.parametrize(
        'factory_name, view',
        [
            ('project_factory', project_list_view),
            ('test_plan_factory', plan_list_view),
            ('test_factory', test_list_view),
        ],
        ids=['Project view', 'Test plan view', 'Test view'],
    )
    def test_archive_filter(
        self, api_client, authorized_superuser, factory_name, view, project, request,
        is_archive_flag,
    ):
        factory = request.getfixturevalue(factory_name)

        factory_args_archive = {'project': project}
        factory_args = {'project': project}
        query_params = {'project': project.id}
        if is_archive_flag is not None:
            query_params['is_archive'] = is_archive_flag
        expected_number_of_objects = constants.NUMBER_OF_OBJECTS_TO_CREATE
        if factory_name == 'project_factory':
            for elem in [factory_args, factory_args_archive, query_params]:
                elem.pop('project')
            expected_number_of_objects += 1
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            factory(is_archive=bool(idx % 2), **factory_args_archive)
        content = api_client.send_request(
            view,
            query_params=query_params,
        ).json()
        if isinstance(content, dict):
            content = content['results']
        if is_archive_flag:
            assert len(content) == expected_number_of_objects, 'Not all objects were given with is_archive True.'
        else:
            for elem in content:
                assert not elem['is_archive'], 'Got archived instance when is_archive False or not provided.'

    @pytest.mark.parametrize('is_archive_flag', [None, 0, 1], ids=['No flag', 'Negative flag', 'Positive flag'])
    def test_archive_treeview(self, api_client, authorized_superuser, test_plan_factory, project, is_archive_flag):
        zero_level_plan = test_plan_factory(project=project)

        first_level_plans = [
            test_plan_factory(parent=zero_level_plan, project=project, is_archive=bool(idx % 2))
            for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)
        ]

        for first_level_plan in first_level_plans:
            test_plan_factory(parent=first_level_plan, project=project)
            test_plan_factory(parent=first_level_plan, project=project, is_archive=True)
        query_params = {
            'treeview': 1,
            'project': project.id,
        }
        if query_params is not None:
            query_params['is_archive'] = is_archive_flag
        content = api_client.send_request(
            self.plan_list_view,
            query_params=query_params,
        ).json()['results']
        if not is_archive_flag:  # noqa: WPS504
            for plan_lvl_0 in content:
                assert not plan_lvl_0['is_archive'], 'Not archived plan was found at 0 depth'
                for plan_lvl_1 in plan_lvl_0['children']:
                    assert not plan_lvl_1['is_archive'], 'Not archived plan was found at 1 depth'
                    for plan_lvl_2 in plan_lvl_1['children']:
                        assert not plan_lvl_2['is_archive'], 'Not archived plan was found at 2 depth'
        else:
            for plan_lvl_0 in content:
                assert len(plan_lvl_0['children']) == constants.NUMBER_OF_OBJECTS_TO_CREATE, 'Numbers of plan did ' \
                                                                                             'not match at depth 1'
                for plan_lvl_1 in plan_lvl_0['children']:
                    assert len(plan_lvl_1['children']) == 2, 'Numbers of plan did not match at depth 2'
