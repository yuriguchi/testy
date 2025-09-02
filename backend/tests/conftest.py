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
import shutil
from http import HTTPStatus
from pathlib import Path
from unittest import mock

import allure
import pytest
import pytest_asyncio
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from pytest_factoryboy import register

from tests import constants
from tests.commons import CustomAPIClient, RequestType
from tests.factories import (
    AttachmentFactory,
    AttachmentTestCaseFactory,
    AttachmentTestResultFactory,
    CommentTestCaseFactory,
    CommentTestFactory,
    CommentTestPlanFactory,
    CommentTestResultFactory,
    CommentTestSuiteFactory,
    CustomAttributeFactory,
    GroupFactory,
    LabeledItemFactory,
    LabelFactory,
    MembershipFactory,
    NotificationFactory,
    NotificationSettingFactory,
    ParameterFactory,
    PermissionFactory,
    ProjectFactory,
    ResultStatusFactory,
    RoleFactory,
    SystemMessageFactory,
    TestCaseFactory,
    TestCaseWithStepsFactory,
    TestFactory,
    TestPlanFactory,
    TestPlanWithParametersFactory,
    TestResultFactory,
    TestResultWithStepsFactory,
    TestSuiteFactory,
    UserFactory,
)
from testy.core.choices import ActionCode
from testy.core.models import NotificationSetting, Project
from testy.core.selectors.custom_attribute import CustomAttributeSelector
from testy.tests_representation.models import TestResult
from testy.users.choices import UserAllowedPermissionCodenames

register(ParameterFactory)
register(ProjectFactory)
register(TestCaseFactory)
register(TestCaseWithStepsFactory, _name='test_case_with_steps')
register(TestFactory)
register(TestPlanFactory)
register(TestPlanWithParametersFactory)
register(TestResultFactory)
register(TestSuiteFactory)
register(UserFactory)
register(GroupFactory)
register(LabelFactory)
register(AttachmentTestCaseFactory, _name='attachment_test_case')
register(AttachmentTestResultFactory, _name='attachment_test_result')
register(AttachmentFactory)
register(LabeledItemFactory)
register(CommentTestFactory)
register(CommentTestCaseFactory)
register(CommentTestSuiteFactory)
register(CommentTestPlanFactory)
register(CommentTestResultFactory)
register(SystemMessageFactory)
register(RoleFactory)
register(MembershipFactory)
register(CustomAttributeFactory)
register(PermissionFactory)
register(TestResultWithStepsFactory)
register(ResultStatusFactory)
register(NotificationSettingFactory)
register(NotificationFactory)

UserModel = get_user_model()


@pytest.fixture
def api_client():
    return CustomAPIClient()


@pytest.fixture
def superuser_client(superuser, api_client):
    api_client.force_login(superuser)
    yield api_client


@pytest.fixture
def superuser(user_factory):
    yield user_factory(is_superuser=True, is_staff=True)


@pytest.fixture
def authorized_superuser(api_client, superuser):
    api_client.force_login(superuser)
    return superuser


@pytest.fixture
def authorized_client(api_client, user):
    api_client.force_login(user)
    return api_client


@pytest.fixture
def authorized_superuser_client(api_client, superuser):
    api_client.force_login(superuser)
    return api_client


@pytest.fixture
def combined_parameters(number_of_param_groups, number_of_entities_in_group, parameter_factory):
    parameters = []
    for _ in range(number_of_param_groups):
        src_param = parameter_factory()
        parameters.append(src_param.id)
        for _ in range(number_of_entities_in_group - 1):
            parameters.append(parameter_factory(group_name=src_param.group_name).id)
    number_of_combinations = pow(number_of_entities_in_group, number_of_param_groups)
    return parameters, number_of_combinations


