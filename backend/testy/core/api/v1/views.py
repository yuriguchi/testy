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
from pathlib import Path

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from notifications.models import Notification
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from testy import permissions
from testy.core.api.v1.serializers import (
    AccessRequestSerializer,
    AllProjectsStatisticSerializer,
    AttachmentSerializer,
    ContentTypeSerializer,
    CustomAttributeInputSerializer,
    CustomAttributeOutputSerializer,
    LabelSerializer,
    MarkNotificationSerializer,
    ModifyNotificationsSettingsSerializer,
    NotificationSerializer,
    NotificationSettingSerializer,
    ProjectRetrieveSerializer,
    ProjectSerializer,
    ProjectStatisticsSerializer,
    SystemMessageSerializer,
)
from testy.core.filters import (
    AttachmentFilter,
    CustomAttributeFilter,
    LabelFilter,
    NotificationFilter,
    NotificationSettingFilter,
    ProjectFilter,
    ProjectOrderingFilter,
)
from testy.core.mixins import MediaViewMixin
from testy.core.models import Project, SystemMessage
from testy.core.permissions import (
    AttachmentPermission,
    BaseProjectPermission,
    ProjectIsPrivatePermission,
    ProjectPermission,
)
from testy.core.selectors.attachments import AttachmentSelector
from testy.core.selectors.custom_attribute import CustomAttributeSelector
from testy.core.selectors.labels import LabelSelector
from testy.core.selectors.notifications import NotificationSelector
from testy.core.selectors.projects import ProjectSelector
from testy.core.services.attachments import AttachmentService
from testy.core.services.custom_attribute import CustomAttributeService
from testy.core.services.labels import LabelService
from testy.core.services.notifications import NotificationService
from testy.core.services.projects import ProjectService
from testy.paginations import StandardSetPagination
from testy.root.mixins import TestyArchiveMixin, TestyDestroyModelMixin, TestyModelViewSet, TestyRestoreModelMixin
from testy.swagger.v1.custom_attributes import (
    custom_attributes_allowed_content_types,
    custom_attributes_create_schema,
    custom_attributes_update_schema,
)
from testy.swagger.v1.notifications import (
    disable_notifications_schema,
    enable_notifications_schema,
    notification_list_schema,
    notification_mark_as_schema,
)
from testy.swagger.v1.projects import (
    project_access_schema,
    project_create_schema,
    project_list_schema,
    project_members_schema,
    project_progress_schema,
    project_update_schema,
)
from testy.tests_representation.api.v1.serializers import (
    ParameterSerializer,
    TestPlanProgressSerializer,
    TestPlanTreeSerializer,
)
from testy.tests_representation.selectors.parameters import ParameterSelector
from testy.tests_representation.selectors.testplan import TestPlanSelector
from testy.users.api.v1.serializers import UserRoleSerializer
from testy.users.filters import UserFilter
from testy.users.models import Membership, User
from testy.users.selectors.roles import RoleSelector
from testy.users.services.roles import RoleService
from testy.utilities.request import PeriodDateTime

_GET = 'get'
_MEMBERS = 'members'
_LIST = 'list'
_POST = 'post'
_SETTINGS = 'settings'


