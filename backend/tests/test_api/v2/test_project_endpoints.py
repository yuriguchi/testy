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

import os
from copy import deepcopy
from distutils import extension
from http import HTTPStatus
from operator import attrgetter, itemgetter
from unittest import mock

import allure
import pytest
from django.db.models import Q
from django.utils import timezone

from tests import constants
from tests.commons import RequestType, model_to_dict_via_serializer
from tests.error_messages import PERMISSION_ERR_MSG
from tests.mock_serializers.v2 import ProjectRetrieveMockSerializer, ProjectStatisticsMockSerializer
from tests.test_api.v2.test_role_endpoints import TestRoleEndpoints
from testy.core.choices import AccessRequestStatus
from testy.core.models import AccessRequest, Project
from testy.core.selectors.project_settings import ProjectSettings
from testy.serializer_fields import EstimateField
from testy.tests_description.models import TestCase
from testy.tests_representation.models import Parameter, TestResult
from testy.users.models import Membership
from testy.utilities.time import WorkTimeProcessor


@pytest.mark.django_db
@allure.parent_suite('Projects')
@allure.suite('Integration tests')
@allure.sub_suite('Endpoints')
class TestProjectEndpoints:
    view_name_list = 'api:v2:project-list'
    view_name_detail = 'api:v2:project-detail'
    view_name_progress = 'api:v2:project-progress'
    view_name_statistics = 'api:v2:project-statistics'
    view_name_access = 'api:v2:project-access'
    view_name_icon = 'api:v2:project-icon'

    @pytest.mark.django_db(reset_sequences=True)
    @allure.title('Test list display')
    def test_list(self, superuser_client, superuser, project_factory):
        with allure.step('Create projects'):
            instances = [project_factory() for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
        expected_instances = model_to_dict_via_serializer(
            instances,
            many=True,
            serializer_class=ProjectStatisticsMockSerializer,
            requested_user=superuser,
        )
        actual = superuser_client.send_request(self.view_name_list).json()['results']
        with allure.step('Validate response body'):
            assert actual == expected_instances

    @allure.title('Test detail display')
    def test_retrieve(self, superuser_client, superuser, project):
        expected_dict = model_to_dict_via_serializer(
            project,
            ProjectRetrieveMockSerializer,
            requested_user=superuser,
        )
        response = superuser_client.send_request(self.view_name_detail, reverse_kwargs={'pk': project.pk})
        actual_dict = response.json()
        with allure.step('Validate response body'):
            assert actual_dict == expected_dict

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_creation(self, superuser_client, create_file):
        allure.dynamic.title(f'Test project creation with {extension} icon')
        expected_number_of_parameters = 1
        project_dict = {
            'name': constants.PROJECT_NAME,
            'description': constants.DESCRIPTION,
            'icon': create_file,
        }
        superuser_client.send_request(
            self.view_name_list,
            project_dict,
            HTTPStatus.CREATED,
            RequestType.POST,
            format='multipart',
        )
        with allure.step('Validate project created'):
            assert Project.objects.count() == expected_number_of_parameters, f'Expected number of projects is ' \
                                                                             f'"{expected_number_of_parameters}"' \
                                                                             f'actual: "{Parameter.objects.count()}"'
        with allure.step('Validate icon added succefully'):
            assert os.path.isfile(Project.objects.first().icon.path)

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_partial_update(self, superuser_client, project, create_file, extension):
        allure.dynamic.title(f'Test partial update with {extension} icon')
        new_name = 'new_name'
        with allure.step('Validate no icon exists'):
            assert not project.icon
        project_dict = {
            'id': project.id,
            'name': new_name,
            'icon': create_file,
        }
        superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': project.pk},
            request_type=RequestType.PATCH,
            data=project_dict,
            format='multipart',
        )
        with allure.step('Get updated data from project'):
            project.refresh_from_db()
            actual_name = project.name
            icon_path = project.icon.path
        with allure.step('Validate icon added'):
            assert os.path.isfile(icon_path)
        with allure.step('Validate name changed'):
            assert actual_name == new_name, f'New name does not match. Expected name "{new_name}"' \
                                            f'actual: "{actual_name}"'
        with allure.step('Remove icon via api'):
            superuser_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': project.pk},
                request_type=RequestType.PATCH,
                data={'icon': ''},
                format='multipart',
            )
        with allure.step('Validate icon removed'):
            assert not os.path.isfile(icon_path)

    @pytest.mark.parametrize('extension', ['.jpeg'])
    @allure.title('Test update')
    def test_update(self, superuser_client, project, create_file):
        new_name = 'new_name'
        project_dict = {
            'id': project.id,
            'icon': create_file,
            'name': new_name,
        }
        superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': project.pk},
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
            data=project_dict,
            format='multipart',
        )
        project.refresh_from_db()
        actual_name = project.name
        icon_path = project.icon.path
        with allure.step('Validate icon exists'):
            assert os.path.isfile(icon_path)
        with allure.step('Validate name updated'):
            assert actual_name == new_name, f'Project name do not match. Expected name "{actual_name}", ' \
                                            f'actual: "{new_name}"'

    @pytest.mark.parametrize('extension', ['.jpeg'])
    def test_delete(self, superuser_client, project_factory, create_file):
        allure.dynamic.title('Test deletion')
        with allure.step('Create project with icon'):
            project = project_factory(icon=create_file)
        with allure.step('Validate project created'):
            assert Project.objects.count() == 1, 'Project was not created'
        with allure.step('Validate icon exists'):
            icon_path = project.icon.path
        superuser_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': project.pk},
        )
        with allure.step('Validate project was deleted'):
            assert not Project.objects.count(), f'Project with id "{project.id}" was not deleted.'
        with allure.step('Validate icon was removed'):
            assert not os.path.isfile(icon_path), 'Icon was not deleted'

    @allure.title('Test project is set automatically for result')
    def test_valid_project_assignation(self, superuser_client, user, test, result_status_factory):
        result_dict = {
            'status': result_status_factory(project=test.project).pk,
            'test': test.id,
            'user': user.id,
            'comment': constants.TEST_COMMENT,
        }
        superuser_client.send_request(
            'api:v2:testresult-list',
            result_dict,
            HTTPStatus.CREATED,
            RequestType.POST,
        )

        expected_project = TestCase.objects.first().project

        result_project = TestResult.objects.first().project
        with allure.step('Validate test project'):
            assert test.project == expected_project, f'Test was not created with correct project, ' \
                                                     f'expected project: {expected_project}' \
                                                     f'actual project: {test.project}'
        with allure.step('Validate result project'):
            assert result_project == expected_project, f'Test result was not created with correct project, ' \
                                                       f'expected project: {expected_project}' \
                                                       f'actual project: {result_project}'

    @pytest.mark.parametrize('request_type', [RequestType.PATCH, RequestType.PUT])
    def test_archived_editable_for_superuser_only(
        self,
        superuser_client,
        project_factory,
        user,
        request_type,
    ):
        msg = 'partial update' if RequestType.PATCH else 'update'
        allure.dynamic.title(f'Test archived project editable for superuser only ({msg})')
        superuser_client.force_login(user)
        project = project_factory(is_archive=True)
        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': project.pk},
            request_type=request_type,
            expected_status=HTTPStatus.FORBIDDEN,
            data={},
        )
        with allure.step('Validate error message'):
            assert response.json()['detail'] == PERMISSION_ERR_MSG

    @allure.title('Test ordering filter')
    def test_ordering_filter(self, superuser_client, superuser, project_factory):
        expected_number_of_objects = 5
        projects = []
        with allure.step('Create archived projects'):
            projects.extend(project_factory(is_archive=True) for _ in range(expected_number_of_objects))
        with allure.step('Create projects'):
            projects.extend(project_factory() for _ in range(expected_number_of_objects))
        for filter_value in ('name', 'is_archive'):
            with allure.step(f'Validate {filter_value}'):
                projects.sort(key=attrgetter(filter_value))
            content = superuser_client.send_request(
                self.view_name_list,
                query_params={'ordering': filter_value, 'is_archive': 'true'},
            ).json()
            with allure.step('Validate 10 projects created'):
                assert content['count'] == expected_number_of_objects * 2
            with allure.step('Validate response body'):
                expected_body = model_to_dict_via_serializer(
                    projects,
                    ProjectStatisticsMockSerializer,
                    many=True,
                    requested_user=superuser,
                )
                assert content['results'] == expected_body

    @pytest.mark.django_db(reset_sequences=True)
    @pytest.mark.parametrize(
        'data_fixture_name',
        [
            'multiple_plans_data_project_statistics',
            'result_filter_data_project_statistics',
            'data_different_statuses_project_statistics',
            'empty_plan_data_project_statistics',
        ],
        ids=[
            'statistics for multiple nested level plans ',
            'statistics for results',
            'statistics for results with different statuses',
            'statistics for empty project plan',
        ],
    )
    def test_project_progress(
        self,
        superuser_client,
        project,
        data_fixture_name,
        request,
    ):
        allure.dynamic.title(f'Test {request.node.callspec.id}')
        with allure.step('Create data'):
            expected, start_date, end_date = request.getfixturevalue(data_fixture_name)
        response = superuser_client.send_request(
            self.view_name_progress,
            reverse_kwargs={'pk': project.pk},
            query_params={
                'start_date': start_date,
                'end_date': end_date,
            },
            expected_status=HTTPStatus.OK,
        ).json()
        with allure.step('Validate response body'):
            assert response.sort(key=itemgetter('id')) == expected.sort(key=itemgetter('id'))

    @pytest.mark.parametrize(
        'query_params',
        [
            {'start_date': timezone.datetime(2000, 1, 1)},
            {'end_date': timezone.datetime(2000, 1, 1)},
        ],
        ids=['only start provided', 'only end provided'],
    )
    def test_default_filter_period(
        self,
        superuser_client,
        project,
        query_params,
        test_plan_factory,
        test_factory,
        test_result_factory,
        request,
    ):
        allure.dynamic.title(f'Test period filter {request.node.callspec.id}')
        with mock.patch(
            'django.utils.timezone.now',
            return_value=timezone.make_aware(timezone.datetime(2000, 1, 2), timezone.utc),
        ):
            plan = test_plan_factory(project=project)
            test_result_factory(test=test_factory(plan=plan))

        response = superuser_client.send_request(
            self.view_name_progress,
            reverse_kwargs={'pk': project.pk},
            expected_status=HTTPStatus.OK,
            query_params=query_params,
        )
        with allure.step('Validate response body'):
            assert response.json(), 'Info about plan was not included in response.'

    @allure.title('Test default settings values')
    def test_settings_default_values(self, superuser_client, project_factory):
        with allure.step('Create project with empty settinsg'):
            project = project_factory(settings={})
        response = superuser_client.send_request(self.view_name_detail, reverse_kwargs={'pk': project.pk})
        actual_dict = response.json()
        with allure.step('Instantiate default settings'):
            project_settings = ProjectSettings()
        with allure.step('Validate result is editable set correctly'):
            assert actual_dict['settings']['is_result_editable'] == project_settings.is_result_editable
        with allure.step('Validate result edit limit set correctly'):
            assert actual_dict['settings']['result_edit_limit'] == WorkTimeProcessor.format_duration(
                project_settings.result_edit_limit,
                to_workday=False,
            )
        with allure.step('Validate project default status set correctly'):
            assert actual_dict['settings']['default_status'] == project_settings.default_status

    @allure.title('Test default status from foreign project cannot be selected')
    def test_default_from_foreign_project_forbidden(
        self,
        project_factory,
        result_status_factory,
        superuser_client,
    ):
        project_factory(settings={})
        project = project_factory()
        foreign_project = project_factory()
        foreign_status = result_status_factory(project=foreign_project)
        valid_status_no_proj = result_status_factory(project=None)
        valid_status_w_proj = result_status_factory(project=project)
        project_dict = {
            'name': constants.PROJECT_NAME,
            'description': constants.DESCRIPTION,
            'settings': {'default_status': None},
        }
        with allure.step('Validate creation with foreign status not possible'):
            project_dict['settings']['default_status'] = foreign_status.pk
            superuser_client.send_request(
                self.view_name_list,
                project_dict,
                HTTPStatus.BAD_REQUEST,
                RequestType.POST,
            )
        with allure.step('Validate creation with Not assign status possible'):
            project_dict['settings']['default_status'] = valid_status_no_proj.pk
            superuser_client.send_request(
                self.view_name_list,
                project_dict,
                HTTPStatus.CREATED,
                RequestType.POST,
            )
        with allure.step('Validate status can be updated by patch/put'):
            project_dict['settings']['default_status'] = valid_status_w_proj.pk
            for request_type in (RequestType.PATCH, RequestType.PATCH):
                superuser_client.send_request(
                    self.view_name_detail,
                    project_dict,
                    reverse_kwargs={'pk': project.pk},
                    request_type=request_type,
                )
        with allure.step('Validate validation works by patch/put'):
            project_dict['settings']['default_status'] = valid_status_no_proj.pk
            for request_type in (RequestType.PATCH, RequestType.PATCH):
                superuser_client.send_request(
                    self.view_name_detail,
                    project_dict,
                    reverse_kwargs={'pk': project.pk},
                    request_type=request_type,
                )

    @allure.title('Test status deleted from config on status_deletion')
    def test_status_deleted_from_config(self, project_factory, result_status_factory, superuser_client):
        with allure.step('Create project with empty settings'):
            project_factory(settings={})
        with allure.step('Create project to modify'):
            modified_project = project_factory()
            deleted_status = result_status_factory(project=modified_project)
            modified_project.settings['default_status'] = deleted_status.pk
            modified_project.save()
        with allure.step('Create project with status that will not be modified'):
            result = result_status_factory(project=None)
            unmodified_project = project_factory(settings={'default_status': result.pk})
            result_status_factory(project=unmodified_project)
        superuser_client.send_request(
            'api:v2:status-detail',
            reverse_kwargs={'pk': deleted_status.pk},
            request_type=RequestType.DELETE,
            expected_status=HTTPStatus.NO_CONTENT,
        )
        project_count = Project.objects.filter(settings__default_status__isnull=True).count()
        with allure.step('Validate only one project was modified after status deletion'):
            assert project_count == 1

    @allure.title('Test is_visible on project')
    def test_is_visible_annotation(
        self,
        project_factory,
        membership_factory,
        authorized_client,
        user,
        member,
    ):
        expected_number_of_visible = 5
        expected_number_of_not_visible = 5
        expected_visible = []
        expected_invisible = []
        for _ in range(expected_number_of_visible):
            project = project_factory(is_private=True)
            expected_visible.append(project.id)
            membership_factory(
                project=project,
                user=user,
                role=member,
            )
        for _ in range(expected_number_of_not_visible):
            expected_invisible.append(project_factory(is_private=True).id)
        projects_response = authorized_client.send_request(self.view_name_list).json()['results']
        visible_projects = [
            project['id'] for project in filter(lambda project: project.get('is_visible'), projects_response)
        ]
        invisible_projects = [
            project['id'] for project in filter(lambda project: not project.get('is_visible'), projects_response)
        ]
        with allure.step('Validate visible objects'):
            assert visible_projects == expected_visible
        with allure.step('Validate invisible objects'):
            assert invisible_projects == expected_invisible

    @allure.title('Test manageable flag')
    def test_is_manageable(self, project, authorized_client, user, role, admin):
        assert not authorized_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': project.pk},
        ).json()['is_manageable']
        with allure.step('Assign empty role for user on project'):
            Membership.objects.create(
                role=role,
                user=user,
                project=project,
            )
        with allure.step('Validate is_manageable is set to False'):
            assert not authorized_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': project.pk},
            ).json()['is_manageable']
        with allure.step('Assign admin role for user on project'):
            Membership.objects.create(
                role=admin,
                user=user,
                project=project,
            )
        with allure.step('Validate is manageable is set to True'):
            assert authorized_client.send_request(
                self.view_name_detail,
                reverse_kwargs={'pk': project.pk},
            ).json()['is_manageable']

    @allure.title('Test user can request access to project')
    def test_access_request(
        self,
        project_factory,
        superuser_client,
        user_factory,
        admin,
        member,
        membership_factory,
        mock_project_access_email,
    ):
        with allure.step('Create private project'):
            project = project_factory(is_private=True)
        with allure.step('Create user without role'):
            user_to_request_access = user_factory()
        with allure.step('Create admin user'):
            admin_user = user_factory()
            membership_factory(project=project, role=admin, user=admin_user)
        with allure.step('Create another admin user'):
            admin_user_spb = user_factory()
            membership_factory(project=project, role=admin, user=admin_user_spb)
        with allure.step('Login as user to request access'):
            superuser_client.force_login(user_to_request_access)
        superuser_client.send_request(
            self.view_name_access,
            data={'reason': 'I need access to your glorious project!'},
            request_type=RequestType.POST,
            reverse_kwargs={'pk': project.pk},
        )
        with allure.step('Validate access email was sent to recipients'):
            assert mock_project_access_email.called_with(recipients=[admin_user.email, admin_user_spb.email])
        with allure.step('Login as admin user'):
            superuser_client.force_login(admin_user)
        with allure.step('Resolve access request'):
            superuser_client.send_request(
                TestRoleEndpoints.view_name_assign,
                data={'project': project.pk, 'roles': [member.pk], 'user': user_to_request_access.pk},
                request_type=RequestType.POST,
            )
        with allure.step('Validate access request status is set to resolved'):
            assert AccessRequest.objects.first().status == AccessRequestStatus.RESOLVED

    @allure.title('Test spamming access request forbidden')
    def test_access_request_forbidden(
        self,
        project_factory,
        authorized_client,
        user_factory,
        membership_factory,
        member,
    ):
        with allure.step('Create private project'):
            project = project_factory(is_private=True)
        with allure.step('Create member user for project'):
            user_with_access = user_factory()
            membership_factory(project=project, user=user_with_access, role=member)
        with allure.step('Send access request'):
            authorized_client.send_request(
                self.view_name_access,
                data={'reason': 'I need access to your glorious project!'},
                request_type=RequestType.POST,
                reverse_kwargs={'pk': project.pk},
            )
        with allure.step('Send access request when first one is not resolved'):
            authorized_client.send_request(
                self.view_name_access,
                data={'reason': 'I need access to your glorious project!'},
                request_type=RequestType.POST,
                reverse_kwargs={'pk': project.pk},
                expected_status=HTTPStatus.BAD_REQUEST,
                additional_error_msg='User could send duplicate request',
            )
        with allure.step('Login as user with access'):
            authorized_client.force_login(user_with_access)
        with allure.step('Validate user cannot send access request when he has access'):
            authorized_client.send_request(
                self.view_name_access,
                data={'reason': 'I need access to your glorious project!'},
                request_type=RequestType.POST,
                reverse_kwargs={'pk': project.pk},
                expected_status=HTTPStatus.BAD_REQUEST,
                additional_error_msg='User could send duplicate request',
            )

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'])
    def test_icon_after_updating(self, api_client, authorized_superuser, project_factory, create_file, extension):
        project = project_factory(icon=create_file)
        old_icon = project.icon
        new_name = 'new_name'
        project_dict = {
            'id': project.id,
            'name': new_name,
        }
        api_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': project.pk},
            request_type=RequestType.PATCH,
            data=project_dict,
        )
        project.refresh_from_db()
        assert project.icon, 'Icon was deleted'
        api_client.send_request(self.view_name_icon, reverse_kwargs={'pk': project.pk})
        assert old_icon == project.icon, 'Icon was updated'

    @pytest.mark.parametrize('update_dict', (
        {'is_result_editable': False},
        {'is_result_editable': False, 'result_edit_limit': 6000},
        {'status_order': {'8': 1}},
        {'is_result_editable': False, 'result_edit_limit': '6000s', 'status_order': {'8': 1}},
    ))
    def test_update_settings(self, superuser_client, update_dict, project_factory):
        project = project_factory()
        expected_dict = project.settings.copy()
        expected_dict.update(update_dict)
        if 'result_edit_limit' in update_dict:
            expected_dict['result_edit_limit'] = EstimateField(to_workday=False).to_internal_value(
                expected_dict['result_edit_limit'],
            )
        expected_dict['result_edit_limit'] = WorkTimeProcessor.format_duration(
            expected_dict['result_edit_limit'],
            to_workday=False,
        )
        response = superuser_client.send_request(
            self.view_name_detail,
            reverse_kwargs={'pk': project.pk},
            request_type=RequestType.PATCH,
            data={'settings': update_dict},
        )
        assert expected_dict == response.json()['settings']

    @pytest.mark.parametrize(
        'fixture, archive, attr_name',
        [
            ('test_suite_factory', False, 'suites_count'),
            ('test_factory', True, 'tests_count'),
            ('test_plan_factory', True, 'plans_count'),
            ('test_case_factory', True, 'cases_count'),
        ],
    )
    def test_project_statistics_updated(self, project, request, fixture, archive, attr_name):
        allure.dynamic.title(f'Test statistics trigger for {attr_name}')
        expected_count = 2
        factory = request.getfixturevalue(fixture)
        soft_deleted = factory(project=project)
        hard_deleted = factory(project=project)
        project.projectstatistics.refresh_from_db()
        with allure.step('Validate insert triggers work'):
            self._validate_statistics_count(project, attr_name, expected_count)
        with allure.step('Validate soft delete triggers work'):
            soft_deleted.delete()
            self._validate_statistics_count(project, attr_name, expected_count - 1)
        with allure.step('Validate hard delete triggers work'):
            hard_deleted.hard_delete()
            self._validate_statistics_count(project, attr_name, expected_count - 2)
        if archive:
            with allure.step('Validate statistics changes for archive actions'):
                archived = factory(project=project)
                self._validate_statistics_count(project, attr_name, 1)
                archived.is_archive = True
                archived.save()
                self._validate_statistics_count(project, attr_name, 0)

    @classmethod
    def _validate_statistics_count(cls, project, attr_name, expected_count):
        project.refresh_from_db()
        assert getattr(project.projectstatistics, attr_name) == expected_count


