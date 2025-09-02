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

from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer

from testy.core.choices import ActionCode
from testy.core.constants import NOTIFICATION_COUNT_GROUP
from testy.core.services.notifications import NotificationService
from testy.core.tasks import notify_user
from testy.users.selectors.users import UserSelector


class WebsocketNotificationConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.notifications_count_receiver = NOTIFICATION_COUNT_GROUP.format(user_id=self.user_id)

        async_to_sync(self.channel_layer.group_add)(
            self.notifications_count_receiver,
            self.channel_name,
        )
        user = UserSelector.user_by_id(self.user_id)
        if user:
            NotificationService.change_notifications_count(user=user)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.notifications_count_receiver,
            self.channel_name,
        )

    def notifications_count(self, event):
        self.send_json({'count': event.get('count', 0)})


class NotificationConsumer(SyncConsumer):
    def test_assigned(self, event):
        event.pop('type')
        event['action_code'] = ActionCode.TEST_ASSIGNED
        notify_user.delay(event)

    def test_unassigned(self, event):
        event.pop('type')
        event['action_code'] = ActionCode.TEST_UNASSIGNED
        notify_user.delay(event)