class ProjectViewSet(TestyModelViewSet, TestyArchiveMixin, MediaViewMixin):
    queryset = ProjectSelector.project_list_raw()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, ProjectOrderingFilter]
    permission_classes = [permissions.IsAdminOrForbidArchiveUpdate, ProjectPermission, ProjectIsPrivatePermission]
    ordering_fields = ['name', 'is_archive']
    pagination_class = StandardSetPagination
    lookup_value_regex = r'\d+'
    schema_tags = ['Projects']

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return ProjectFilter
        if self.action == _MEMBERS:
            return UserFilter

    def get_queryset(self):
        project_selector = ProjectSelector(self.request.user)
        if self.action in {'recovery_list', 'restore', 'delete_permanently'}:
            return project_selector.project_deleted_list()
        if self.action in {_LIST, 'retrieve'}:
            return project_selector.project_list_statistics()
        return project_selector.project_list()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectRetrieveSerializer
        if self.action == _LIST:
            return ProjectStatisticsSerializer
        if self.action == _MEMBERS:
            return UserRoleSerializer
        if self.action == 'testplans_by_project':
            return TestPlanTreeSerializer
        if self.action == 'parameters_by_project':
            return ParameterSerializer
        return ProjectSerializer

    @project_members_schema
    @action(methods=[_GET], url_path=_MEMBERS, url_name=_MEMBERS, detail=True)
    def members(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        self.check_object_permissions(request, project)
        users = User.objects.filter(memberships__project=project).distinct().prefetch_related(
            Prefetch('memberships', queryset=Membership.objects.filter(project=project)),
            'groups',
            'memberships__role',
            'memberships__role__permissions',
        ).order_by('-id')
        qs = self.filter_queryset(users)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)

    @action(methods=[_GET], url_path='testplans', url_name='testplans', detail=True)
    def testplans_by_project(self, request, pk):
        qs = TestPlanSelector().testplan_project_root_list(project_id=pk)
        serializer = self.get_serializer(qs, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    @project_access_schema
    @action(methods=[_POST], url_path='access', url_name='access', detail=True)
    def request_access(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if RoleSelector.access_request_pending_list(project, request.user):
            raise ValidationError('You already requested access to this project.')
        if RoleSelector.project_view_allowed(request.user, pk):
            raise ValidationError('You already have read access to project.')
        serializer = AccessRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # noqa: WPS204
        RoleService.access_request_create(project, request.user, serializer.validated_data.get('reason'))
        return Response(data='Request sent!')

    @action(methods=[_GET], url_path='parameters', url_name='parameters', detail=True)
    def parameters_by_project(self, request, pk):
        qs = ParameterSelector().parameter_project_list(project_id=pk)
        serializer = self.get_serializer(qs, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(methods=[_GET], url_path='icon', url_name='icon', detail=True)
    def icon(self, request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        if not project.icon or not project.icon.storage.exists(project.icon.path):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return self.format_response(project.icon, request)

    @project_progress_schema
    @action(methods=[_GET], url_path='progress', url_name='progress', detail=True)
    def project_progress(self, request, pk):
        period = PeriodDateTime(request, 'start_date', 'end_date')
        plans = ProjectSelector().project_progress(
            pk, period=period,
        )
        return Response(TestPlanProgressSerializer(plans, many=True).data)

    @project_list_schema
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)

    @project_create_schema
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = ProjectService().project_create(serializer.validated_data, request.user)
        return Response(
            ProjectRetrieveSerializer(instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @project_update_schema
    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_instance = ProjectService().project_update(instance, serializer.validated_data)
        return Response(ProjectRetrieveSerializer(new_instance, context=self.get_serializer_context()).data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        if instance.icon:
            ProjectService().remove_media(Path(instance.icon.path))
        return super().destroy(request, pk, *args, **kwargs)


class AttachmentViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = AttachmentSelector().attachment_list()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated, AttachmentPermission]
    filter_backends = [DjangoFilterBackend]
    schema_tags = ['Attachments']

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return AttachmentFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachments = AttachmentService().attachment_create(serializer.validated_data, request)
        data = [
            self.get_serializer(
                attachment,
                context=self.get_serializer_context(),
            ).data for attachment in attachments
        ]
        return Response(data, status=status.HTTP_201_CREATED)


class LabelViewSet(TestyModelViewSet):
    queryset = LabelSelector().label_list()
    serializer_class = LabelSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated, BaseProjectPermission]
    schema_tags = ['Labels']

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return LabelFilter

    def perform_create(self, serializer: ProjectSerializer):
        serializer.instance = LabelService().label_create(serializer.validated_data)

    def perform_update(self, serializer: ProjectSerializer):
        serializer.instance = LabelService().label_update(serializer.instance, serializer.validated_data)


class SystemMessagesViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = SystemMessageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return SystemMessage.objects.filter(is_active=True).order_by('-updated_at')


class SystemStatisticViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Project.objects.none()
    serializer_class = AllProjectsStatisticSerializer
    schema_tags = ['Statistics']

    def list(self, request, *args, **kwargs):
        statistic = ProjectSelector(request.user).all_projects_statistic()
        serializer = AllProjectsStatisticSerializer(statistic)
        return Response(serializer.data)


class CustomAttributeViewSet(TestyModelViewSet):
    queryset = CustomAttributeSelector().custom_attribute_list()
    serializer_class = CustomAttributeInputSerializer
    filter_backends = [DjangoFilterBackend]
    schema_tags = ['Custom attributes']

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return CustomAttributeFilter

    def get_serializer_class(self):
        if self.action in {_LIST, 'retrieve'}:
            return CustomAttributeOutputSerializer
        return CustomAttributeInputSerializer

    @custom_attributes_allowed_content_types
    @action(methods=[_GET], url_path='content-types', url_name='content-types', detail=False)
    def get_allowed_content_types(self, request):
        allowed_content_types = CustomAttributeSelector.get_allowed_content_types()
        return Response(ContentTypeSerializer(allowed_content_types, many=True).data, status=status.HTTP_200_OK)

    @custom_attributes_create_schema
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        custom_attribute = CustomAttributeService().custom_attribute_create_v1(serializer.validated_data)
        return Response(
            CustomAttributeOutputSerializer(custom_attribute, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @custom_attributes_update_schema
    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_instance = CustomAttributeService().custom_attribute_update_v1(instance, serializer.validated_data)
        return Response(CustomAttributeOutputSerializer(new_instance, context=self.get_serializer_context()).data)


@notification_list_schema
class NotificationViewSet(
    mixins.RetrieveModelMixin,
    TestyDestroyModelMixin,
    TestyRestoreModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Notification.objects.none()
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardSetPagination
    schema_tags = ['Notifications']

    @property
    def filterset_class(self):
        if self.action == _LIST:
            return NotificationFilter
        if self.action == 'notification_settings':
            return NotificationSettingFilter

    def get_queryset(self):
        if self.action in {'enable_notifications', 'disable_notifications', 'notification_settings'}:
            return NotificationSelector.list_notification_settings(self.request.user)
        return NotificationSelector.list_notifications(self.request.user)

    def get_serializer_class(self):
        if self.action in {'enable_notifications', 'disable_notifications'}:
            return ModifyNotificationsSettingsSerializer
        if self.action == 'notification_settings':
            return NotificationSettingSerializer
        if self.action == 'mark_as':
            return MarkNotificationSerializer
        return NotificationSerializer

    @action(methods=['get'], url_name=_SETTINGS, url_path=_SETTINGS, detail=False)
    def notification_settings(self, request):
        return Response(data=self.get_serializer(self.get_queryset(), many=True).data)

    @notification_mark_as_schema
    @action(methods=[_POST], url_name='mark-as', url_path='mark-as', detail=False)
    def mark_as(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            NotificationService.mark_as(
                serializer.validated_data.get('unread', True),
                self.request.user,
                serializer.validated_data.get('notifications'),
            ),
        )

    @enable_notifications_schema
    @action(methods=[_POST], url_name='enable', url_path='enable', detail=False)
    def enable_notifications(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        codes = serializer.validated_data.get(_SETTINGS, [])
        NotificationService.enable_notifications(request.user, codes)
        message = ', '.join([code.verbose_name for code in codes])
        return Response(f'Enabled notifications for {message}')

    @disable_notifications_schema
    @action(methods=[_POST], url_name='disable', url_path='disable', detail=False)
    def disable_notifications(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        codes = serializer.validated_data.get(_SETTINGS, [])
        NotificationService.disable_notifications(request.user, codes)
        message = ', '.join([code.verbose_name for code in codes])
        return Response(f'Disabled notifications for {message}')
