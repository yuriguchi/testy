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
from copy import deepcopy
from http import HTTPStatus

import pytest

from tests.commons import RequestType
from testy.core.models import Project
from testy.tests_description.models import TestCase, TestSuite
from testy.tests_representation.models import Test, TestPlan, TestResult


@pytest.mark.django_db
class TestRecovery:
    view_name_list = 'api:v2:recovery-list'
    deleted_list_view = 'api:v2:{0}-deleted-list'
    recovery_view_name = 'api:v2:{0}-deleted-recover'
    delete_permanent_view_name = 'api:v2:{0}-deleted-remove'
    remove_view_name = 'api:v2:remove-permanently'
    project_view_name_detail = 'api:v2:project-detail'
    case_view_name_detail = 'api:v2:testcase-detail'
    plan_view_name_detail = 'api:v2:testplan-detail'
    suite_view_name_detail = 'api:v2:testsuite-detail'

    model_to_key = [
        [Project, 'project'],
        [TestPlan, 'testplan'],
        [Test, 'test'],
        [TestResult, 'result'],
        [TestCase, 'testcase'],
        [TestSuite, 'testsuite'],
    ]

    @pytest.mark.parametrize(
        'string_to_model',
        [('project', Project), ('testplan', TestPlan), ('testcase', TestCase), ('testsuite', TestSuite)],
        ids=['project', 'plan', 'case', 'suite'],
    )
    def test_deleted_list(self, api_client, authorized_superuser, data_for_cascade_tests_behaviour, string_to_model):
        model_str, model_class = string_to_model
        model_class.objects.all().delete()
        view_name = self.deleted_list_view.format(model_str)
        content = api_client.send_request(view_name).json()
        assert model_class.deleted_objects.count() == content['count']

    @pytest.mark.parametrize(
        'instances_key, expected_objects_diff, model_query_param, detail_view, idxs_for_deletion',
        [
            ('project', [1, 11, 40, 400, 2, 1], 0, project_view_name_detail, [-1]),
            ('testplan', [0, 1, 20, 200, 0, 0], 3, plan_view_name_detail, [-1]),
            ('testcase', [0, 0, 20, 200, 1, 0], 2, case_view_name_detail, [-1]),
            ('testsuite', [0, 0, 40, 400, 2, 1], 1, suite_view_name_detail, [-1]),
            ('testplan', [0, 2, 20, 200, 0, 0], 3, plan_view_name_detail, [-1, -2]),
            ('testcase', [0, 0, 40, 400, 2, 0], 2, case_view_name_detail, [-1, -2]),
        ],
        ids=['projects', 'plans', 'cases', 'suites', 'several plans', 'several cases'],
    )
    def test_data_cascade_recovery(
        self, api_client, authorized_superuser, data_for_cascade_tests_behaviour,
        instances_key, expected_objects_diff, model_query_param, detail_view,
        idxs_for_deletion,
    ):
        expected_objects, objects_count = data_for_cascade_tests_behaviour
        test_mapping = deepcopy(self.model_to_key)
        for elem, object_diff in zip(test_mapping, expected_objects_diff):
            elem.append(object_diff)
        for idx in idxs_for_deletion:
            api_client.send_request(
                detail_view,
                reverse_kwargs={'pk': expected_objects[instances_key][idx].id},
                expected_status=HTTPStatus.NO_CONTENT,
                request_type=RequestType.DELETE,
            )

        for model, key, objects_number_diff in test_mapping:
            assert model.objects.count() == objects_count[key] - objects_number_diff, f'Count of objects of ' \
                                                                                      f'model {model} did not match' \
                                                                                      f'expected'
        api_client.send_request(
            self.recovery_view_name.format(instances_key),
            data={
                'model': model_query_param,
                'instance_ids': [expected_objects[instances_key][idx].id for idx in idxs_for_deletion],
            },
            request_type=RequestType.POST,
        )

        for model, key in self.model_to_key:
            assert model.objects.count() == objects_count[key], f'Objects with model {model} were not restored'

        self._validate_restored_objects(expected_objects)

    @pytest.mark.parametrize(
        'instances_key, expected_objects_diff, model_key, detail_view, idxs_for_deletion',
        [
            ('project', [1, 11, 40, 400, 2, 1], 0, project_view_name_detail, [-1]),
            ('testplan', [0, 1, 20, 200, 0, 0], 3, plan_view_name_detail, [-1]),
            ('testcase', [0, 0, 20, 200, 1, 0], 2, case_view_name_detail, [-1]),
            ('testsuite', [0, 0, 40, 400, 2, 1], 1, suite_view_name_detail, [-1]),
            ('testplan', [0, 2, 20, 200, 0, 0], 3, plan_view_name_detail, [-1, -2]),
            ('testcase', [0, 0, 40, 400, 2, 0], 2, case_view_name_detail, [-1, -2]),
        ],
        ids=['projects', 'plans', 'cases', 'suites', 'several plans', 'several cases'],
    )
    def test_data_permanent_deletion(
        self, api_client, authorized_superuser, data_for_cascade_tests_behaviour,
        instances_key, expected_objects_diff, model_key, detail_view,
        idxs_for_deletion,
    ):
        expected_objects, objects_count = data_for_cascade_tests_behaviour
        test_mapping = deepcopy(self.model_to_key)
        for elem, object_diff in zip(test_mapping, expected_objects_diff):
            elem.append(object_diff)
        for idx in idxs_for_deletion:
            api_client.send_request(
                detail_view,
                reverse_kwargs={'pk': expected_objects[instances_key][idx].id},
                expected_status=HTTPStatus.NO_CONTENT,
                request_type=RequestType.DELETE,
            )

        for model, key, objects_number_diff in test_mapping:
            assert model.objects.count() == objects_count[key] - objects_number_diff, f'Count of objects of ' \
                                                                                      f'model {model} did not match' \
                                                                                      f'expected'
        api_client.send_request(
            self.delete_permanent_view_name.format(instances_key),
            data={
                'model': model_key,
                'instance_ids': [expected_objects[instances_key][idx].id for idx in idxs_for_deletion],
            },
            request_type=RequestType.POST,
            expected_status=HTTPStatus.NO_CONTENT,
        )

        for model, _ in self.model_to_key:
            assert not model.deleted_objects.count()

    def _validate_restored_objects(self, expected_objects):
        actual_objects = {
            'project': [],
            'testplan': [],
            'testsuite': [],
            'testcase': [],
            'test': [],
            'result': [],
        }
        for model, key in self.model_to_key:
            actual_objects[key] = list(model.objects.all())

        for objects in expected_objects.values():
            objects.sort(key=lambda instance: instance.id)

        for objects in actual_objects.values():
            objects.sort(key=lambda instance: instance.id)

        assert expected_objects == actual_objects, 'Some objects were restored with different content'