@allure.step('Generate several test plans via api')
@pytest.fixture
def several_test_plans_from_api(api_client, authorized_superuser, parameter_factory, project):
    with allure.step('Create parameters'):
        parameters = []
        for _ in range(3):
            parameters.append(parameter_factory(project=project).id)

    test_plan_ids = []
    with allure.step('Create plans with parameterization'):
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            testplan_dict = {
                'name': f'Test plan {idx}',
                'due_date': constants.END_DATE,
                'started_at': constants.DATE,
                'parameters': parameters,
                'project': project.id,
            }
            response = api_client.send_request(
                'api:v2:testplan-list',
                testplan_dict,
                HTTPStatus.CREATED,
                RequestType.POST,
            )
            test_plan_ids.extend(plan['id'] for plan in response.json())
    yield test_plan_ids


@pytest.fixture
def generate_objects(
    project, project_factory, test_plan_factory, test_result_factory, test_suite_factory,
    test_case_factory, parameter_factory, test_factory,
):
    cases = []
    parameters = [parameter_factory(project=project) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
    for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
        parameter_factory(project=project)
    for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE + 5):
        project_factory()
    for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
        parent = test_suite_factory(project=project)
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            cases.append(test_case_factory(project=project, suite=parent))
            test_suite_factory(project=project, parent=parent)
    for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
        parent = test_plan_factory(project=project)
        parent.parameters.set(parameters)
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test_plan_factory(project=project, parent=parent)
    for case in cases:
        test = test_factory(case=case, project=project)
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test_result_factory(test=test, project=project)
    yield


@pytest.fixture
def create_file(extension, media_directory):
    media_path = Path(__file__).resolve().parent
    with open(media_path / 'media_for_tests' / 'test.png', 'rb') as file:
        png_bin = file.read()
    with open(media_path / 'media_for_tests' / 'test.jpeg', 'rb') as file:
        jpeg_bin = file.read()
    with open('tests/media_for_tests/broken_image.jpg', 'rb') as file:
        broken_image = file.read()
    extension_to_content_type = {
        '.txt': ('text/plain', b'Test content'),
        '.png': ('image/png', png_bin),
        '.jpeg': ('image/jpeg', jpeg_bin),
        '.jpg': ('image/jpeg', broken_image),
        '.pdf': ('application/pdf', b'Test content'),
        '.zip': ('application/zip', b'Test content'),
    }
    name = f'test_file{extension}'
    file = SimpleUploadedFile(
        name,
        extension_to_content_type[extension][1],
        content_type=extension_to_content_type[extension][0],
    )
    yield file


@pytest.fixture
def media_directory(settings):
    tmp_dir = 'tmp_test_media/'
    settings.MEDIA_ROOT = tmp_dir
    yield tmp_dir
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


@pytest.fixture
def data_for_cascade_tests_behaviour(
    project, test_plan_factory, test_suite_factory,
    test_case_factory, test_factory, test_result_factory, result_status_factory,
):
    parent_plan = test_plan_factory(project=project)
    test_suite = test_suite_factory(project=project)
    test_case1 = test_case_factory(project=project, suite=test_suite)
    test_case2 = test_case_factory(project=project, suite=test_suite)
    status = result_status_factory(project=project, name=constants.STATUS_NAME)
    expected_objects = {
        'project': [project],
        'testplan': [parent_plan],
        'testsuite': [test_suite],
        'testcase': [test_case1, test_case2],
        'test': [],
        'result': [],
    }
    child_test_plans = []
    for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
        test_plan = test_plan_factory(project=project, parent=parent_plan)
        child_test_plans.append(test_plan)
        expected_objects['testplan'].append(test_plan)

    for case in [test_case1, test_case2]:
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test = test_factory(case=case, plan=child_test_plans[0], project=project)
            expected_objects['test'].append(test)
            for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
                expected_objects['result'].append(test_result_factory(test=test, project=project, status=status))
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            test = test_factory(case=case, plan=child_test_plans[-1], project=project)
            expected_objects['test'].append(test)
            for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
                expected_objects['result'].append(test_result_factory(test=test, project=project, status=status))
    objects_count = {}
    for key, value in expected_objects.items():
        objects_count[key] = len(value)
    yield expected_objects, objects_count