@pytest.mark.django_db
@allure.parent_suite('Projects')
@allure.suite('Integration tests')
@allure.sub_suite('Endpoints')
class TestProjectFilters:
    view_name_list = 'api:v2:project-list'
    view_name_members = 'api:v2:project-members'

    @allure.title('Test favorites filter')
    def test_favorites_filter(self, superuser_client, superuser, project_factory):
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            project_factory(name=str(idx))
        with allure.step('Select project ids that will be favorite'):
            favorite_ids = Project.objects.filter(name__in=['3', '5']).values_list('id', flat=True)
        with allure.step('Select project ids that will not be favorite'):
            not_favorite_ids = Project.objects.filter(~Q(name__in=['3', '5'])).values_list('id', flat=True)
        user_config = {
            'projects': {
                'favorite': list(favorite_ids),
            },
        }
        with allure.step('Set favorites in config'):
            superuser.config = user_config
            superuser.save()
        with allure.step('Validate display with favorites off'):
            actual_projects = superuser_client.send_request(
                self.view_name_list,
                query_params={'favorites': False},
            ).json()['results']
            actual_ids = [project['id'] for project in actual_projects]
            expected_ids = list(deepcopy(favorite_ids))
            expected_ids.extend(list(not_favorite_ids))
            assert actual_ids == expected_ids

        actual_projects = superuser_client.send_request(
            self.view_name_list,
            query_params={'favorites': True},
        ).json()['results']
        with allure.step('Validate only favorites are displayed'):
            actual_ids = [project['id'] for project in actual_projects]
            assert actual_ids == list(favorite_ids)
        actual_projects = superuser_client.send_request(
            self.view_name_list,
            query_params={'favorites': False, 'ordering': '-name'},
        ).json()['results']
        with allure.step('Validate favorites are going before other projects if favorites is off'):
            actual_ids = [project['id'] for project in actual_projects]
            expected_ids = list(deepcopy(favorite_ids.order_by('-name')))
            expected_ids.extend(list(not_favorite_ids.order_by('-name')))
            assert actual_ids == expected_ids

    @allure.title('Test search by name')
    def test_search_by_name(self, superuser_client, project_factory):
        with allure.step('Create projects'):
            projects = [project_factory() for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
        with allure.step('Map search condition to number of objects'):
            filter_values_to_count = [
                (constants.PROJECT_NAME, constants.NUMBER_OF_OBJECTS_TO_CREATE),
                (projects[0].name, 1),
                (projects[1].name, 1),
            ]
        for filter_value, expected_number_of_objects in filter_values_to_count:
            actual_objects_count = superuser_client.send_request(
                self.view_name_list,
                query_params={'name': filter_value},
            ).json()['count']
            with allure.step(f'Validate objects count on search condition "{filter_value}"'):
                assert expected_number_of_objects == actual_objects_count
