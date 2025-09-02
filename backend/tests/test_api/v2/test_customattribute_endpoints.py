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

from tests import constants
from tests.commons import RequestType, model_to_dict_via_serializer
from tests.error_messages import (
    DUPLICATE_CUSTOM_ATTRIBUTE_ERR_MSG,
    REQUIRED_FIELD_MSG,
    SUITE_IDS_CONTAINS_NOT_RELATED_ITEMS,
)
from testy.core.api.v2.serializers import CustomAttributeBaseSerializer
from testy.core.choices import CustomFieldType
from testy.core.models import CustomAttribute

_ERRORS = 'errors'


@pytest.mark.django_db
class TestCustomAttributeEndpoints:
    view_name_list = 'api:v2:customattribute-list'
    view_name_detail = 'api:v2:customattribute-detail'

    def test_list(self, api_client, authorized_superuser, custom_attribute_factory, project):
        expected_instances = []

        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            expected_instances.append(
                model_to_dict_via_serializer(
                    custom_attribute_factory(project=project), CustomAttributeBaseSerializer,
                ),
            )

        response = api_client.send_request(self.view_name_list, query_params={'project': project.id})

        for instance in response.json():
            assert instance in expected_instances

    def test_retrieve(self, api_client, authorized_superuser, custom_attribute):
        expected_dict = model_to_dict_via_serializer(custom_attribute, CustomAttributeBaseSerializer)
        response = api_client.send_request(self.view_name_detail, reverse_kwargs={'pk': custom_attribute.pk})
        actual_dict = response.json()
        assert actual_dict == expected_dict, 'Actual model dict is different from expected'

    def test_creation(self, api_client, authorized_superuser, project):
        expected_custom_attributes_count = 1
        assert CustomAttribute.objects.count() == 0, 'Extra custom attributes were found.'

        custom_attribute_fields = {
            'name': constants.CUSTOM_ATTRIBUTE_NAME,
            'project': project.pk,
            'type': CustomFieldType.TXT,
            'applied_to': {
                'testplan': {
                    'is_required': False,
                },
                'testcase': {
                    'is_required': False,
                    'suite_ids': [],
                },
            },
        }
        api_client.send_request(self.view_name_list, custom_attribute_fields, HTTPStatus.CREATED, RequestType.POST)
        assert CustomAttribute.objects.count() == expected_custom_attributes_count, (
            f'Expected number of attributes {expected_custom_attributes_count} '
            f'actual: {CustomAttribute.objects.count()}'
        )

    def test_creation_case_insensitive(self, api_client, authorized_superuser, project):
        expected_custom_attributes_count = 1
        assert CustomAttribute.objects.count() == 0, 'Extra custom attributes were found.'

        custom_attribute_fields_lower = {
            'name': constants.CUSTOM_ATTRIBUTE_NAME.lower(),
            'project': project.pk,
            'type': CustomFieldType.JSON,
            'applied_to': {
                'testplan': {
                    'is_required': False,
                },
            },
        }

        api_client.send_request(
            self.view_name_list, custom_attribute_fields_lower, HTTPStatus.CREATED, RequestType.POST,
        )

        assert CustomAttribute.objects.count() == expected_custom_attributes_count, (
            f'Expected number of custom attributes {expected_custom_attributes_count} '
            f'actual: {CustomAttribute.objects.count()}'
        )

        custom_attribute_fields_upper = {
            'name': constants.CUSTOM_ATTRIBUTE_NAME.upper(),
            'project': project.pk,
            'type': CustomFieldType.JSON,
            'applied_to': {
                'testplan': {
                    'is_required': False,
                },
            },
        }

        response = api_client.send_request(
            self.view_name_list, custom_attribute_fields_upper, HTTPStatus.BAD_REQUEST, RequestType.POST,
        )
        err_msg = DUPLICATE_CUSTOM_ATTRIBUTE_ERR_MSG.format(
            custom_attribute_fields_upper['name'],
            custom_attribute_fields_lower['name'],
            project.name,
        )
        assert response.json()['name'] == err_msg

    @pytest.mark.parametrize('expected_status', [HTTPStatus.OK, HTTPStatus.BAD_REQUEST])
    def test_update(
        self, api_client, authorized_superuser, custom_attribute, project, expected_status,
    ):
        updated_name = 'new_custom_attribute_name'
        custom_attribute_fields = {
            'name': updated_name,
        }
        if expected_status == HTTPStatus.OK:
            custom_attribute_fields['project'] = project.pk
            custom_attribute_fields['type'] = CustomFieldType.JSON
            custom_attribute_fields['applied_to'] = {
                'testplan': {
                    'is_required': False,
                },
            }

        response = api_client.send_request(
            self.view_name_detail,
            custom_attribute_fields,
            request_type=RequestType.PUT,
            expected_status=expected_status,
            reverse_kwargs={'pk': custom_attribute.pk},
        )
        if expected_status == HTTPStatus.OK:
            actual_name = CustomAttribute.objects.get(pk=custom_attribute.id).name
            assert actual_name == updated_name, (
                f'Name does not match. Expected name "{actual_name}", actual: "{updated_name}"'
            )
        else:
            assert response.json()['project'][0] == REQUIRED_FIELD_MSG
            assert response.json()['type'][0] == REQUIRED_FIELD_MSG
            assert response.json()['applied_to'][0] == REQUIRED_FIELD_MSG

    def test_partial_update(self, api_client, authorized_superuser, custom_attribute):
        new_name = 'new_custom_attribute_name'
        custom_attribute_fields_updated = {
            'name': new_name,
        }
        api_client.send_request(
            self.view_name_detail,
            custom_attribute_fields_updated,
            request_type=RequestType.PATCH,
            reverse_kwargs={'pk': custom_attribute.pk},
        )
        actual_name = CustomAttribute.objects.get(pk=custom_attribute.id).name
        assert actual_name == new_name, f'Name does not match. Expected name "{actual_name}", actual: "{new_name}"'

    def test_delete(self, api_client, authorized_superuser, custom_attribute):
        assert CustomAttribute.objects.count() == 1, 'Custom attribute was not created'

        api_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': custom_attribute.pk},
        )

        assert CustomAttribute.objects.count() == 0, \
            f'Custom attribute with id "{custom_attribute.id}" was not deleted.'

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    def test_duplicates_not_allowed(
        self, api_client, authorized_superuser, custom_attribute_factory, project, request_type,
    ):
        custom_attribute_factory(name=constants.CUSTOM_ATTRIBUTE_NAME, project=project)

        custom_attribute_to_patch = custom_attribute_factory(project=project)

        custom_attribute_fields = {
            'name': constants.CUSTOM_ATTRIBUTE_NAME,
        }
        if request_type == RequestType.PUT:
            custom_attribute_fields['project'] = project.id
            custom_attribute_fields['type'] = CustomFieldType.JSON
            custom_attribute_fields['applied_to'] = {
                'testplan': {
                    'is_required': False,
                },
            }

        api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': custom_attribute_to_patch.pk},
            data=custom_attribute_fields,
            expected_status=HTTPStatus.BAD_REQUEST,
            request_type=request_type,
        )

    @pytest.mark.parametrize('expected_status', [HTTPStatus.CREATED, HTTPStatus.BAD_REQUEST])
    def test_suite_is_a_part_of_project(
        self, api_client, authorized_superuser, project, test_suite_factory, expected_status,
    ):
        expected_custom_attributes_count = 1
        if expected_status == HTTPStatus.CREATED:
            test_suite = test_suite_factory(project=project)
        else:
            test_suite = test_suite_factory()
        assert CustomAttribute.objects.count() == 0, 'Extra custom attributes were found.'

        custom_attribute_fields = {
            'name': constants.CUSTOM_ATTRIBUTE_NAME,
            'project': project.pk,
            'type': CustomFieldType.TXT,
            'applied_to': {
                'testcase': {
                    'is_required': False,
                    'suite_ids': [test_suite.id],
                },
            },
        }

        response = api_client.send_request(
            self.view_name_list, custom_attribute_fields, expected_status, RequestType.POST,
        )

        if expected_status == HTTPStatus.BAD_REQUEST:
            assert response.json()[_ERRORS][0] == SUITE_IDS_CONTAINS_NOT_RELATED_ITEMS
        else:
            assert CustomAttribute.objects.count() == expected_custom_attributes_count, (
                f'Expected number of custom attributes {expected_custom_attributes_count} '
                f'actual: {CustomAttribute.objects.count()}'
            )

    @pytest.mark.parametrize('expected_status', [HTTPStatus.OK, HTTPStatus.BAD_REQUEST])
    def test_suite_is_a_part_of_project_on_update(
        self, api_client, authorized_superuser, project, test_suite_factory, custom_attribute_factory,
        expected_status,
    ):
        expected_custom_attributes_count = 1
        broken_suite_id = 999
        initial_suite = test_suite_factory(project=project)
        suite_for_update = test_suite_factory(project=project)

        custom_attribute = custom_attribute_factory(
            name=constants.CUSTOM_ATTRIBUTE_NAME,
            project=project,
            applied_to={
                'testcase': {
                    'is_required': False,
                    'suite_ids': [initial_suite.id],
                },
            },
        )

        assert CustomAttribute.objects.count() == expected_custom_attributes_count, (
            f'Expected number of custom attributes {expected_custom_attributes_count} '
            f'actual: {CustomAttribute.objects.count()}'
        )

        custom_attribute_fields_updated = {
            'applied_to': {
                'testcase': {
                    'is_required': False,
                    'suite_ids': [suite_for_update.id] if expected_status == HTTPStatus.OK else [broken_suite_id],
                },
            },
        }

        response = api_client.send_request(
            self.view_name_detail,
            custom_attribute_fields_updated,
            expected_status,
            request_type=RequestType.PATCH,
            reverse_kwargs={'pk': custom_attribute.pk},
        )

        if expected_status == HTTPStatus.BAD_REQUEST:
            assert response.json()[_ERRORS][0] == SUITE_IDS_CONTAINS_NOT_RELATED_ITEMS
        else:
            suite_ids = response.json()['applied_to']['testcase']['suite_ids']
            assert suite_ids == [suite_for_update.id], f'Expected suite ids {[suite_for_update.id]} actual: {suite_ids}'