@pytest.fixture
def generate_historical_objects(
    test_plan_factory,
    test_factory,
    test_result_factory,
    user_factory,
    result_status_factory,
):
    parent_plan = test_plan_factory()
    inner_plan = test_plan_factory(parent=parent_plan)
    plan = test_plan_factory(parent=inner_plan)
    test_list = [test_factory(plan=plan), test_factory(plan=plan)]
    status_list = [
        result_status_factory(project=test_list[0].project), result_status_factory(project=test_list[1].project),
    ]
    users_list = []
    result_list = []
    for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
        if idx % 2 == 0:
            user = user_factory(username=f'v.testovich{idx}')
            users_list.append(user)
            result_list.append(test_result_factory(user=user, status=status_list[0], test=test_list[0]))
        else:
            user = user_factory(username=f'y.testovich{idx}')
            users_list.append(user)
            result = test_result_factory(user=user, status=status_list[1], test=test_list[1])
            with mock.patch('django.utils.timezone.now', return_value=result.created_at + timezone.timedelta(days=3)):
                result.save()
    for historical_result in TestResult.history.all():
        historical_result.history_user = historical_result.history_object.user
        historical_result.save()
    return parent_plan, users_list, test_list, status_list


@pytest.fixture
def multiple_plans_data_project_statistics(project, test_plan_factory, test_result_factory, test_factory):
    root_plans = []
    with mock.patch(
        'django.utils.timezone.now',
        return_value=timezone.make_aware(timezone.datetime(2000, 1, 2), timezone.utc),
    ):
        for _ in range(5):
            plan = test_plan_factory(project=project)
            test_result_factory(test=test_factory(plan=plan), project=project)
            root_plans.append(plan)
    plans_depth_1 = []
    with mock.patch(
        'django.utils.timezone.now',
        return_value=timezone.make_aware(timezone.datetime(2000, 1, 4), timezone.utc),
    ):
        for parent_plan in root_plans:
            plan = test_plan_factory(project=project, parent=parent_plan)
            test_result_factory(test=test_factory(plan=plan), project=project)
            plans_depth_1.append(plan)
    plans_depth_2 = []
    with mock.patch(
        'django.utils.timezone.now',
        return_value=timezone.make_aware(timezone.datetime(2000, 1, 4), timezone.utc),
    ):
        for parent_plan in plans_depth_1:
            plan = test_plan_factory(project=project, parent=parent_plan)
            test_result_factory(test=test_factory(plan=plan), project=project)
            plans_depth_2.append(plan)
    start_date = timezone.datetime(2000, 1, 1).isoformat()
    end_date = timezone.datetime(2000, 1, 3).isoformat()
    expected = [
        {
            'id': plan.id,
            'tests_total': 3,
            'tests_progress_period': 1,
            'tests_progress_total': 3,
        } for plan in root_plans
    ]
    return expected, start_date, end_date


@pytest.fixture
def result_filter_data_project_statistics(project, test_plan_factory, test_result_factory, test_factory):
    root_plan = test_plan_factory(project=project)
    child_plan = test_plan_factory(project=project, parent=root_plan)
    with mock.patch(
        'django.utils.timezone.now',
        return_value=timezone.make_aware(timezone.datetime(2000, 1, 2), timezone.utc),
    ):
        for _ in range(3):
            test_result_factory(test=test_factory(plan=child_plan), project=project)
    with mock.patch(
        'django.utils.timezone.now',
        return_value=timezone.make_aware(timezone.datetime(2000, 1, 4), timezone.utc),
    ):
        test_result_factory(test=test_factory(plan=child_plan), project=project)

    start_date = timezone.datetime(2000, 1, 1).isoformat()
    end_date = timezone.datetime(2000, 1, 3).isoformat()
    expected = [
        {
            'id': plan.id,
            'tests_total': 3,
            'tests_progress_period': 1,
            'tests_progress_total': 3,
        } for plan in [root_plan, child_plan]
    ]
    return expected, start_date, end_date


