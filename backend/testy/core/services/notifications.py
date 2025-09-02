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
from typing import Iterable

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Model
from notifications.models import Notification
from notifications.signals import notify

from testy.core.choices import ActionCode
from testy.core.constants import NOTIFICATION_COUNT_GROUP
from testy.core.models import NotificationSetting
from testy.users.models import User

channel_layer = get_channel_layer()


class NotificationService:

    @classmethod
    def notify_user(
        cls,
        instance: Model,
        receiver: User,
        action_code: ActionCode,
        actor: Model,
        non_user_actor: str = '',
        **kwargs,
    ) -> None:
        kwargs['actor'] = actor.username if isinstance(actor, User) else non_user_actor
        action = NotificationSetting.objects.filter(subscribers=receiver, action_code=action_code).first()
        if action is None:
            return
        notify.send(
            actor,
            target=instance,
            recipient=receiver,
            verb=action.message.format(**kwargs),
            template=action.message.format(**kwargs),
            placeholder_text=action.placeholder_text.format(**kwargs),
            placeholder_link=action.placeholder_link.format(**kwargs),
        )

    @classmethod
    def change_notifications_count(cls, user: User) -> None:
        async_to_sync(channel_layer.group_send)(
            NOTIFICATION_COUNT_GROUP.format(user_id=user.id),
            {
                'type': 'notifications.count',
                'count': user.notifications.unread().count(),
            },
        )

    @classmethod
    def mark_as(cls, unread: bool, user: User, notifications: list[Notification] | None = None) -> list[int]:
        qs = Notification.objects.filter(recipient=user)
        if notifications:
            qs = qs.filter(pk__in=[notification.pk for notification in notifications])
        updated = qs.update(unread=unread)
        cls.change_notifications_count(user)
        return updated

    @classmethod
    def enable_notifications(cls, user: User, settings: Iterable[NotificationSetting]) -> list[NotificationSetting]:
        through_model = NotificationSetting.subscribers.through
        instances = [through_model(notificationsetting=code, user_id=user.id) for code in settings]
        return through_model.objects.bulk_create(instances, ignore_conflicts=True)

    @classmethod
    def disable_notifications(cls, user: User, settings: Iterable[NotificationSetting]) -> None:
        through_model = NotificationSetting.subscribers.through
        through_model.objects.filter(user_id=user.id, notificationsetting__in=settings).delete()
