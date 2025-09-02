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
import operator
from functools import reduce
from typing import Any, Callable

import humanize
import timeago
from core.constants import CUSTOM_ATTRIBUTES_ALLOWED_APPS, CUSTOM_ATTRIBUTES_ALLOWED_MODELS
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from notifications.models import Notification
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (
    BooleanField,
    CharField,
    DateTimeField,
    IntegerField,
    JSONField,
    ListField,
    SerializerMethodField,
)
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import HyperlinkedIdentityField, ModelSerializer, Serializer

from testy.core.models import Attachment, CustomAttribute, Label, NotificationSetting, Project, SystemMessage
from testy.core.selectors.custom_attribute import CustomAttributeSelector
from testy.core.selectors.notifications import NotificationSelector
from testy.core.selectors.project_settings import ProjectSettings
from testy.core.validators import CustomAttributeV1CreateValidator, DefaultStatusValidator, ProjectStatusOrderValidator
from testy.serializer_fields import EstimateField


class LabelSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:label-detail')
    username = SerializerMethodField()

    class Meta:
        model = Label
        fields = ('id', 'url', 'name', 'username', 'type', 'user', 'project')
        ref_name = 'LabelV1'

    def get_username(self, instance) -> str | None:
        if instance.user is not None:
            return instance.user.username
        return None


class CustomAttributeBaseSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:customattribute-detail')

    class Meta:
        model = CustomAttribute
        fields = (
            'id',
            'url',
            'project',
            'name',
            'type',
            'is_deleted',
        )
        ref_name = 'CustomAttributeBaseV1'


class CustomAttributeInputSerializer(CustomAttributeBaseSerializer):
    content_types = PrimaryKeyRelatedField(
        queryset=CustomAttributeSelector.get_allowed_content_types(),
        many=True,
        allow_empty=False,
        allow_null=False,
    )
    is_required = BooleanField(required=False, allow_null=False, default=False, initial=False)
    suite_ids = ListField(
        child=IntegerField(),
        allow_null=False,
        allow_empty=True,
        required=False,
        default=list,
        initial=list,
    )
    status_specific = ListField(
        child=IntegerField(),
        allow_null=True,
        allow_empty=True,
        required=False,
        default=list,
        initial=list,
    )

    class Meta:
        model = CustomAttribute
        fields = CustomAttributeBaseSerializer.Meta.fields + (
            'content_types', 'is_required', 'suite_ids', 'status_specific',
        )

        validators = [CustomAttributeV1CreateValidator()]
        ref_name = 'CustomAttributeInputV1'


class CustomAttributeOutputSerializer(CustomAttributeBaseSerializer):
    is_required = SerializerMethodField()
    suite_ids = SerializerMethodField()
    status_specific = SerializerMethodField()
    content_types = SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_content_types = ContentType.objects.filter(
            app_label__in=CUSTOM_ATTRIBUTES_ALLOWED_APPS,
            model__in=CUSTOM_ATTRIBUTES_ALLOWED_MODELS,
        ).values('id', 'model')

    class Meta:
        model = CustomAttribute
        fields = CustomAttributeInputSerializer.Meta.fields
        ref_name = 'CustomAttributeOutputSerializerV1'

    def get_is_required(self, instance):
        is_required = self._get_field_by_name(instance.applied_to, 'is_required', operator.or_)
        return bool(is_required)

    def get_status_specific(self, instance):
        status_specific = self._get_field_by_name(instance.applied_to, 'status_specific', operator.add)
        if not status_specific:
            return []
        return list(set(status_specific))

    def get_suite_ids(self, instance):
        suite_ids = self._get_field_by_name(instance.applied_to, 'suite_ids', operator.add)
        if not suite_ids:
            return []
        return list(set(suite_ids))

    def get_content_types(self, instance):
        content_types = []
        for content_type in self.allowed_content_types:
            if content_type['model'] in instance.applied_to.keys():
                content_types.append(content_type['id'])
        return content_types

    @classmethod
    def _get_field_by_name(
        cls,
        applied_to: dict[str, Any],
        field_name: str,
        reduce_func: Callable,
    ) -> Any:
        fields_value = [field.get(field_name) for field in applied_to.values() if field.get(field_name)]
        if not fields_value:
            return None
        return reduce(reduce_func, fields_value)


class ContentTypeSerializer(ModelSerializer):
    name = SerializerMethodField()

    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model', 'name']
        ref_name = 'ContentTypeV1'

    def get_name(self, instance) -> str:
        return instance.name.title()


class ProjectSettingsSerializer(Serializer):
    is_result_editable = BooleanField(
        allow_null=False,
        default=ProjectSettings().is_result_editable,
    )
    result_edit_limit = EstimateField(
        allow_null=True,
        default=ProjectSettings().result_edit_limit,
        to_workday=False,
    )
    status_order = JSONField(
        default=dict,
        validators=[ProjectStatusOrderValidator()],
    )
    default_status = IntegerField(
        allow_null=True,
        required=False,
    )

    class Meta:
        validators = [
            DefaultStatusValidator(),
        ]
        ref_name = 'ProjectSettingsV1'


class ProjectSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:project-detail')
    settings = ProjectSettingsSerializer(required=False)

    class Meta:
        model = Project
        fields = ('id', 'url', 'name', 'description', 'is_archive', 'icon', 'settings', 'is_private')
        ref_name = 'ProjectSerializerV1'


class ProjectRetrieveSerializer(ProjectSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:project-detail')
    icon = SerializerMethodField(read_only=True)
    is_manageable = BooleanField(read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ('is_manageable',)
        ref_name = 'ProjectRetrieveV1'

    def get_icon(self, instance):
        if not instance.icon:
            return ''
        return self.context['request'].build_absolute_uri(
            reverse('api:v1:project-icon', kwargs={'pk': instance.id}),
        )


class ProjectStatisticsSerializer(ProjectRetrieveSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:project-detail')
    is_visible = BooleanField(read_only=True)
    cases_count = IntegerField()
    suites_count = IntegerField()
    plans_count = IntegerField()
    tests_count = IntegerField()

    class Meta:
        model = Project
        fields = ProjectRetrieveSerializer.Meta.fields + (
            'cases_count', 'suites_count', 'plans_count', 'tests_count', 'is_visible',
        )
        ref_name = 'ProjectStatisticsV1'


class AllProjectsStatisticSerializer(Serializer):
    projects_count = IntegerField()
    cases_count = IntegerField()
    suites_count = IntegerField()
    plans_count = IntegerField()
    tests_count = IntegerField()

    class Meta:
        ref_name = 'AllProjectsStatisticV1'


class AttachmentSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:attachment-detail')
    size_humanize = SerializerMethodField()
    link = SerializerMethodField(read_only=True)

    class Meta:
        model = Attachment
        fields = (
            'id', 'project', 'comment', 'name', 'filename', 'file_extension', 'size', 'size_humanize', 'content_type',
            'object_id', 'user', 'file', 'url', 'link',
        )

        read_only_fields = ('name', 'filename', 'file_extension', 'size', 'user', 'url')
        extra_kwargs = {'file': {'write_only': True}}
        ref_name = 'AttachmentV1'

    def get_size_humanize(self, instance):
        return humanize.naturalsize(instance.size)

    def get_link(self, instance):
        return self.context['request'].build_absolute_uri(
            reverse('attachment-path', kwargs={'pk': instance.id}),
        )

    def validate(self, attrs):
        content_type = attrs.get('content_type')
        object_id = attrs.get('object_id')

        if content_type is None:
            return attrs

        if not content_type.model_class().objects.all().filter(pk=object_id):
            raise ValidationError(f'Specified model does not have object with id {object_id}')

        return attrs


class SystemMessageSerializer(ModelSerializer):
    class Meta:
        model = SystemMessage
        fields = ('id', 'created_at', 'updated_at', 'content', 'level', 'is_closing')
        ref_name = 'SystemMessageV1'


class CopyDetailSerializer(Serializer):
    id = IntegerField(required=True)
    new_name = CharField(required=False)

    class Meta:
        ref_name = 'CopyDetailV1'


class AccessRequestSerializer(Serializer):
    reason = CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        ref_name = 'AccessRequestV1'


class NotificationSerializer(ModelSerializer):
    actor = CharField(source='actor.username', read_only=True)
    timeago = SerializerMethodField()
    timestamp = DateTimeField(read_only=True)
    message = SerializerMethodField()

    @classmethod
    def get_message(cls, instance: Notification):
        return instance.data

    @classmethod
    def get_timeago(cls, instance: Notification):
        return timeago.format(timezone.now() - instance.timestamp)

    class Meta:
        model = Notification
        fields = (
            'id',
            'unread',
            'actor',
            'timestamp',
            'timeago',
            'message',
        )
        ref_name = 'NotificationV1'


class NotificationSettingSerializer(ModelSerializer):
    enabled = BooleanField(read_only=True)

    class Meta:
        model = NotificationSetting
        fields = ('action_code', 'verbose_name', 'enabled')
        ref_name = 'NotificationSettingV1'


class ModifyNotificationsSettingsSerializer(Serializer):
    settings = PrimaryKeyRelatedField(
        queryset=NotificationSelector.list_notification_settings(),
        many=True,
        required=True,
    )

    class Meta:
        ref_name = 'ModifyNotificationsSettingsV1'


class MarkNotificationSerializer(Serializer):
    unread = BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (request := self.context.get('request')) and request.user:
            self.fields['notifications'] = PrimaryKeyRelatedField(
                many=True,
                queryset=NotificationSelector.list_notifications(request.user),
                allow_empty=True,
            )

    class Meta:
        ref_name = 'MarkNotificationV1'
