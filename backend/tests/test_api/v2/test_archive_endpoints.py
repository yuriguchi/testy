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
from testy.tests_representation.models import Test, TestCase, TestPlan, TestResult


@pytest.mark.django_db
class TestArchiveEndpoints:
    archive_preview_view_name = 'api:v2:{0}-archive-preview'
    archive_view_name = 'api:v2:{0}-archive-commit'
    archive_restore_view_name = 'api:v2:{0}-archive-restore'

    model_to_key = [
        [Project, 'project'],
        [TestPlan, 'testplan'],
        [TestCase, 'testcase'],
        [Test, 'test'],
        [TestResult, 'result'],
    ]

    @pytest.mark.parametrize(
        'instances_key, expected_objects_diff, idxs_for_deletion',
        [
            ('project', [1, 11, 2, 40, 400], [-1]),
            ('testplan', [0, 1, 0, 20, 200], [-1]),
            ('testplan', [0, 2, 0, 20, 200], [-1, -2]),
            ('test', [0, 0, 0, 1, 10], [-1]),
            ('testcase', [0, 0, 2, 40, 400], [-1, -2]),
        ],
    )
    def test_data_cascade_recovery(
        self, api_client, authorized_superuser, data_for_cascade_tests_behaviour,
        instances_key, expected_objects_diff, idxs_for_deletion,
    ):
        expected_objects, objects_count = data_for_cascade_tests_behaviour
        expected_objects.pop('testsuite')
        test_mapping = deepcopy(self.model_to_key)
        for elem, object_diff in zip(test_mapping, expected_objects_diff):
            elem.append(object_diff)

        for idx in idxs_for_deletion:
            api_client.send_request(
                self.archive_view_name.format(instances_key),
                reverse_kwargs={'pk': expected_objects[instances_key][idx].id},
                request_type=RequestType.POST,
            )
        for model, key, objects_number_diff in test_mapping:
            assert model.objects.filter(is_archive=False).count() == objects_count[key] - objects_number_diff, \
                f'Count of objects of model {model} did not match expected'
        api_client.send_request(
            self.archive_restore_view_name.format(instances_key),
            data={
                'instance_ids': [expected_objects[instances_key][idx].id for idx in idxs_for_deletion],
            },
            request_type=RequestType.POST,
            expected_status=HTTPStatus.OK,
        )

        for model, key in self.model_to_key:
            assert model.objects.count() == objects_count[key], f'Objects with model {model} were not restored'

        self._validate_restored_objects(expected_objects)

    @pytest.mark.parametrize(
        'instances_key, expected_objects_diff, idx_for_deletion',
        [
            ('project', [1, 11, 2, 40, 400], -1),
            ('testplan', [0, 1, 0, 20, 200], -1),
            ('test', [0, 0, 0, 1, 10], -1),
            ('testcase', [0, 0, 1, 20, 200], -1),
        ],
    )
    def test_archive_preview(
        self, api_client, authorized_superuser, data_for_cascade_tests_behaviour,
        instances_key, expected_objects_diff, idx_for_deletion, use_dummy_cache_backend,
    ):
        expected_objects, objects_count = data_for_cascade_tests_behaviour
        expected_objects.pop('testsuite')
        test_mapping = deepcopy(self.model_to_key)
        for elem, object_diff in zip(test_mapping, expected_objects_diff):
            elem.append(object_diff)
        response = api_client.send_request(
            self.archive_preview_view_name.format(instances_key),
            reverse_kwargs={'pk': expected_objects[instances_key][idx_for_deletion].id},
        )
        assert response.cookies.get('archive_cache'), 'No cache was set'
        content = response.json()
        verbose_name_mapping = {
            'testplan': 'test plans',
            'project': 'projects',
            'test': 'tests',
            'result': 'test results',
            'testcase': 'test cases',
        }
        len_affected_objects = len([expected_diff for expected_diff in expected_objects_diff if expected_diff > 0])

        assert len_affected_objects == len(content), 'Number of lack objects does not match'
        for _, key, objects_number_diff in test_mapping:
            verbose_name = verbose_name_mapping[key]
            for elem in content:
                if elem['verbose_name'] == verbose_name:
                    assert objects_number_diff == elem['count'], f'Objects count is wrong for {verbose_name}'
                    break

        self._validate_restored_objects(expected_objects)

    def _validate_restored_objects(self, expected_objects):
        actual_objects = {
            'project': [],
            'testplan': [],
            'test': [],
            'result': [],
            'case': [],
        }
        for model, key in self.model_to_key:
            actual_objects[key] = list(model.objects.all())

        for objects in expected_objects.values():
            objects.sort(key=lambda instance: instance.id)

        for objects in actual_objects.values():
            objects.sort(key=lambda instance: instance.id)

        for _, key in self.model_to_key:
            for expected_object, actual_object in zip(actual_objects[key], expected_objects[key]):
                assert expected_object.is_archive == actual_object.is_archive
