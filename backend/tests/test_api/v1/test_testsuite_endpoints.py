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
import json
import re
from copy import deepcopy
from http import HTTPStatus
from typing import Any, Iterable

import allure
import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet

from tests import constants
from tests.commons import RequestType, model_to_dict_via_serializer
from tests.error_messages import REQUIRED_FIELD_MSG
from tests.mock_serializers.v1 import (
    TestSuiteBaseMockSerializer,
    TestSuiteMockTreeSerializer,
    TestSuiteRetrieveMockSerializer,
)
from testy.core.models import Attachment, Label, LabeledItem
from testy.tests_description.api.v1.serializers import TestSuiteTreeSerializer
from testy.tests_description.models import TestCase, TestCaseStep, TestSuite
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.utilities.sql import get_max_level
from testy.utilities.tree import form_tree_prefetch_objects


@pytest.mark.django_db(reset_sequences=True, transaction=True)
@allure.parent_suite('Test suites')
@allure.suite('Integration tests')
@allure.sub_suite('Endpoints')
class TestSuiteEndpoints:
    view_name_list = 'api:v1:testsuite-list'
    view_name_detail = 'api:v1:testsuite-detail'
    view_name_copy = 'api:v1:testsuite-copy'

    @allure.title('Test list display')
    def test_list(self, superuser_client, test_suite_factory, project):
        with allure.step(f'Generate {constants.NUMBER_OF_OBJECTS_TO_CREATE_PAGE} test suites'):
            instances = [test_suite_factory(project=project) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
            expected_json = model_to_dict_via_serializer(
                instances,
                TestSuiteBaseMockSerializer,
                many=True,
                refresh_instances=True,
            )
        response = superuser_client.send_request(self.view_name_list, query_params={'project': project.id}).json_strip()
        with allure.step('Validate response is matching expected data'):
            assert expected_json == response

    @allure.title('Test detail display')
    def test_retrieve(self, superuser_client, test_suite):
        expected_dict = model_to_dict_via_serializer(
            test_suite,
            TestSuiteRetrieveMockSerializer,
            refresh_instances=True,
        )
        response = superuser_client.send_request(self.view_name_detail, reverse_kwargs={'pk': test_suite.pk})
        actual_dict = response.json()
        with allure.step('Validate response is matching expected data'):
            assert actual_dict == expected_dict, 'Actual model dict is different from expected'

    @allure.title('Test creation')
    def test_creation(self, superuser_client, project):
        expected_number_of_suites = 1
        suite_dict = {
            'name': constants.TEST_CASE_NAME,
            'project': project.id,
        }
        superuser_client.send_request(self.view_name_list, suite_dict, HTTPStatus.CREATED, RequestType.POST)
        with allure.step('Validate object was created'):
            assert TestSuite.objects.count() == expected_number_of_suites, f'Expected number of users ' \
                                                                           f'"{expected_number_of_suites}"' \
                                                                           f'actual: "{TestSuite.objects.count()}"'

    @pytest.mark.parametrize(
        'request_type',
        [RequestType.PATCH, RequestType.PUT],
        ids=['partial update', 'update'],
    )
    def test_update(self, test_suite, superuser_client, project, request_type, request):
        allure.dynamic.title(f'Test {request.node.callspec.id}')
        new_name = 'new_expected_test_case_name'
        suite_dict = {
            'id': test_suite.id,
            'name': new_name,
            'project': project.id,
        }
        superuser_client.send_request(
            self.view_name_detail,
            suite_dict,
            request_type=request_type,
            reverse_kwargs={'pk': test_suite.pk},
        )
        actual_name = TestSuite.objects.get(pk=test_suite.id).name
        with allure.step('Validate name was updated'):
            assert actual_name == new_name, f'Suite names do not match. Expected name "{actual_name}", ' \
                                            f'actual: "{new_name}"'

    @allure.title('Test partial update on put not allowed')
    def test_required_fields_on_update(self, superuser_client, test_suite):
        new_name = 'new_expected_test_case_name'
        suite_dict = {
            'id': test_suite.id,
            'name': new_name,
        }
        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': test_suite.pk},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.BAD_REQUEST,
            data=suite_dict,
        )
        with allure.step('Validate error message'):
            assert response.json()['project'][0] == REQUIRED_FIELD_MSG

    @allure.title('Test deletion')
    def test_delete(self, superuser_client, test_suite):
        with allure.step('Validate suite created'):
            assert TestSuite.objects.count() == 1, 'Test suite was not created'
        superuser_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': test_suite.pk},
        )
        with allure.step('Validate suite was deleted'):
            assert not TestSuite.objects.count(), f'Test suite with id "{test_suite.id}" was not deleted.'

    @pytest.mark.parametrize('user_fixture', ['user', 'superuser'], ids=['from user', 'from superuser'])
    @pytest.mark.parametrize('is_project_specified', [False, True], ids=['project not specified', 'project specified'])
    @pytest.mark.parametrize('is_name_specified', [False, True], ids=['new name not specified', 'new name specified'])
    @pytest.mark.parametrize('is_suite_specified', [False, True], ids=['suite not specified', 'suite is specified'])
    def test_suites_copy(
        self,
        api_client,
        test_suite_factory,
        project_factory,
        test_case_factory,
        test_case_with_steps_factory,
        attachment_factory,
        labeled_item_factory,
        is_suite_specified,
        is_project_specified,
        is_name_specified,
        request,
        user_fixture,
    ):
        user = request.getfixturevalue(user_fixture)
        api_client.force_login(user)
        allure.dynamic.title(f'Test suite copy with {request.node.callspec.id}')
        attach_reference = 'Some useful text about cats ![](https://possible-host.com/attachments/{attachment_id}/)'
        replacement_name = 'Suite replacement name'
        source_project = project_factory()
        dst_project = project_factory()
        with allure.step('Create test suites tree structure'):
            root_suite = test_suite_factory(project=source_project)
            child_suite = test_suite_factory(project=source_project, parent=root_suite)
            section_1 = test_suite_factory(project=source_project, parent=child_suite)
            section_2 = test_suite_factory(project=source_project, parent=child_suite)
        source_suites = [root_suite, child_suite, section_1, section_2]
        attachments_section_2 = []
        attachments_steps_section_2 = []
        with allure.step('Create cases for suite section_1'):
            cases_section_1 = [test_case_factory(suite=section_1) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
        cases_section_2 = []
        labels = []
        labeled_items = []
        with allure.step('Generate cases with steps, attachments and labels in suite section_2'):
            for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
                case = test_case_with_steps_factory(suite=section_2)
                attachment = attachment_factory(content_object=case)
                case.scenario = attach_reference.format(attachment_id=attachment.id)
                case.save()
                labeled_item = labeled_item_factory(content_object=case)
                labeled_items.append(labeled_item)
                labels.append(labeled_item.label)
                cases_section_2.append(case)
                attachments_section_2.append(attachment)
                for step in case.steps.all():
                    attachment = attachment_factory(content_object=step)
                    step.expected = attach_reference.format(attachment_id=attachment.id)
                    step.save()
                    attachments_steps_section_2.append(attachment)

        data = {
            'suites': [{'id': root_suite.id}],
        }
        if is_suite_specified:
            dst_suite = test_suite_factory(project=dst_project)
            data['dst_suite_id'] = dst_suite.id

        if is_project_specified:
            data['dst_project_id'] = dst_project.id

        if is_name_specified:
            data['suites'][0]['new_name'] = replacement_name

        if is_suite_specified and not is_project_specified:
            with allure.step('Validate project is required to copy test suite'):
                api_client.send_request(
                    self.view_name_copy,
                    request_type=RequestType.POST,
                    data=data,
                    expected_status=HTTPStatus.BAD_REQUEST,
                )
            return
        api_client.send_request(
            self.view_name_copy,
            request_type=RequestType.POST,
            data=data,
        )
        src_steps = TestCaseStep.objects.filter(test_case__in=[case.id for case in cases_section_2]).order_by('id')

        copied_cases_sec_1 = (
            TestCase.objects
            .filter(suite__name=section_1.name)
            .exclude(pk__in=self.get_ids_from_list(cases_section_1))
            .order_by('id')
        )
        copied_cases_sec_2 = (
            TestCase.objects
            .filter(suite__name=section_2.name)
            .exclude(pk__in=self.get_ids_from_list(cases_section_2))
            .order_by('id')
        )

        copied_attachments_sec_2 = (
            Attachment.objects
            .filter(content_type=ContentType.objects.get_for_model(TestCase))
            .exclude(pk__in=self.get_ids_from_list(attachments_section_2))
            .order_by('id')
        )
        copied_steps = (
            TestCaseStep.objects
            .all()
            .exclude(pk__in=self.get_ids_from_list(src_steps))
            .order_by('id')
        )
        copied_attachments_steps_sec_2 = (
            Attachment.objects
            .filter(content_type=ContentType.objects.get_for_model(TestCaseStep))
            .exclude(pk__in=self.get_ids_from_list(attachments_steps_section_2))
            .order_by('id')
        )
        copied_labels = (
            Label.objects
            .all()
            .exclude(pk__in=self.get_ids_from_list(labels))
            .order_by('id')
        )

        copied_labeled_items = (
            LabeledItem.objects
            .filter(label__in=copied_labels if is_project_specified else labels)
            .exclude(pk__in=self.get_ids_from_list(labeled_items))
            .order_by('id')
        )

        with allure.step('Validate cases in suite section_1'):
            self._validate_copied_objects(
                cases_section_1,
                copied_cases_sec_1,
                changed_attr_names=['id', 'attachments', 'labeled_items', 'suite_id'],
                copied_attr_names=[
                    'name', 'setup', 'scenario', 'expected', 'teardown', 'estimate', 'description', 'is_steps',
                ],
                project_id_changed=is_project_specified,
            )
        with allure.step('Validate cases in suite section_2'):
            self._validate_copied_objects(
                cases_section_2,
                copied_cases_sec_2,
                changed_attr_names=['id', 'attachments', 'labeled_items', 'suite_id'],
                copied_attr_names=['name', 'setup', 'expected', 'teardown', 'estimate', 'description', 'is_steps'],
                attach_reference_fields=['scenario'],
                project_id_changed=is_project_specified,
            )
        with allure.step('Validate attachments in suite section_2'):
            self._validate_copied_objects(
                attachments_section_2,
                copied_attachments_sec_2,
                changed_attr_names=['id', 'object_id', 'content_object', 'file'],
                copied_attr_names=['name', 'filename', 'file_extension', 'size', 'content_type', 'comment'],
                project_id_changed=is_project_specified,
            )
        with allure.step('Validate steps copied in suite section_2'):
            self._validate_copied_objects(
                src_steps,
                copied_steps,
                changed_attr_names=['id', 'test_case_id'],
                copied_attr_names=['name', 'scenario', 'sort_order'],
                attach_reference_fields=['expected'],
                project_id_changed=is_project_specified,
            )
        with allure.step('Validate attachments copied for steps in suite section_2'):
            self._validate_copied_objects(
                attachments_steps_section_2,
                copied_attachments_steps_sec_2,
                changed_attr_names=['id', 'object_id', 'content_object', 'file'],
                copied_attr_names=['name', 'filename', 'file_extension', 'size', 'content_type', 'comment'],
                project_id_changed=is_project_specified,
            )

        if is_project_specified:
            with allure.step('Validate copied labels and objects'):
                self._validate_copied_objects(
                    labels,
                    copied_labels,
                    changed_attr_names=['id'],
                    copied_attr_names=['name', 'user', 'type'],
                    project_id_changed=is_project_specified,
                )
        else:
            with allure.step('Validate number of labels did not change'):
                assert len(Label.objects.all()) == constants.NUMBER_OF_OBJECTS_TO_CREATE

        with allure.step('Validate labeled item reference copied'):
            changed_attr_names = ['id', 'label', 'content_object'] if is_project_specified else ['id', 'content_object']
            self._validate_copied_objects(
                labeled_items,
                copied_labeled_items,
                changed_attr_names=changed_attr_names,
                copied_attr_names=['content_type'],
                project_id_changed=is_project_specified,
                skip_project_validation=True,
                sort_by='id',
            )

        copied_suites = TestSuite.objects.all().exclude(pk__in=self.get_ids_from_list(source_suites)).order_by('id')

        if is_name_specified:
            if is_suite_specified:
                copied_suites = copied_suites.exclude(id=dst_suite.id)
            self._validate_copied_objects(
                source_suites[:1],
                copied_suites[:1],
                changed_attr_names=['id', 'name', 'parent', 'tree_id'],
                copied_attr_names=['description'],
                project_id_changed=is_project_specified,
            )
            source_suites = source_suites[1:]
            copied_suites = copied_suites.exclude(id=copied_suites.first().id)

        if is_suite_specified:
            with allure.step('Validate copied suites'):
                assert len(copied_suites) == len(copied_suites.filter(tree_id=copied_suites[0].tree_id)), \
                    'Tree was not rebuild properly'
                copied_suites = copied_suites.exclude(id=dst_suite.id)
                self._validate_copied_objects(
                    source_suites,
                    copied_suites,
                    changed_attr_names=['id', 'parent', 'tree_id'],
                    copied_attr_names=['name', 'description'],
                    project_id_changed=is_project_specified,
                )
        else:
            with allure.step('Validate copied suites'):
                self._validate_copied_objects(
                    source_suites,
                    copied_suites,
                    changed_attr_names=['id', 'parent', 'tree_id'],
                    copied_attr_names=['name', 'description'],
                    project_id_changed=is_project_specified,
                )
            with allure.step('Validate tree was rebuilt'):
                assert len(copied_suites) == len(copied_suites.filter(tree_id=copied_suites[0].tree_id)), \
                    'Tree was not rebuild properly'

    @classmethod
    def get_ids_from_list(cls, objs: list[models.Model]):
        return [obj.id for obj in objs]

    @allure.title('Test copy suite with migrating back steps')
    def test_copy_suite_with_migrating_steps(self, authorized_superuser_client, project, test_suite_factory):
        suite = test_suite_factory(project=project)
        copied_suite_name = 'copied_suite'
        case_list_reverse = 'api:v1:testcase-list'
        case_detail_reverse = 'api:v1:testcase-detail'
        payload = {
            'name': 'Case',
            'attributes': {},
            'attachments': [],
            'is_steps': True,
            'steps': [
                {'name': '1', 'scenario': '1', 'expected': '', 'sort_order': 1, 'attachments': []},
                {'name': '2', 'scenario': '2', 'expected': '', 'sort_order': 2, 'attachments': []},
            ],
            'labels': [{'name': 'new_label'}],
            'project': project.pk,
            'suite': suite.pk,
        }
        with allure.step('Create test case with steps via api'):
            src_case_id = authorized_superuser_client.send_request(
                case_list_reverse,
                data=payload,
                request_type=RequestType.POST,
                expected_status=HTTPStatus.CREATED,
            ).json()['id']
        with allure.step('Bump version of test case via update'):
            authorized_superuser_client.send_request(
                case_detail_reverse,
                reverse_kwargs={'pk': src_case_id},
                data=payload,
                request_type=RequestType.PUT,
            )

        with allure.step('Create copy of test suite via api'):
            authorized_superuser_client.send_request(
                self.view_name_copy,
                data={'suites': [{'id': suite.id, 'new_name': copied_suite_name}], 'dst_project_id': project.id},
                request_type=RequestType.POST,
            )
        copied_suite = TestSuite.objects.filter(name=copied_suite_name).first()
        assert copied_suite
        copied_case = TestCase.objects.filter(suite_id=copied_suite.id).first()
        assert copied_case

        with allure.step('Validate label history_id'):
            label_history_id = LabeledItem.objects.get(object_id=copied_case.pk).content_object_history_id
            assert label_history_id == copied_case.history.first().history_id

        with allure.step('Bump copied case version'):
            authorized_superuser_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': copied_case.pk},
                data=payload,
                request_type=RequestType.PUT,
            )

        copied_case_histories = copied_case.history.all().order_by('history_date').values_list('history_id', flat=True)
        with allure.step('Validate steps count for all versions'):
            for history_id in copied_case_histories:
                resp_body = authorized_superuser_client.send_request(
                    case_detail_reverse,
                    reverse_kwargs={'pk': copied_case.pk},
                    query_params={'version': history_id},
                ).json()
            assert len(resp_body['steps']) == 2
        with allure.step('Validate steps count for case without version'):
            resp_body = authorized_superuser_client.send_request(
                case_detail_reverse,
                reverse_kwargs={'pk': src_case_id},
            ).json()
            assert len(resp_body['steps']) == 2

    @classmethod
    def _validate_copied_objects(
        cls,
        src_objects: Iterable[Any],
        copied_objects: Iterable[Any],
        changed_attr_names: list[str],
        copied_attr_names: list[str],
        project_id_changed: bool,
        skip_project_validation: bool = False,
        attach_reference_fields: list[str] = None,
        sort_by: str = 'name',
    ):
        src_objects_copied = deepcopy(src_objects)
        copied_objects_copied = deepcopy(copied_objects)

        src_objects_copied = sorted(src_objects_copied, key=lambda elem: getattr(elem, sort_by))
        copied_objects_copied = sorted(copied_objects_copied, key=lambda elem: getattr(elem, sort_by))

        pattern = r'Some useful text about cats !\[\]\(https://possible-host\.com/attachments/\d+/\)'
        if not attach_reference_fields:
            attach_reference_fields = []
        if project_id_changed and not skip_project_validation:
            changed_attr_names.append('project_id')
        elif not project_id_changed and not skip_project_validation:
            copied_attr_names.append('project_id')
        with allure.step('Validate copied objects number'):
            assert len(src_objects_copied) == len(copied_objects_copied), \
                'Both validating objects lengths must be equal'

        for src_obj, copied_obj in zip(src_objects_copied, copied_objects_copied):
            for changed_attr_name in changed_attr_names:
                if not getattr(src_obj, changed_attr_name):
                    continue
                assert getattr(src_obj, changed_attr_name) != getattr(copied_obj, changed_attr_name), \
                    f'{changed_attr_name} has not changed'

            for copied_attr_name in copied_attr_names:
                assert getattr(src_obj, copied_attr_name) == getattr(copied_obj, copied_attr_name), \
                    f'{copied_attr_name} changed'

            for attach_reference_field in attach_reference_fields:
                src_value = getattr(src_obj, attach_reference_field)
                copied_value = getattr(copied_obj, attach_reference_field)
                assert re.match(pattern, src_value) and re.match(pattern, copied_value)
                assert getattr(src_obj, attach_reference_field) != getattr(copied_obj, attach_reference_field), \
                    'Attachment reference was not changed'


