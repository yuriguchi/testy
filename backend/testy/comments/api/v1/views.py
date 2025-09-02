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
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from testy.comments.api.v1.serializers import CommentSerializer, InputCommentSerializer
from testy.comments.exceptions import ContentTypeDoesntExist, WrongObjectId
from testy.comments.models import Comment
from testy.comments.paginations import CommentSetPagination
from testy.comments.selectors.comments import CommentSelector
from testy.comments.services.comment import CommentService
from testy.swagger.v1.comments import comment_create_schema, comment_list_schema


@comment_list_schema
class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.none()
    serializer_class = CommentSerializer
    pagination_class = CommentSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    permission_classes = [IsAuthenticated]
    schema_tags = ['Comments']

    ordering = ('-created_at',)

    def get_serializer_class(self):
        if self.action in {'create', 'update'}:
            return InputCommentSerializer
        return super().get_serializer_class()

    def get_object_with_content_type(self):
        request_data = self.request.query_params if self.action == 'list' else self.request.data
        model_name = request_data.get('model')
        try:
            model_id = int(request_data.get('object_id'))
        except (ValueError, TypeError):
            raise WrongObjectId()
        try:
            ct_object = ContentType.objects.get(model=model_name)
        except ObjectDoesNotExist:
            raise ContentTypeDoesntExist()

        model_class = ct_object.model_class()
        obj = get_object_or_404(model_class, id=model_id)
        return obj, ct_object

    def get_queryset(self):
        if self.action not in {'list', 'create'}:
            return Comment.objects.filter(user=self.request.user)
        if comment_id := self.request.query_params.get('comment_id'):
            return CommentSelector.get_same_comments(comment_id)
        obj, ct_object = self.get_object_with_content_type()
        return Comment.objects.filter(content_type=ct_object, object_id=obj.id)

    @comment_create_schema
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj, ct_object = self.get_object_with_content_type()
        data = {
            'content_type': ct_object,
            'object_id': obj.id,
            **serializer.validated_data,
        }
        comment = CommentService().comment_create(
            data=data,
            user=request.user,
        )
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_update(self, serializer):
        serializer.instance = CommentService().comment_update(
            serializer.instance, serializer.validated_data,
        )
