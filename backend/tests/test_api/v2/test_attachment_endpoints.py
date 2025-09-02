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
import io
import os.path
from http import HTTPStatus
from pathlib import Path

import pytest
from django.conf import settings
from PIL import Image

from tests.commons import RequestType
from testy.core.models import Attachment
from testy.core.services.attachments import AttachmentService


@pytest.mark.django_db
class TestAttachmentEndpoints:
    list_view_name = 'api:v2:attachment-list'
    detail_view_name = 'api:v2:attachment-detail'
    attachment_file_response_view_name = 'attachment-path'
    attachments_folder = 'attachments'

    @pytest.mark.parametrize(
        'extension, as_attachment',
        [
            ('.txt', True),
            ('.png', False),
            ('.jpeg', False),
            ('.jpg', False),
            ('.pdf', True),
            ('.zip', True),
        ],
        ids=['txt', 'png', 'jpeg', 'corrupted jpg', 'pdf', 'zip'],
    )
    def test_attachment_correct_output(self, api_client, authorized_superuser, create_file, project, as_attachment):
        attachment_json = {
            'project': project.id,
            'file': create_file,
        }
        attachment_id = api_client.send_request(
            self.list_view_name,
            data=attachment_json,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
            format='multipart',
        ).json()[0]['id']
        response = api_client.send_request(
            self.attachment_file_response_view_name,
            reverse_kwargs={'pk': attachment_id},
        )
        assert response.headers['Content-Disposition'].split(';')[0] == 'attachment' if as_attachment else 'inline', \
            'File was returned in wrong Content-Disposition'

    @pytest.mark.parametrize('extension', ['.txt'])
    @pytest.mark.django_db(transaction=True)
    def test_file_deleted_after_attachment_deleted(self, api_client, authorized_superuser, create_file, project):
        attachment_json = {
            'project': project.id,
            'file': create_file,
        }

        attachment_id = api_client.send_request(
            self.list_view_name,
            data=attachment_json,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
            format='multipart',
        ).json()[0]['id']
        attachment = Attachment.objects.get(pk=attachment_id)
        assert os.path.isfile(attachment.file.path)
        attachment.hard_delete()
        assert not os.path.isfile(attachment.file.path)

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_attachment_creates_non_existing_thumbnails(
        self, api_client, authorized_superuser, create_file, project,
        media_directory,
    ):
        attachment_json = {
            'project': project.id,
            'file': create_file,
        }
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1  # plus 1 for src file
        attachment_id = api_client.send_request(
            self.list_view_name,
            data=attachment_json,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
            format='multipart',
        ).json()[0]['id']
        files_folder = Path(Attachment.objects.get(pk=attachment_id).file.url).parts[3]
        number_of_objects_in_dir = len(os.listdir(Path(media_directory, self.attachments_folder, files_folder)))
        assert number_of_objects_to_create == number_of_objects_in_dir
        for resolution in settings.TESTY_THUMBNAIL_RESOLUTIONS:
            content = api_client.send_request(
                self.attachment_file_response_view_name,
                reverse_kwargs={'pk': attachment_id},
                query_params={'width': resolution[0], 'height': resolution[1]},
            ).streaming_content
            img = Image.open(io.BytesIO(b''.join(content)))
            assert resolution[0] == img.width, 'width did not match'
            assert resolution[1] == img.height, 'height did not match'
            assert number_of_objects_to_create == number_of_objects_in_dir, 'Already existing file was created again.'

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_attachment_creates_thumbnails(
        self, api_client, authorized_superuser, create_file, project,
        media_directory,
    ):
        attachment_json = {
            'project': project.id,
            'file': create_file,
        }
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1  # plus 1 for src file
        attachment_id = api_client.send_request(
            self.list_view_name,
            data=attachment_json,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
            format='multipart',
        ).json()[0]['id']
        files_folder = Path(Attachment.objects.get(pk=attachment_id).file.url).parts[3]
        attachment_file_path = Path(media_directory, self.attachments_folder, files_folder)
        assert number_of_objects_to_create == len(os.listdir(attachment_file_path))
        test_mod_parameters = [
            (16, 16),
            (32, 32),
            (512, 512),
        ]
        for width, height in test_mod_parameters:
            query_params = {}
            if width:
                query_params['width'] = width
            if height:
                query_params['height'] = height
            content = api_client.send_request(
                self.attachment_file_response_view_name,
                reverse_kwargs={'pk': attachment_id},
                query_params=query_params,
            ).streaming_content
            img = Image.open(io.BytesIO(b''.join(content)))
            # image is scaled saving aspect ratio
            assert width if width else height == img.width, 'width did not match'
            assert height if height else width == img.height, 'height did not match'
            assert number_of_objects_to_create == len(os.listdir(attachment_file_path)), \
                'Already existing file was created again.'

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_attachments_behaviour_on_file_system_file_delete(
        self, api_client, authorized_superuser, create_file,
        project, media_directory,
    ):
        attachment_json = {
            'project': project.id,
            'file': create_file,
        }
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1  # plus 1 for src file
        attachment_id = api_client.send_request(
            self.list_view_name,
            data=attachment_json,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
            format='multipart',
        ).json()[0]['id']
        attachment = Attachment.objects.get(pk=attachment_id)
        files_folder = Path(attachment.file.url).parts[3]
        attachment_file_path = Path(media_directory, self.attachments_folder, files_folder)
        assert number_of_objects_to_create == len(os.listdir(attachment_file_path))
        os.remove(attachment.file.path)
        number_of_objects_to_create -= 1
        api_client.send_request(
            self.attachment_file_response_view_name,
            reverse_kwargs={'pk': attachment_id},
            expected_status=HTTPStatus.NOT_FOUND,
        )
        api_client.send_request(
            self.attachment_file_response_view_name,
            reverse_kwargs={'pk': attachment_id},
            query_params={'width': 32, 'height': 32},
            expected_status=HTTPStatus.NOT_FOUND,
        )
        assert number_of_objects_to_create == len(os.listdir(attachment_file_path))

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_files_deleted(
        self, api_client, authorized_superuser, create_file,
        project, media_directory, test_case,
    ):
        attachment_json = {
            'project': project.id,
            'file': create_file,
        }
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1  # plus 1 for src file
        attachment_id = api_client.send_request(
            self.list_view_name,
            data=attachment_json,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
            format='multipart',
        ).json()[0]['id']
        attachment = Attachment.objects.get(pk=attachment_id)
        files_folder = Path(attachment.file.url).parts[3]
        attachment_file_path = Path(media_directory, self.attachments_folder, files_folder)
        assert number_of_objects_to_create == len(os.listdir(attachment_file_path))
        AttachmentService().attachment_set_content_object(attachment, test_case)
        assert number_of_objects_to_create == len(os.listdir(attachment_file_path))
        with open(attachment_file_path / 'asdasdasasd.txt', 'x') as file:
            file.write('Cats data again!')
        with open(attachment_file_path / 'asdasdasasd.png', 'x') as file:
            file.write('Cats data again!')
        api_client.send_request(
            self.detail_view_name,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': attachment_id},
            expected_status=HTTPStatus.NO_CONTENT,
        )
        Attachment.deleted_objects.all().hard_delete()
        assert len(os.listdir(attachment_file_path)) == 2, 'All related files must be deleted, other should exist.'

    @pytest.mark.parametrize('extension', ['.txt'])
    @pytest.mark.django_db(transaction=True)
    def test_cascade_soft_delete(
        self, api_client, authorized_superuser, create_file, project,
        attachment_test_case_factory, test_result_factory, test_case_factory, test_factory,
    ):
        case = test_case_factory(project=project)
        test = test_factory(case=case, project=project)
        result = test_result_factory(test=test, project=project)
        attachment_test_case_factory(project=project, content_object=case)
        attachment_test_case_factory(project=project, content_object=result)
        api_client.send_request(
            'api:v2:testcase-detail',
            reverse_kwargs={'pk': case.id},
            request_type=RequestType.DELETE,
            expected_status=HTTPStatus.NO_CONTENT,
        )
        assert not Attachment.objects.count()


@pytest.mark.django_db
class TestAttachmentFilter:
    list_view_name = 'api:v2:attachment-list'

    def test_project_filter(self, attachment_factory, project_factory, authorized_client, test_case):
        project_to_discover = project_factory()
        attachment_factory(project=project_to_discover, content_object=test_case)
        attachment_factory(project=project_factory(), content_object=test_case)
        resp_body = authorized_client.send_request(
            self.list_view_name,
            query_params={'project': project_to_discover.id},
        ).json_strip(is_paginated=False)
        assert len(resp_body) == 1
