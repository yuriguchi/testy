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

import datetime
import io
import os
from copy import deepcopy
from http import HTTPStatus
from pathlib import Path
from typing import Any

import allure
import pytest
from aiohttp import BasicAuth
from django.conf import settings
from django.utils import timezone
from PIL import Image
from rest_framework.reverse import reverse
from rest_framework.test import RequestsClient

from tests import constants
from tests.commons import RequestType, model_to_dict_via_serializer
from tests.error_messages import (
    CASE_INSENSITIVE_USERNAME_ALREADY_EXISTS,
    DIGIT_PASS,
    INVALID_EMAIL_MSG,
    LOWERCASE_PASS,
    SHORT_PASS,
    SPECIAL_SYMB_PASS,
    UNAUTHORIZED_MSG,
    UPPERCASE_PASS,
    USERNAME_ALREADY_EXISTS,
)
from testy.users.api.v2.serializers import UserSerializer
from testy.users.models import Membership, User


@pytest.mark.django_db
class TestUserEndpoints:
    view_name_list = 'api:v2:user-list'
    view_name_detail = 'api:v2:user-detail'
    view_name_me = 'api:v2:user-me'
    view_name_config = 'api:v2:user-config'
    view_name_password_update = 'api:v2:user-change-password'
    view_name_login = 'user-login'
    view_name_logout = 'user-logout'

    def test_list(self, api_client, authorized_superuser, user_factory):
        number_of_pages = 2
        number_of_objects = constants.NUMBER_OF_OBJECTS_TO_CREATE_PAGE * number_of_pages
        users = [authorized_superuser] + [user_factory() for _ in range(number_of_objects - 1)]  # -1 for superuser

        expected_instances = model_to_dict_via_serializer(users, UserSerializer, many=True)

        response_instances = []
        for page_number in range(1, number_of_pages + 1):
            response = api_client.send_request(
                self.view_name_list,
                query_params={'page': page_number},
            )
            results = response.json()['results']
            assert len(results) == constants.NUMBER_OF_OBJECTS_TO_CREATE_PAGE
            response_instances += results

        expected_instances.sort(key=lambda u: u['id'])
        response_instances.sort(key=lambda u: u['id'])

        assert expected_instances == response_instances

    def test_retrieve(self, api_client, authorized_superuser, user):
        expected_dict = model_to_dict_via_serializer(user, UserSerializer)
        response = api_client.send_request(self.view_name_detail, reverse_kwargs={'pk': user.pk})
        actual_dict = response.json()
        assert actual_dict == expected_dict, 'Actual model dict is different from expected'

    def test_password_update(self, api_client, user):
        api_client.force_login(user)
        api_client.send_request(
            self.view_name_password_update,
            data={'password': constants.NEW_PASSWORD},
            request_type=RequestType.POST,
        )
        with allure.step('Validate user not logged out after password change'):
            api_client.send_request(self.view_name_me)
        with allure.step('Validate user can login with new credentials'):
            api_client.send_request(
                self.view_name_login,
                request_type=RequestType.POST,
                data={
                    'username': user.username,
                    'password': constants.NEW_PASSWORD,
                    'remember_me': True,
                },
            )

    @pytest.mark.parametrize(
        'password, err_msg',
        [
            ('Test_1', SHORT_PASS),
            ('testsome_1', UPPERCASE_PASS),
            ('TESTSOME_1', LOWERCASE_PASS),
            ('TestSome_', DIGIT_PASS),
            ('TestSome22', SPECIAL_SYMB_PASS),
        ],
        ids=[
            'Minimal length',
            'Upper case required',
            'Lower case required',
            'Digit required',
            'Special symbol required',
        ],
    )
    def test_password_constraints(self, authorized_client, password, err_msg):
        resp = authorized_client.send_request(
            self.view_name_password_update,
            request_type=RequestType.POST,
            data={
                'password': password,
            },
            expected_status=HTTPStatus.BAD_REQUEST,
        ).json()
        assert resp['password'][0] == err_msg

    def test_me(self, api_client, authorized_superuser):
        expected_dict = model_to_dict_via_serializer(authorized_superuser, UserSerializer)
        response = api_client.send_request(self.view_name_me)
        actual_dict = response.json()
        assert actual_dict == expected_dict, 'Actual model dict is different from expected'

    def test_me_config(self, api_client, authorized_superuser):
        config = {
            'custom_attr_1': 'custom1',
            'custom_attr_2': 'custom2',
            'custom_attr_3': 'custom3',
        }
        content = api_client.send_request(self.view_name_config).json()
        assert not content, 'Something already in config before it is updated'
        content = api_client.send_request(
            self.view_name_config,
            data=config,
            request_type=RequestType.PATCH,
        ).json()
        assert config == content, 'Config was not update or content did not match'
        new_attr = {'latest_custom_attr': 'custom4'}
        content = api_client.send_request(
            self.view_name_config,
            data=new_attr,
            request_type=RequestType.PATCH,
        ).json()
        config.update(new_attr)
        assert config == content, 'Config was not update or content did not match'

    def test_creation(self, api_client, authorized_superuser):
        expected_users_num = 2
        assert User.objects.count() == 1, 'Extra users were found.'
        user_dict = {
            'username': constants.USERNAME,
            'first_name': constants.FIRST_NAME,
            'last_name': constants.LAST_NAME,
            'password': constants.PASSWORD,
            'email': constants.USER_EMAIL,
        }
        api_client.send_request(self.view_name_list, user_dict, HTTPStatus.CREATED, RequestType.POST)
        assert User.objects.count() == expected_users_num, f'Expected number of users "{expected_users_num}"' \
                                                           f'actual: "{User.objects.count()}"'

    @pytest.mark.parametrize(
        'username,new_username,message',
        [
            ('user', 'user', USERNAME_ALREADY_EXISTS),
            ('user', 'UsEr', CASE_INSENSITIVE_USERNAME_ALREADY_EXISTS),
            ('user', 'USER', CASE_INSENSITIVE_USERNAME_ALREADY_EXISTS),
        ],
    )
    def test_duplicate_username_not_allowed(
        self, api_client, authorized_superuser, username, new_username, message,
    ):
        expected_users_num = 2
        assert User.objects.count() == 1, 'Extra users were found.'
        user_dict = {
            'username': username,
            'first_name': constants.FIRST_NAME,
            'last_name': constants.LAST_NAME,
            'password': constants.PASSWORD,
            'email': constants.USER_EMAIL,
        }
        api_client.send_request(self.view_name_list, user_dict, HTTPStatus.CREATED, RequestType.POST)
        user_dict['username'] = new_username
        response = api_client.send_request(
            self.view_name_list, user_dict, HTTPStatus.BAD_REQUEST, RequestType.POST,
        )
        assert response.json() == {
            'username': [message],
        }
        assert User.objects.count() == expected_users_num, f'Expected number of users "{expected_users_num}"' \
                                                           f'actual: "{User.objects.count()}"'

    @pytest.mark.parametrize(
        'field, new_val',
        [
            ('first_name', 'new_name'),
            ('last_name', 'new_last_name'),
            ('email', 'newmail@yadro.com'),
            ('is_active', False),
            ('is_superuser', False),
        ],
    )
    def test_partial_update(self, api_client, authorized_superuser, field, new_val, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        api_client.send_request(
            self.view_name_detail,
            data={field: new_val},
            request_type=RequestType.PATCH,
            reverse_kwargs={'pk': user.pk},
        )
        user.refresh_from_db()
        actual_val = getattr(user, field)
        assert actual_val == new_val, f'Username does not match. Expected "{new_val}", actual: "{actual_val}"'

    def test_update(self, api_client, authorized_superuser, user_factory):
        user = user_factory(is_active=True, is_superuser=True)
        user_dict = {
            'id': user.id,
            'first_name': 'new_name',
            'last_name': 'new_last_name',
            'email': 'newmail@yadro.com',
            'is_superuser': False,
            'is_active': False,
        }
        api_client.send_request(
            self.view_name_detail,
            user_dict,
            request_type=RequestType.PUT,
            expected_status=HTTPStatus.OK,
            reverse_kwargs={'pk': user.pk},
        )
        user.refresh_from_db()
        for field in ('first_name', 'last_name', 'email', 'is_superuser', 'is_active'):
            assert user_dict[field] == getattr(user, field), f'"{field}" does not match expected'

    def test_delete(self, api_client, authorized_superuser, user):
        assert User.objects.count() == 2, 'User was not created'
        api_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.NO_CONTENT,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': user.pk},
        )
        assert User.objects.count() == 1, f'User with id "{user.id}" was not deleted.'

    def test_delete_yourself_is_forbidden(self, api_client, authorized_superuser):
        assert User.objects.count() == 1, 'Extra users were detected'
        response = api_client.send_request(
            self.view_name_detail,
            expected_status=HTTPStatus.BAD_REQUEST,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': authorized_superuser.pk},
        )
        content = response.json()
        assert content == {'errors': ['User cannot delete itself']}, 'Another error was raised'
        assert User.objects.count() == 1, 'User was deleted by himself'

    def test_unauthorized_access(self, api_client):
        for request_type in RequestType:
            response = api_client.send_request(
                self.view_name_list,
                expected_status=HTTPStatus.UNAUTHORIZED,
                request_type=request_type,
            )
            received_dict = response.json()
            assert received_dict['detail'] == UNAUTHORIZED_MSG, 'Expected message was not found in response.' \
                                                                f'Request type: {RequestType.POST.value}'

    def test_email_validation(self, api_client, authorized_superuser, user):
        update_types = [RequestType.PUT, RequestType.PATCH]
        user_dict = {
            'username': constants.USERNAME,
            'password': constants.PASSWORD,
            'email': constants.INVALID_EMAIL,
        }
        response = api_client.send_request(self.view_name_list, user_dict, HTTPStatus.BAD_REQUEST, RequestType.POST)
        received_dict = response.json()
        assert received_dict['email'][0] == INVALID_EMAIL_MSG, 'Validation email error was not found in response.' \
                                                               f'Request type: {RequestType.POST.value}'
        user_dict_update = {
            'username': constants.USERNAME,
            'password': constants.PASSWORD,
            'email': constants.INVALID_EMAIL,
        }
        for request_type in update_types:
            response = api_client.send_request(
                self.view_name_detail,
                data=user_dict_update,
                expected_status=HTTPStatus.BAD_REQUEST,
                request_type=request_type,
                reverse_kwargs={'pk': user.pk},
            )
            received_dict = response.json()
            assert received_dict['email'][0] == INVALID_EMAIL_MSG, 'Validation email error was not found in response.' \
                                                                   f'Request type: {request_type.value}'

    @pytest.mark.django_db(transaction=True)
    def test_cookie_auth(self, user):
        client = RequestsClient()
        response = client.post(
            f'http://testserver{reverse(self.view_name_login)}',
            data={'username': user.username, 'password': constants.PASSWORD},
        )
        csrf = response.cookies['csrftoken']
        sessionid = response.cookies['sessionid']
        assert response.status_code == HTTPStatus.OK
        response = client.get(f'http://testserver{reverse(self.view_name_me)}')
        assert response.status_code == HTTPStatus.OK
        response = client.post(f'http://testserver{reverse(self.view_name_logout)}')
        assert response.status_code == HTTPStatus.FORBIDDEN, 'X-CSRFToken header should be essential.'
        response = client.post(f'http://testserver{reverse(self.view_name_logout)}', headers={'X-CSRFToken': csrf})
        assert response.status_code == HTTPStatus.OK
        response = client.get(f'http://testserver{reverse(self.view_name_me)}')
        assert response.status_code == HTTPStatus.UNAUTHORIZED, 'User could get to me page unauthorized'
        client.cookies['csrftoken'] = csrf
        client.cookies['sessionid'] = sessionid
        response = client.get(f'http://testserver{reverse(self.view_name_me)}')
        assert response.status_code == HTTPStatus.UNAUTHORIZED, 'User could use invalidated sessionid/csrftoken'

    @pytest.mark.django_db(transaction=True)
    def test_cookie_auth_expiration(self, api_client, settings, user, freezer):
        response = api_client.post(
            reverse(self.view_name_login),
            data={
                'username': user.username,
                'password': constants.PASSWORD,
            },
        )
        assert response.status_code == HTTPStatus.OK

        initial_time = timezone.now()

        freezer.move_to(
            initial_time + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE - 1),
        )
        response = api_client.get(reverse(self.view_name_me))
        assert response.status_code == HTTPStatus.OK

        freezer.move_to(
            initial_time + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE + 1),
        )
        response = api_client.get(reverse(self.view_name_me))
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.django_db(transaction=True)
    def test_cookie_auth_expiration_remember_me(self, api_client, settings, user, freezer):
        response = api_client.post(
            reverse(self.view_name_login),
            data={
                'username': user.username,
                'password': constants.PASSWORD,
                'remember_me': True,
            },
        )
        assert response.status_code == HTTPStatus.OK

        initial_time = timezone.now()

        freezer.move_to(
            initial_time + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE_REMEMBER_ME - 1),
        )
        response = api_client.get(reverse(self.view_name_me))
        assert response.status_code == HTTPStatus.OK

        freezer.move_to(
            initial_time + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE_REMEMBER_ME + 1),
        )
        response = api_client.get(reverse(self.view_name_me))
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @classmethod
    def _form_dict_user_model(cls, user: User) -> dict[str, Any]:
        user_dict = model_to_dict_via_serializer(user, User)
        fields_to_remove = ['is_superuser', 'last_login', 'password', 'user_permissions']
        for field in fields_to_remove:
            user_dict.pop(field)
        user_dict['date_joined'] = user_dict['date_joined'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return user_dict


@pytest.mark.django_db
class TestUserAvatars:
    view_name_list = 'api:v2:user-list'
    view_name_detail = 'api:v2:user-detail'
    view_name_avatar = 'api:v2:user-avatar'
    avatars_file_response_view_name = 'avatar-path'
    avatars_folder = 'avatars'

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'])
    @pytest.mark.django_db(transaction=True)
    def test_file_deleted_after_user_deleted(
        self, api_client, authorized_superuser, create_file, project, user,
        media_directory,
    ):
        user_dict = {
            'username': constants.USERNAME,
            'first_name': constants.FIRST_NAME,
            'last_name': constants.LAST_NAME,
            'password': constants.PASSWORD,
            'email': constants.USER_EMAIL,
            'avatar': create_file,
        }
        user_id = api_client.send_request(
            self.view_name_list,
            data=user_dict,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
            format='multipart',
        ).json()['id']
        expected_numbers_of_files = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1
        files_folder = Path(User.objects.get(pk=user_id).avatar.url).parts[3]
        number_of_objects_in_dir = len(os.listdir(Path(media_directory, self.avatars_folder, files_folder)))
        assert expected_numbers_of_files == number_of_objects_in_dir

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_existing_thumbnails_used(
        self, api_client, authorized_superuser, create_file,
        media_directory,
    ):
        user_dict = {
            'avatar': create_file,
        }
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1  # plus 1 for src file
        user_id = User.objects.first().id
        api_client.send_request(
            self.view_name_avatar,
            data=user_dict,
            request_type=RequestType.POST,
            format='multipart',
        )
        files_folder = Path(User.objects.get(pk=user_id).avatar.url).parts[3]
        number_of_objects_in_dir = len(os.listdir(Path(media_directory, self.avatars_folder, files_folder)))
        assert number_of_objects_to_create == number_of_objects_in_dir
        for resolution in settings.TESTY_THUMBNAIL_RESOLUTIONS:
            content = api_client.send_request(
                self.avatars_file_response_view_name,
                reverse_kwargs={'pk': user_id},
                query_params={'width': resolution[0], 'height': resolution[1]},
            ).streaming_content
            img = Image.open(io.BytesIO(b''.join(content)))
            assert resolution[0] == img.width, 'width did not match'
            assert number_of_objects_to_create == number_of_objects_in_dir, 'Already existing file was created again.'

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_avatar_creation_creates_thumbnails(self, api_client, authorized_superuser, create_file, media_directory):
        user_dict = {
            'avatar': create_file,
        }
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1  # plus 1 for src file
        user_id = User.objects.first().id
        api_client.send_request(
            self.view_name_avatar,
            data=user_dict,
            request_type=RequestType.POST,
            format='multipart',
        )
        files_folder = Path(User.objects.get(pk=user_id).avatar.url).parts[3]
        attachment_file_path = Path(media_directory, self.avatars_folder, files_folder)
        assert number_of_objects_to_create == len(os.listdir(attachment_file_path))
        test_mod_parameters = [
            (350, None),
            (None, 350),
            (350, 350),
        ]
        for width, height in test_mod_parameters:
            query_params = {}
            if width:
                query_params['width'] = width
            if height:
                query_params['height'] = height
            api_client.send_request(
                self.avatars_file_response_view_name,
                reverse_kwargs={'pk': user_id},
                query_params=query_params,
                expected_status=HTTPStatus.NOT_FOUND,
            )

    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_attachments_behaviour_on_file_system_file_delete(
        self, api_client, authorized_superuser, create_file,
        media_directory,
    ):
        user_dict = {
            'avatar': create_file,
        }
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1  # plus 1 for src file
        api_client.send_request(
            self.view_name_avatar,
            data=user_dict,
            request_type=RequestType.POST,
            format='multipart',
        )
        user = User.objects.first()
        files_folder = Path(user.avatar.url).parts[3]
        avatar_file_path = Path(media_directory, self.avatars_folder, files_folder)
        assert number_of_objects_to_create == len(os.listdir(avatar_file_path))
        os.remove(user.avatar.path)
        number_of_objects_to_create -= 1
        api_client.send_request(
            self.avatars_file_response_view_name,
            reverse_kwargs={'pk': user.id},
            expected_status=HTTPStatus.NOT_FOUND,
        )
        api_client.send_request(
            self.avatars_file_response_view_name,
            reverse_kwargs={'pk': user.id},
            query_params={'width': 32, 'height': 32},
            expected_status=HTTPStatus.NOT_FOUND,
        )
        assert number_of_objects_to_create == len(os.listdir(avatar_file_path))

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_files_deleted(self, api_client, authorized_superuser, create_file, media_directory):
        user_dict = {
            'username': constants.USERNAME,
            'first_name': constants.FIRST_NAME,
            'last_name': constants.LAST_NAME,
            'password': constants.PASSWORD,
            'email': constants.USER_EMAIL,
            'avatar': create_file,
        }
        user_id = api_client.send_request(
            self.view_name_list,
            data=user_dict,
            request_type=RequestType.POST,
            expected_status=HTTPStatus.CREATED,
            format='multipart',
        ).json()['id']
        user = User.objects.get(pk=user_id)
        files_folder = Path(user.avatar.url).parts[3]
        avatar_file_path = Path(media_directory, self.avatars_folder, files_folder)
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1
        assert number_of_objects_to_create == len(os.listdir(avatar_file_path))
        with open(avatar_file_path / 'asdasdasasd.txt', 'x') as file:
            file.write('Cats data again!')
        with open(avatar_file_path / 'asdasdasasd.png', 'x') as file:
            file.write('Cats data again!')
        api_client.send_request(
            self.view_name_detail,
            request_type=RequestType.DELETE,
            reverse_kwargs={'pk': user.id},
            expected_status=HTTPStatus.NO_CONTENT,
        )
        assert len(os.listdir(avatar_file_path)) == 2, 'All related files must be deleted, other should exist.'

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_avatar_removed_on_update(self, api_client, authorized_superuser, create_file, media_directory):
        file2 = deepcopy(create_file)
        user_dict = {
            'avatar': create_file,
        }

        api_client.send_request(
            self.view_name_avatar,
            data=user_dict,
            request_type=RequestType.POST,
            format='multipart',
        )
        user = User.objects.first()
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1  # plus 1 for src file
        files_folder = Path(user.avatar.url).parts[3]
        avatar_file_path = Path(media_directory, self.avatars_folder, files_folder)
        old_list_of_files = os.listdir(avatar_file_path)
        assert number_of_objects_to_create == len(old_list_of_files)
        user_dict2 = {
            'avatar': file2,
        }
        api_client.send_request(
            self.view_name_avatar,
            data=user_dict2,
            request_type=RequestType.POST,
            format='multipart',
        )
        assert not len(os.listdir(avatar_file_path))

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('extension', ['.png', '.jpeg'], ids=['png', 'jpeg'])
    def test_avatar_deletion(self, api_client, authorized_superuser, create_file, media_directory):
        user_dict = {
            'avatar': create_file,
        }
        api_client.send_request(
            self.view_name_avatar,
            data=user_dict,
            request_type=RequestType.POST,
            format='multipart',
        )
        user = User.objects.first()
        number_of_objects_to_create = len(settings.TESTY_THUMBNAIL_RESOLUTIONS) + 1  # plus 1 for src file
        files_folder = Path(user.avatar.url).parts[3]
        avatar_file_path = Path(media_directory, self.avatars_folder, files_folder)
        old_list_of_files = os.listdir(avatar_file_path)
        assert number_of_objects_to_create == len(old_list_of_files)
        api_client.send_request(
            self.view_name_avatar,
            request_type=RequestType.DELETE,
        )
        for extension in ['.txt', '.png']:
            with open(avatar_file_path / f'asdasdasasd{extension}', 'x') as file:
                file.write('Cats data again!')
        assert len(os.listdir(avatar_file_path)) == 2
        api_client.send_request(
            self.view_name_avatar,
            request_type=RequestType.DELETE,
        )
        assert len(os.listdir(avatar_file_path)) == 2

    @allure.title('Test Basic auth')
    def test_basic_auth(self, superuser, api_client, user):
        auth = BasicAuth(superuser.username, constants.PASSWORD).encode()
        with allure.step('Validate safe request'):
            api_client.send_request(self.view_name_list, headers={'HTTP_AUTHORIZATION': auth})
        with allure.step('Validate unsafe request'):
            api_client.send_request(
                self.view_name_detail,
                data={},
                reverse_kwargs={'pk': user.pk},
                headers={'HTTP_AUTHORIZATION': auth},
                request_type=RequestType.PATCH,
            )


@pytest.mark.django_db
class TestUserFilters:
    view_name_list = 'api:v2:user-list'
    view_name_members = 'api:v2:project-members'

    @pytest.mark.parametrize('view_name', [view_name_list, view_name_members])
    @pytest.mark.parametrize(
        'field,token,expected,remaining',
        (
            ('username', 'token', ['TOKEN', 'test_token', 'token_test'], ['remain']),
            ('email', 'token', ['token@example.com', 'example@token.com'], ['remain@remain.com']),
            ('first_name', 'Token', ['Token', 'Tokenshi', 'Itoken'], ['Remain']),
            ('last_name', 'Token', ['Token', 'Tokenshi', 'Itoken'], ['Remain']),
            ('is_active', False, [False], [True]),
            ('is_superuser', False, [False], [True]),
        ),
    )
    def test_filter(
        self,
        api_client,
        authorized_superuser,
        user_factory,
        field,
        token,
        expected,
        remaining,
        view_name,
        project,
        membership_factory,
        role,
    ):
        allure.dynamic.title(f'Test user filter for {view_name}')
        for value in expected + remaining:
            user = user_factory(**{field: value})
            membership_factory(user=user, project=project, role=role)

        response = api_client.send_request(
            view_name,
            query_params={field: token},
            reverse_kwargs={'pk': project.pk} if view_name == self.view_name_members else None,
        )
        results = response.json()['results']

        assert sorted(r[field] for r in results) == sorted(expected)

    def test_project_filter(self, authorized_superuser_client, project_factory, user_factory, role):
        project_spb = project_factory(name='project spb')
        project_msk = project_factory(name='project msk')
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            if idx % 2 == 0:
                Membership.objects.create(user=user_factory(), project=project_spb, role=role)
            else:
                Membership.objects.create(user=user_factory(), project=project_msk, role=role)
        count_spb_users = authorized_superuser_client.send_request(
            self.view_name_list,
            query_params={'project': project_spb.pk},
        ).json()['count']
        assert constants.NUMBER_OF_OBJECTS_TO_CREATE / 2 == count_spb_users
        count_msk_users = authorized_superuser_client.send_request(
            self.view_name_list,
            query_params={'project': project_spb.pk},
        ).json()['count']
        assert constants.NUMBER_OF_OBJECTS_TO_CREATE / 2 == count_msk_users
        count_all_users = authorized_superuser_client.send_request(
            self.view_name_list,
            query_params={'project': f'{project_spb.pk},{project_msk.pk}'},
        ).json()['count']
        assert constants.NUMBER_OF_OBJECTS_TO_CREATE == count_all_users
