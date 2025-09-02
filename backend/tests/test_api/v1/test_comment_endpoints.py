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
from tests.error_messages import EMPTY_COMMENT
from testy.comments.api.v1.serializers import CommentSerializer
from testy.comments.models import Comment


@pytest.mark.django_db
class TestCommentEndpoints:
    view_name_list = 'api:v1:comment-list'
    view_name_detail = 'api:v1:comment-detail'

    @pytest.mark.parametrize(
        'factory_name, content_type', [
            ('comment_test_factory', 'test'),
            ('comment_test_case_factory', 'testcase'),
            ('comment_test_result_factory', 'testresult'),
            ('comment_test_suite_factory', 'testsuite'),
            ('comment_test_plan_factory', 'testplan'),
        ],
    )
    def test_list(self, api_client, authorized_superuser, factory_name, content_type, request):
        factory = request.getfixturevalue(factory_name)
        instances = [factory() for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
        object_id = instances[0].object_id
        expected_instances = model_to_dict_via_serializer(instances, CommentSerializer, many=True)

        content = api_client.send_request(
            self.view_name_list,
            query_params={
                'model': content_type,
                'object_id': object_id,
            },
        ).json()

        for instance in content['results']:
            assert instance in expected_instances

    @pytest.mark.parametrize(
        'factory_name', [
            'comment_test_factory',
            'comment_test_case_factory',
            'comment_test_result_factory',
            'comment_test_suite_factory',
            'comment_test_plan_factory',
        ],
    )
    def test_retrieve(self, api_client, authorized_superuser, factory_name, request):
        instance = request.getfixturevalue(factory_name)(user=authorized_superuser)
        expected_dict = model_to_dict_via_serializer(instance, CommentSerializer)
        response = api_client.send_request(self.view_name_detail, reverse_kwargs={'pk': instance.pk})
        actual_dict = response.json()
        assert actual_dict == expected_dict, 'Actual model dict is different from expected'

    @pytest.mark.parametrize(
        'is_attachment, content, expected_status', [
            (False, '    ', HTTPStatus.BAD_REQUEST),
            (False, None, HTTPStatus.BAD_REQUEST),
            (True, '', HTTPStatus.CREATED),
            (False, constants.TEST_COMMENT, HTTPStatus.CREATED),
            (True, constants.TEST_COMMENT, HTTPStatus.CREATED),
        ],
    )
    @pytest.mark.parametrize(
        'factory_name, content_type', [
            ('test_factory', 'test'),
            ('test_case_factory', 'testcase'),
            ('test_result_factory', 'testresult'),
            ('test_suite_factory', 'testsuite'),
            ('test_plan_factory', 'testplan'),
        ],
    )
    def test_creation(
        self,
        api_client,
        authorized_superuser,
        factory_name,
        content_type,
        request,
        expected_status,
        is_attachment,
        content,
        attachment_factory,
    ):
        instance = request.getfixturevalue(factory_name)()
        assert Comment.objects.count() == 0, 'Extra comments were found.'
        attachments = []
        if is_attachment:
            attachments += [attachment_factory(content_type=None, object_id=None).id]
        body_dict = {
            'content': content,
            'model': content_type,
            'object_id': instance.pk,
            'attachments': attachments,
        }
        response = api_client.send_request(self.view_name_list, body_dict, expected_status, RequestType.POST)
        if expected_status == HTTPStatus.CREATED:
            assert Comment.objects.count() == 1, f'Expected number of comments 1' \
                                                 f'actual: "{Comment.objects.count()}"'
            attachments_count = Comment.objects.get(pk=response.json()['id']).attachments.count()
            assert bool(attachments_count) == is_attachment
        else:
            assert response.json()['errors'][0] == EMPTY_COMMENT

    @pytest.mark.parametrize(
        'is_attachment, content, expected_status', [
            (False, '    ', HTTPStatus.BAD_REQUEST),
            (False, None, HTTPStatus.BAD_REQUEST),
            (True, '', HTTPStatus.OK),
            (False, constants.TEST_COMMENT, HTTPStatus.OK),
            (True, constants.TEST_COMMENT, HTTPStatus.OK),
        ],
    )
    @pytest.mark.parametrize(
        'factory_name', [
            'comment_test_factory',
            'comment_test_case_factory',
            'comment_test_result_factory',
            'comment_test_suite_factory',
            'comment_test_plan_factory',
        ],
    )
    def test_update(
        self,
        api_client,
        authorized_superuser,
        factory_name,
        request,
        expected_status,
        is_attachment,
        content,
        attachment_factory,
    ):
        instance = request.getfixturevalue(factory_name)(user=authorized_superuser, content='old content')
        attachments = []
        if is_attachment:
            attachments += [attachment_factory(content_type=None, object_id=None).id]
        body_dict = {
            'content': content,
            'attachments': attachments,
        }

        response = api_client.send_request(
            self.view_name_detail,
            body_dict,
            request_type=RequestType.PUT,
            expected_status=expected_status,
            reverse_kwargs={'pk': instance.pk},
        )

        if expected_status == HTTPStatus.OK:
            actual_content = Comment.objects.get(pk=instance.id).content
            assert actual_content == content, \
                f'Content does not match. Expected content "{content}", ' \
                f'actual: "{actual_content}"'
            attachments_count = Comment.objects.get(pk=instance.id).attachments.count()
            assert bool(attachments_count) == is_attachment
        else:
            assert response.json()['errors'][0] == EMPTY_COMMENT

    @pytest.mark.parametrize(
        'factory_name', [
            'comment_test_factory',
            'comment_test_case_factory',
            'comment_test_result_factory',
            'comment_test_suite_factory',
            'comment_test_plan_factory',
        ],
    )
    def test_delete(self, api_client, authorized_superuser, factory_name, request):
        content_after_deletion = 'Comment was deleted'
        instance = request.getfixturevalue(factory_name)(user=authorized_superuser)
        assert Comment.objects.count() == 1, 'Comment was not created'
        api_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': instance.pk},
        )
        assert Comment.objects.count() == 1, 'Comment was hard deleted'
        content = api_client.send_request(self.view_name_detail, reverse_kwargs={'pk': instance.pk}).json()
        assert content['content'] == content_after_deletion, 'Comment was not mark as deleted'

    @pytest.mark.parametrize(
        'factory_name', [
            'comment_test_factory',
            'comment_test_case_factory',
            'comment_test_result_factory',
            'comment_test_suite_factory',
            'comment_test_plan_factory',
        ],
    )
    def test_search_comment(self, api_client, authorized_superuser, factory_name, request):
        factory = request.getfixturevalue(factory_name)
        instances = [factory() for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE)]
        for idx, comment in enumerate(instances, 1):
            actual_comments = api_client.send_request(
                self.view_name_list,
                query_params={
                    'comment_id': comment.id,
                    'ordering': 'created_at',
                    'page_size': 1,
                },
            ).json()['results']
            assert len(actual_comments) == 1, f'Invalid pagination, more than one comment, iteration = {idx}'
            assert actual_comments[0]['id'] == comment.id, (
                f'Invalid pagination, expected '
                f'comment with id = {comment.id},'
                f' get {actual_comments[0]["id"]}'
            )
