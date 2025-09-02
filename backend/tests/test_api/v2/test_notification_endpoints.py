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
from contextlib import asynccontextmanager
from http import HTTPStatus

import allure
import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from notifications.models import Notification

from tests.commons import RequestType, model_to_dict_via_serializer
from tests.mock_serializers.v2 import NotificationSettingMockSerializer
from testy.core.api.v2.serializers import NotificationSerializer
from testy.core.choices import ActionCode
from testy.core.models import NotificationSetting
from testy.core.services.notifications import NotificationService
from testy.root.asgi import application


@allure.parent_suite('Test notifications')
@allure.suite('Integration tests')
@allure.sub_suite('Endpoints')
@pytest.mark.django_db
class TestNotificationEndpoints:
    view_name_list = 'api:v2:notification-list'
    view_name_enable = 'api:v2:notification-enable'
    view_name_disable = 'api:v2:notification-disable'
    view_name_settings = 'api:v2:notification-settings'
    view_name_mark_as = 'api:v2:notification-mark-as'

    @allure.title('Test notifications list display')
    def test_notification_list(self, user, authorized_client, notification_factory, test):
        with allure.step('Create notifications'):
            notifications = [notification_factory(recipient=user, actor=user, target=test) for _ in range(5)]
            expected = model_to_dict_via_serializer(notifications, NotificationSerializer, many=True)
        resp_body = authorized_client.send_request(self.view_name_list, query_params={'ordering': 'id'}).json_strip()
        with allure.step('Validate response body'):
            assert resp_body == expected

    @allure.title('Test notifications settings display')
    def test_notification_settings_list(self, user, authorized_client, default_notify_settings):
        with allure.step('Enable single notification setting'):
            NotificationSetting.objects.first().subscribers.add(user)
        expected = model_to_dict_via_serializer(
            NotificationSetting.objects.all(),
            NotificationSettingMockSerializer,
            many=True,
            requested_user=user,
        )
        resp_body = authorized_client.send_request(self.view_name_settings).json_strip(is_paginated=False)
        with allure.step('Validate response body'):
            assert resp_body == expected

    @allure.title('Test notifications enabling')
    def test_notification_enabling(
        self,
        mock_notifications_channel_layer,
        authorized_client,
        default_notify_settings,
        test,
        user,
    ):
        setting = NotificationSetting.objects.get(action_code=ActionCode.TEST_ASSIGNED)
        with allure.step('Enable notifications via api'):
            authorized_client.send_request(
                self.view_name_enable,
                data={'settings': [setting.pk]},
                request_type=RequestType.POST,
            )
        with allure.step('Notify user via service about case assignment'):
            NotificationService.notify_user(
                test,
                user,
                ActionCode.TEST_ASSIGNED,
                actor=user,
                name=test.case.name,
                project_id=test.project.pk,
                plan_id=test.plan.pk,
                test_id=test.pk,
            )
        with allure.step('Notify user via service about case unassignment'):
            NotificationService.notify_user(
                test,
                user,
                ActionCode.TEST_UNASSIGNED,
                name=test.case.name,
                actor=user,
            )
        assert Notification.objects.filter(
            unread=True,
        ).count() == 1, 'Only subscribed notification should be created'

    @allure.title('Test notifications disabling')
    def test_notification_disabling(self, authorized_client, default_notify_settings, test, user):
        settings = NotificationSetting.objects.filter(pk__in=default_notify_settings)
        for setting in settings:
            setting.subscribers.add(user)
        with allure.step('Disable notifications via api'):
            authorized_client.send_request(
                self.view_name_disable,
                data={'settings': default_notify_settings},
                request_type=RequestType.POST,
            )
        with allure.step('Notify user via service about case unassignment'):
            NotificationService.notify_user(
                test,
                user,
                ActionCode.TEST_UNASSIGNED,
                name=test.case.name,
                actor=user,
            )
        with allure.step('Validate notifications did not appear'):
            assert not Notification.objects.filter(unread=True).count()

    @pytest.mark.parametrize('unread', [True, False], ids=['unread', 'read'])
    def test_mark_as(
        self,
        mock_notifications_channel_layer,
        user,
        authorized_client,
        test,
        notification_factory,
        unread,
    ):
        action = 'unread' if unread else 'read'
        allure.dynamic.title(f'Test mark as {action}')
        notifications_count = 5
        unread_ids = []
        with allure.step(f'Create {notifications_count} notifications'):
            for _ in range(notifications_count):
                notification = notification_factory(target=test, actor=user, recipient=user, unread=True)
                unread_ids.append(notification.id)

        with allure.step(f'Mark notifications as {action}'):
            authorized_client.send_request(
                self.view_name_mark_as,
                data={'notifications': unread_ids, 'unread': unread},
                request_type=RequestType.POST,
            )
        with allure.step('Validate notifications were marked as unread'):
            assert Notification.objects.filter(unread=unread).count() == notifications_count

    @allure.title('Test user does not have access to others notifications')
    def test_notifications_access(self, test, user_factory, notification_factory, api_client):
        user_seeing = user_factory()
        user_unseeing = user_factory()
        notifications_count = 3
        invisible_ids = []
        with allure.step('Create notifications that will be visible for user'):
            for _ in range(notifications_count):
                notification_factory(target=test, actor=user_seeing, recipient=user_seeing, unread=True)
        with allure.step('Create notifications for another user'):
            for _ in range(notifications_count):
                notification = notification_factory(
                    target=test,
                    actor=user_unseeing,
                    recipient=user_unseeing,
                    unread=True,
                )
                invisible_ids.append(notification.id)
        api_client.force_login(user_seeing)
        response_body = api_client.send_request(self.view_name_list).json_strip(is_paginated=False)
        with allure.step('Validate only visible objects are visible'):
            assert response_body['count'] == notifications_count
        with allure.step('Validate actions on invisible objects are not allowed'):
            api_client.send_request(
                self.view_name_mark_as,
                data={'notifications': invisible_ids, 'unread': False},
                request_type=RequestType.POST,
                expected_status=HTTPStatus.BAD_REQUEST,
            )

    @asynccontextmanager
    async def notifications_socket(self, user_id):
        communicator = WebsocketCommunicator(
            application=application,
            path=f'/ws/notifications/{user_id}/',
        )
        connected, _ = await communicator.connect()
        assert connected is True, 'Could not establish connection with websocket.'
        try:
            yield communicator
        finally:
            await communicator.disconnect()

    @allure.title('Test notifications sent')
    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_websock_notify_count(self, mock_notifications_channel_layer, test, subscribed_user):
        async with self.notifications_socket(subscribed_user.id) as socket:
            resp_json = await socket.receive_json_from()
            assert resp_json['count'] == 0, 'Initial count should be 0'
            await database_sync_to_async(NotificationService.notify_user)(
                test,
                subscribed_user,
                ActionCode.TEST_ASSIGNED,
                actor=subscribed_user,
                name=test.case.name,
                project_id=test.project.pk,
                plan_id=test.plan.pk,
                test_id=test.pk,
            )
            resp_json = await socket.receive_json_from()
            assert resp_json['count'] == 1