@pytest.mark.django_db(reset_sequences=True)
@allure.parent_suite('Test suites')
@allure.suite('Integration tests')
@allure.sub_suite('Endpoints query parameters')
class TestSuiteEndpointsQueryParams:
    view_name_list = 'api:v1:testsuite-list'

    @allure.title('Test filter by project')
    def test_suite_filter(self, superuser_client, generate_projects_and_suites):
        for project in generate_projects_and_suites:
            with allure.step(f'Validate suites for project {project.id}'):
                suites = TestSuite.objects.filter(project=project.id)
                expected_dict = model_to_dict_via_serializer(suites, TestSuiteBaseMockSerializer, many=True)
                response = superuser_client.send_request(
                    self.view_name_list,
                    expected_status=HTTPStatus.OK,
                    request_type=RequestType.GET,
                    query_params={'project': project.id},
                )
                actual_dict = response.json_strip()
                with allure.step('Validate suites'):
                    assert actual_dict == expected_dict, 'Actual and expected dict are different.'

    @allure.title('Test treeview flag')
    def test_suite_treeview(self, superuser_client, generate_projects_and_suites):
        for project in generate_projects_and_suites:
            suites = TestSuiteSelector().suite_list_treeview().filter(project=project)
            expected_dict = model_to_dict_via_serializer(suites, serializer_class=TestSuiteTreeSerializer, many=True)
            response = superuser_client.send_request(
                self.view_name_list,
                expected_status=HTTPStatus.OK,
                request_type=RequestType.GET,
                query_params={'project': project.id, 'treeview': 'True'},
            )
            actual_dict = response.json_strip()
            with allure.step('Validate suites'):
                assert actual_dict.sort(key=lambda x: x['id']) == expected_dict.sort(key=lambda x: x['id']), \
                    'Actual and expected dict are different.'

    @allure.title('Test search')
    @pytest.mark.django_db(reset_sequences=True)
    def test_search(self, superuser_client, test_suite_factory, project):
        root_suite = test_suite_factory(project=project)
        inner_suite = test_suite_factory(project=project, parent=root_suite)
        expected_suites = []
        search_name = 'search_name'
        with allure.step('Create expected objects with name to be found'):
            for idx in range(int(constants.NUMBER_OF_OBJECTS_TO_CREATE / 2)):
                expected_suites.append(
                    test_suite_factory(
                        parent=inner_suite,
                        name=f'search_name_{idx}',
                        project=project,
                    ),
                )
        with allure.step('Create objects that will not be found'):
            for _ in range(int(constants.NUMBER_OF_OBJECTS_TO_CREATE / 2)):
                expected_suites.append(test_suite_factory(parent=inner_suite, project=project))
        search_qs = self._get_search_qs_by_expected(expected_suites)
        expected_output = model_to_dict_via_serializer(
            search_qs,
            TestSuiteMockTreeSerializer,
            many=True,
            as_json=True,
        )
        actual_data = superuser_client.send_request(
            self.view_name_list,
            query_params={'project': project.id, 'search': search_name, 'treeview': 1},
        ).json_strip(as_json=True)
        assert json.loads(actual_data) == json.loads(expected_output), 'Search data does not match expected data.'
        with allure.step('Validate full list of objects is different from found data'):
            actual_data = superuser_client.send_request(
                self.view_name_list,
                query_params={'project': project.id, 'treeview': 1},
            ).json_strip()
            assert actual_data != expected_output
        with allure.step('Validate no objects found with non-existent search query'):
            actual_data = superuser_client.send_request(
                self.view_name_list,
                query_params={
                    'project': project.id,
                    'search': 'non-existent',
                    'treeview': 1,
                },
            ).json_strip()
            assert not actual_data, 'Non-existent search argument got output.'

    @allure.title('Test search by suite_path')
    def test_search_with_path(self, superuser_client, test_suite_factory, project):
        root_suite = test_suite_factory(project=project)
        inner_suite = test_suite_factory(project=project, parent=root_suite)
        search_name = 'search_name'
        expected_suite = test_suite_factory(project=project, parent=inner_suite, name=search_name)
        expected_output = model_to_dict_via_serializer(
            expected_suite,
            TestSuiteBaseMockSerializer,
            refresh_instances=True,
        )
        actual_suite_list = superuser_client.send_request(
            self.view_name_list,
            expected_status=HTTPStatus.OK,
            request_type=RequestType.GET,
            query_params={'project': project.pk, 'is_flat': True, 'search': search_name},
        ).json()['results']
        with allure.step('Validate response body'):
            assert expected_output == actual_suite_list[0]

    def test_case_counting(
        self,
        superuser_client,
        test_suite_factory,
        project,
        test_case_factory,
    ):
        cases = []
        one_hour_in_seconds = 3600
        for _ in range(2):
            test_suite = test_suite_factory(project=project)
            for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
                is_deleted = idx % 2
                cases.append(test_case_factory(suite=test_suite, is_deleted=is_deleted, estimate=one_hour_in_seconds))

        actual_dict = superuser_client.send_request(
            self.view_name_list,
            expected_status=HTTPStatus.OK,
            request_type=RequestType.GET,
            query_params={'project': project.id, 'treeview': 'True'},
        ).json()['results']

        assert len(actual_dict) == 2, 'Incorrect number of suites'
        for suite in actual_dict:
            assert suite['cases_count'] == constants.NUMBER_OF_OBJECTS_TO_CREATE // 2
            assert suite['total_cases_count'] == suite['cases_count']
            assert suite['total_estimates'] == f'{constants.NUMBER_OF_OBJECTS_TO_CREATE // 2}h'

    @allure.title('Test flat suite list display')
    def test_flat_list_with_paths(
        self,
        superuser_client,
        test_suite_factory,
        project,
    ):
        parent = None
        expected_suites = []
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            parent = test_suite_factory(parent=parent, project=project)
            expected_suites.append(parent)
        expected_suites.sort(key=lambda suite: suite.name)
        actual_suite_list = superuser_client.send_request(
            self.view_name_list,
            expected_status=HTTPStatus.OK,
            request_type=RequestType.GET,
            query_params={'project': project.pk, 'is_flat': True},
        ).json()['results']
        expected_body = model_to_dict_via_serializer(
            expected_suites,
            TestSuiteBaseMockSerializer,
            many=True,
            refresh_instances=True,
        )
        with allure.step('Validate response body'):
            assert expected_body == actual_suite_list

    @classmethod
    @allure.step('Get queryset of filtered and prefetched objects by expected objects')
    def _get_search_qs_by_expected(cls, expected_suites: Iterable[TestSuite]) -> QuerySet[TestSuite]:
        pref_qs = TestSuite.objects.filter(
            pk__in=(suite.id for suite in expected_suites),
        ).get_ancestors(include_self=True).order_by('name')
        max_level = get_max_level(TestSuite)
        return deepcopy(pref_qs).filter(parent=None).prefetch_related(
            *form_tree_prefetch_objects(
                'child_test_suites',
                'child_test_suites',
                max_level,
                queryset=pref_qs,
            ),
        ).order_by('name')