@pytest.fixture
def data_different_statuses_project_statistics(
    project,
    test_plan_factory,
    test_result_factory,
    test_factory,
    result_status_factory,
):
    root_plan = test_plan_factory(project=project)
    child_plan = test_plan_factory(project=project, parent=root_plan)
    result_statuses = [result_status_factory(project=project) for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
    for day, status in zip(range(2, 12, 2), result_statuses):
        with mock.patch(
            'django.utils.timezone.now',
            return_value=timezone.make_aware(timezone.datetime(2000, 1, day), timezone.utc),
        ):
            test_result_factory(test=test_factory(plan=child_plan), project=project, status=status)

    start_date = timezone.datetime(2000, 1, 11).isoformat()
    end_date = timezone.datetime(2000, 1, 13).isoformat()
    expected = [
        {
            'tests_total': 7,
            'id': plan.id,
            'tests_progress_period': 0,
            'tests_progress_total': 6,
        } for plan in [root_plan, child_plan]
    ]
    return expected, start_date, end_date


@pytest.fixture
def empty_plan_data_project_statistics(
    project,
    test_plan_factory,
    test_result_factory,
    test_factory,
    result_status_factory,
):
    root_plan = test_plan_factory(project=project)
    root_plan_2 = test_plan_factory(project=project, parent=root_plan)
    with mock.patch(
        'django.utils.timezone.now',
        return_value=timezone.make_aware(timezone.datetime(2000, 1, 2), timezone.utc),
    ):
        test_result_factory(
            test=test_factory(plan=root_plan_2),
            project=project,
            status=result_status_factory(project=project),
        )
    start_date = timezone.datetime(2000, 1, 1).isoformat()
    end_date = timezone.datetime(2000, 1, 3).isoformat()
    expected = [
        {
            'tests_total': 0,
            'id': root_plan.id,
            'tests_progress_period': 0,
            'tests_progress_total': 0,
        },
        {
            'tests_count': 1,
            'id': root_plan_2.id,
            'tests_progress_period': 1,
            'tests_progress_total': 1,
        },
    ]
    return expected, start_date, end_date


@pytest.fixture
def use_dummy_cache_backend(settings):
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
    }


@pytest.fixture
def cases_with_labels(
    label_factory,
    test_plan_factory,
    labeled_item_factory,
    test_case_factory,
    test_result_factory,
    test_factory,
    project,
    result_status_factory,
    test_suite,
):
    test_plan = test_plan_factory(project=project)
    label_blue_bank = label_factory(name='blue_bank')
    label_green_bank = label_factory(name='green_bank')
    label_red_bank = label_factory(name='red_bank')
    test_cases = [test_case_factory(project=project, suite=test_suite) for _ in range(10)]
    status = result_status_factory(project=project)
    for idx in range(10):
        if not idx % 2:
            labeled_item_factory(label=label_blue_bank, content_object=test_cases[idx])
        if not idx % 3:
            labeled_item_factory(label=label_green_bank, content_object=test_cases[idx])
        if not idx % 5:
            labeled_item_factory(label=label_red_bank, content_object=test_cases[idx])
        test_result_factory(
            test=test_factory(plan=test_plan, case=test_cases[idx], project=project),
            status=status,
            project=project,
        )
    return [label_blue_bank, label_green_bank, label_red_bank], test_cases, test_plan, status


@pytest.fixture
def test_suite_with_cases(test_suite, test_case_factory):
    for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
        test_case_factory(suite=test_suite)
    return test_suite


