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
import random
from http import HTTPStatus

import pytest

from tests import constants
from tests.commons import RequestType, model_to_dict_via_serializer
from tests.error_messages import DUPLICATE_STATUS_ERR_MSG
from testy.tests_representation.api.v1.serializers import ResultStatusSerializer
from testy.tests_representation.choices import ResultStatusType, TestStatuses
from testy.tests_representation.models import ResultStatus


@pytest.mark.django_db
class TestResultStatusEndpoints:
    view_name_list = 'api:v1:status-list'
    view_name_detail = 'api:v1:status-detail'

    def test_list(
        self, api_client, authorized_superuser, result_status_factory,
        system_statuses_dict, project,
    ):
        expected_instances = model_to_dict_via_serializer(
            [result_status_factory(project=project) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)],
            ResultStatusSerializer,
            many=True,
        )
        expected_instances += system_statuses_dict
        response = api_client.send_request(self.view_name_list, query_params={'project': project.id})
        assert len(response.json()) == len(expected_instances)
        for instance_dict in response.json():
            assert instance_dict in expected_instances, f'{instance_dict} was not found in expected instances.'

    def test_list_with_ordering(
        self, api_client, authorized_superuser, result_status_factory,
        system_statuses_dict, project,
    ):
        expected_instances = model_to_dict_via_serializer(
            [result_status_factory(project=project) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)],
            ResultStatusSerializer,
            many=True,
        )
        expected_instances += system_statuses_dict
        random.shuffle(expected_instances)
        order = dict(
            zip([str(instance['id']) for instance in expected_instances], range(1, len(expected_instances) + 1)),
        )
        project.settings['status_order'] = order
        project.save()

        response = api_client.send_request(self.view_name_list, query_params={'project': project.id})
        assert expected_instances == response.json(), 'Expected and received value do not match'

    def test_retrieve(self, api_client, authorized_superuser, result_status):
        expected_dict = model_to_dict_via_serializer(result_status, ResultStatusSerializer)
        response = api_client.send_request(self.view_name_detail, reverse_kwargs={'pk': result_status.pk})
        actual_dict = response.json()
        assert actual_dict == expected_dict, 'Actual model dict is different from expected'

    @pytest.mark.parametrize('type_value', (ResultStatusType.CUSTOM, ResultStatusType.SYSTEM))
    def test_creation(self, superuser_client, superuser, project, type_value):
        project = project if type_value == ResultStatusType.CUSTOM else None
        expected_number_of_statuses = ResultStatus.objects.count() + 1
        status_dict = {
            'name': constants.STATUS_NAME.lower(),
            'project': getattr(project, 'pk', None),
            'type': type_value,
        }
        response = superuser_client.send_request(self.view_name_list, status_dict, HTTPStatus.CREATED, RequestType.POST)
        assert ResultStatus.objects.count() == expected_number_of_statuses, f'Expected number of users ' \
                                                                            f'"{expected_number_of_statuses}"' \
                                                                            f'actual: "{ResultStatus.objects.count()}"'
        for key, val in status_dict.items():
            assert response.json().get(key) == val

    @pytest.mark.parametrize('first_type_value', (ResultStatusType.CUSTOM, ResultStatusType.SYSTEM))
    def test_create_status_with_exist_name_forbidden(
        self, superuser_client, superuser, project, result_status_factory, first_type_value,
    ):
        first_result_status = result_status_factory(
            project=project if first_type_value == ResultStatusType.CUSTOM else None,
            type=first_type_value,
            name=constants.STATUS_NAME,
        )

        create_status_dict = {
            'name': first_result_status.name.upper(),
            'project': project.pk,
        }

        response = superuser_client.send_request(
            self.view_name_list,
            create_status_dict,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        err_msg = DUPLICATE_STATUS_ERR_MSG.format(
            first_result_status.name,
            create_status_dict['name'],
            project.name,
        )
        assert response.json()['errors'][0] == err_msg

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    def test_update(self, api_client, authorized_superuser, result_status, project, request_type):
        update_dict = {
            'project': project.id,
        }
        if request_type == RequestType.PUT:
            update_dict.update({'name': f'{result_status.name}_{result_status.name}'})

        api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': result_status.pk},
            request_type=request_type,
            expected_status=HTTPStatus.OK,
            data=update_dict,
        )
        actual_dict = model_to_dict_via_serializer(
            ResultStatus.objects.get(pk=result_status.id),
            ResultStatusSerializer,
        )
        for key in update_dict.keys():
            assert update_dict[key] == actual_dict[key], f'Field "{key}" was not updated.'

    @pytest.mark.parametrize('type_value', (ResultStatusType.CUSTOM, ResultStatusType.SYSTEM))
    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    def test_update_status_on_exist_name_forbidden(
        self, superuser_client, superuser, project, result_status_factory, type_value, request_type,
    ):
        first_result_status = result_status_factory(
            project=project if type_value == ResultStatusType.CUSTOM else None,
            type=type_value,
            name=constants.STATUS_NAME,
        )

        second_result_status = result_status_factory(project=project)
        update_dict = {'name': f'{first_result_status.name.upper()}'}

        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': second_result_status.pk},
            request_type=request_type,
            expected_status=HTTPStatus.BAD_REQUEST,
            data=update_dict,
        )
        err_msg = DUPLICATE_STATUS_ERR_MSG.format(
            first_result_status.name,
            update_dict['name'],
            project.name,
        )
        assert response.json()['errors'][0] == err_msg

    @pytest.mark.parametrize('request_type', [RequestType.PUT, RequestType.PATCH])
    def test_update_system_status_project_forbidden(
        self, api_client, authorized_superuser, project,
        request_type, result_status_factory,
    ):
        result_status = result_status_factory(type=ResultStatusType.SYSTEM, project=None)
        expected_number_of_statuses = ResultStatus.objects.count()
        update_dict = {
            'project': project.id,
        }
        if request_type == RequestType.PUT:
            update_dict.update({'name': f'{result_status.name}_{result_status.name}'})
        response = api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': result_status.pk},
            request_type=request_type,
            expected_status=HTTPStatus.BAD_REQUEST,
            data=update_dict,
        )
        assert response.json()['errors'][0] == 'System status cannot have project'
        assert ResultStatus.objects.count() == expected_number_of_statuses

    @pytest.mark.parametrize('request_type', [RequestType.PUT, RequestType.PATCH])
    @pytest.mark.parametrize('status_type', [ResultStatusType.CUSTOM, ResultStatusType.SYSTEM])
    def test_update_status_type_forbidden(
        self, superuser_client, superuser,
        result_status_factory, request_type, status_type, project,
    ):
        result_status = result_status_factory(
            type=status_type, project=project if status_type == ResultStatusType.CUSTOM else None,
        )
        expected_number_of_statuses = ResultStatus.objects.count()

        update_dict = {'type': int(not result_status.type)}
        if request_type == RequestType.PUT:
            update_dict.update({'name': f'{result_status.name}_{result_status.name}'})

        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': result_status.pk},
            request_type=request_type,
            data=update_dict,
            expected_status=HTTPStatus.BAD_REQUEST,
        )

        assert response.json()['errors'][0] == 'Status type cannot be changed'
        assert ResultStatus.objects.count() == expected_number_of_statuses

    def test_create_system_with_project_forbidden(self, superuser_client, superuser, project):
        status_dict = {
            'name': constants.STATUS_NAME,
            'project': project.pk,
            'type': ResultStatusType.SYSTEM,
        }
        expected_number_of_statuses = ResultStatus.objects.count()
        response = superuser_client.send_request(
            self.view_name_list,
            status_dict,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        assert response.json()['errors'][0] == 'System status cannot have project'
        assert ResultStatus.objects.count() == expected_number_of_statuses

    @pytest.mark.parametrize('request_type', [RequestType.PUT, RequestType.PATCH])
    def test_update_custom_without_project_forbidden(
        self, api_client, authorized_superuser, request_type, result_status, system_statuses_dict,
    ):
        update_dict = {
            'project': None,
        }
        expected_number_of_statuses = ResultStatus.objects.count()
        if request_type == RequestType.PUT:
            update_dict.update({'name': f'{result_status.name}_{result_status.name}'})
        response = api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': result_status.pk},
            request_type=request_type,
            expected_status=HTTPStatus.BAD_REQUEST,
            data=update_dict,
        )
        assert response.json()['errors'][0] == 'Custom status must have project'
        assert ResultStatus.objects.count() == expected_number_of_statuses

    def test_create_custom_without_project_forbidden(self, superuser_client, superuser):
        status_dict = {
            'name': constants.STATUS_NAME,
            'type': ResultStatusType.CUSTOM,
        }
        expected_number_of_statuses = ResultStatus.objects.count()
        response = superuser_client.send_request(
            self.view_name_list,
            status_dict,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        assert response.json()['errors'][0] == 'Custom status must have project'
        assert ResultStatus.objects.count() == expected_number_of_statuses

    def test_delete(self, api_client, authorized_superuser, result_status):
        expected_number_of_statuses = ResultStatus.objects.count() - 1
        api_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': result_status.pk},
        )
        assert ResultStatus.objects.count() == expected_number_of_statuses, \
            f'Status with id "{result_status.id}" was not deleted.'

    def test_create_with_deleted_name(self, api_client, authorized_superuser, result_status):
        expected_number_of_statuses = ResultStatus.objects.count() - 1
        api_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': result_status.pk},
        )
        assert ResultStatus.objects.count() == expected_number_of_statuses, \
            f'Status with id "{result_status.id}" was not deleted.'

        expected_number_of_statuses += 1
        status_dict = {
            'name': result_status.name,
            'project': result_status.project.pk,
        }
        response = api_client.send_request(self.view_name_list, status_dict, HTTPStatus.CREATED, RequestType.POST)
        assert ResultStatus.objects.count() == expected_number_of_statuses, f'Expected number of users ' \
                                                                            f'"{expected_number_of_statuses}"' \
                                                                            f'actual: "{ResultStatus.objects.count()}"'
        assert response.json()['id'] == result_status.pk

    @pytest.mark.parametrize(
        'color, expected_status', [
            ('#000000', HTTPStatus.OK),
            ('#000', HTTPStatus.OK),
            ('#0000', HTTPStatus.BAD_REQUEST),
            ('#00', HTTPStatus.BAD_REQUEST),
            ('rgb(0, 0, 0)', HTTPStatus.OK),
            ('(255, 255, 255)', HTTPStatus.OK),
            ('rgb(-1, 0, 0)', HTTPStatus.BAD_REQUEST),
            ('(256, 255, 255)', HTTPStatus.BAD_REQUEST),
            ('rgba(0, 0, 0, 0)', HTTPStatus.OK),
            ('(255, 255, 255, 0.8)', HTTPStatus.OK),
            ('rgba(0, 0, 0, 2)', HTTPStatus.BAD_REQUEST),
            ('(255, 255, 255, 1.5)', HTTPStatus.BAD_REQUEST),
            ('255, 255, 255)', HTTPStatus.BAD_REQUEST),
        ],
    )
    @pytest.mark.parametrize('request_type', [RequestType.PUT, RequestType.PATCH, RequestType.POST])
    def test_create_or_update_color_validation(
        self, color, expected_status, project, api_client, authorized_superuser, request_type, result_status,
    ):
        if request_type == RequestType.POST and expected_status == HTTPStatus.OK:
            expected_status = HTTPStatus.CREATED
        status_dict = {'name': constants.STATUS_NAME * 2, 'color': color, 'project': project.pk}
        if request_type == RequestType.POST:
            response = api_client.send_request(
                self.view_name_list,
                data=status_dict,
                expected_status=expected_status,
                request_type=request_type,
            )
        else:
            response = api_client.send_request(
                self.view_name_detail,
                expected_status=expected_status,
                request_type=request_type,
                data=status_dict,
                reverse_kwargs={'pk': result_status.pk},
            )
        if expected_status == HTTPStatus.BAD_REQUEST:
            assert response.json()['errors'][0] == 'Status color must be in hex or rgb or rgba'
        else:
            for key, val in status_dict.items():
                assert response.json().get(key) == val

    @pytest.mark.parametrize('view_name', ('api:v1:testplan-activity-statuses', 'api:v1:testplan-statuses'))
    def test_get_statuses_from_testplan_and_testplan_activity(
        self, api_client, authorized_superuser, generate_historical_objects, view_name,
    ):
        parent_plan, _, _, status_list = generate_historical_objects
        expected_instances = model_to_dict_via_serializer(status_list, ResultStatusSerializer, many=True)
        response_body = api_client.send_request(view_name, reverse_kwargs={'pk': parent_plan.pk}).json()
        assert response_body == expected_instances

    def test_get_last_statuses_from_testplan(
        self, api_client, authorized_superuser, generate_historical_objects,
        result_status_factory, test_result_factory,
    ):
        parent_plan, _, test_list, _ = generate_historical_objects
        result_status = result_status_factory(project=parent_plan.project)
        for test in test_list:
            test_result_factory(test=test, status=result_status, project=parent_plan.project)
        expected_instances = model_to_dict_via_serializer(result_status, ResultStatusSerializer)
        response_body = api_client.send_request(
            'api:v1:testplan-statuses', reverse_kwargs={'pk': parent_plan.pk},
        ).json()
        assert len(response_body) == 1
        assert response_body[0] == expected_instances

    def test_validate_status_with_system_name(self, api_client, authorized_superuser, project):
        create_status_dict = {
            'name': TestStatuses.UNTESTED.label,
            'project': project.pk,
        }
        response = api_client.send_request(
            self.view_name_list,
            create_status_dict,
            HTTPStatus.BAD_REQUEST,
            RequestType.POST,
        )
        err_msg = f'Status with name "{TestStatuses.UNTESTED.label}" is forbidden'
        assert response.json()['errors'][0] == err_msg