@pytest.fixture
def member(role_factory):
    yield role_factory(
        name='Member',
        permissions=Permission.objects.filter(
            codename__in=[
                UserAllowedPermissionCodenames.VIEW_PROJECT,
                UserAllowedPermissionCodenames.ADD_RESULT,
                UserAllowedPermissionCodenames.CHANGE_RESULT,
            ],
        ),
    )


@pytest.fixture
def external(role_factory, permission_factory):
    yield role_factory(
        name='External',
        permissions=[
            permission_factory(
                codename=UserAllowedPermissionCodenames.VIEW_PROJECT_RESTRICTION,
                content_type=ContentType.objects.get_for_model(Project),
            ),
        ],
    )


@pytest.fixture
def admin(role_factory):
    yield role_factory(
        name='Admin',
        permissions=Permission.objects.filter(
            codename__in=UserAllowedPermissionCodenames.values,
        ),
    )


@pytest.fixture
def allowed_content_types():
    return list(CustomAttributeSelector.get_allowed_content_types().values_list('id', flat=True))


@pytest.fixture(autouse=True, scope='session')
def mock_project_access_email():
    with mock.patch('testy.root.tasks.project_access_email.delay') as project_access_mock:
        yield project_access_mock


@allure.step('Generate data for suites')
@pytest.fixture
def generate_projects_and_suites(project_factory, test_suite_factory):
    with allure.step('Create 3 projects'):
        projects = [project_factory() for _ in range(3)]
    with allure.step('Create 2 suites in each project'):
        for _ in range(2):
            for project in projects:
                test_suite_factory(project=project)
    yield projects


@pytest.fixture
def default_notify_settings(notification_setting_factory):
    NotificationSetting.deleted_objects.all().delete()
    action_code = 'action_code'
    settings_data = [
        {
            action_code: ActionCode.TEST_ASSIGNED,
            'message': '{{{{placeholder}}}} was assigned to you by {actor}',
            'verbose_name': 'Test assigned',
            'placeholder_link': '/projects/{project_id}/plans/{plan_id}?test={test_id}',
            'placeholder_text': 'Test {name}',
        },
        {
            action_code: ActionCode.TEST_UNASSIGNED,
            'message': '{{{{placeholder}}}} was unassigned by {actor}',
            'verbose_name': 'Test unassigned',
            'placeholder_link': '/projects/{project_id}/plans/{plan_id}?test={test_id}',
            'placeholder_text': 'Test {name}',
        },
    ]
    settings = []
    for settings_data in settings_data:
        setting = notification_setting_factory(**settings_data)
        settings.append(setting.pk)
    yield settings


@allure.step('Mock channel layer to in-memory storage')
@pytest.fixture
def mock_notifications_channel_layer(settings):
    settings.CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
    with mock.patch('testy.core.services.notifications.channel_layer', get_channel_layer()):
        yield


@allure.step('Mock channel layer to in-memory storage')
@pytest.fixture
def mock_tests_channel_layer(settings):
    settings.CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
    with mock.patch('testy.tests_representation.services.tests.channel_layer', get_channel_layer()):
        yield


@pytest.fixture
def notification_tests_teardown():
    yield
    UserModel.objects.all().delete()
    NotificationSetting.deleted_objects.all().delete()


@pytest_asyncio.fixture
async def subscribed_user(notification_setting_factory, user_factory):
    def wrapper():
        NotificationSetting.deleted_objects.all().delete()
        user = user_factory()
        setting = notification_setting_factory(
            action_code=ActionCode.TEST_ASSIGNED,
            message='{{{{placeholder}}}} was assigned to you by {actor}',
            verbose_name='Test assigned',
            placeholder_link='/projects/{project_id}/plans/{plan_id}?test={test_id}',
            placeholder_text='Test {name}',
        )
        setting.subscribers.add(user)
        return user

    yield await database_sync_to_async(wrapper)()

    def teardown_wrapper():
        NotificationSetting.objects.all().delete()
        UserModel.objects.all().delete()

    await database_sync_to_async(teardown_wrapper)()
