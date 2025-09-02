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
from django.utils import timezone

from tests import constants
from tests.commons import RequestType
from testy.root.auth.models import TTLToken


@pytest.mark.django_db
class TestTokens:
    def test_ttl(self, api_client, user):
        self.get_token(api_client, user.username, constants.PASSWORD)
        token = TTLToken.objects.get(user=user)
        token.expiration_date = timezone.make_aware(timezone.datetime(2009, 1, 1), timezone.utc)
        token.save()
        api_client.send_request(
            'api:v1:test-list',
            expected_status=HTTPStatus.UNAUTHORIZED,
            request_type=RequestType.GET,
            headers={'HTTP_AUTHORIZATION': f'Token {token}'},
        )

    def test_new_token_generated(self, api_client, user):
        obtain_count = 5
        obtained_tokens = []
        for _ in range(obtain_count):
            obtained_tokens.append(
                self.get_token(api_client, user.username, constants.PASSWORD),
            )
        assert obtain_count == len(set(obtained_tokens)), 'Duplicate tokens were obtained'

    def test_different_users_tokens(self, api_client, user, user_factory):
        user2 = user_factory()
        tokens_user1 = [self.get_token(api_client, user.username, constants.PASSWORD) for _ in range(3)]
        tokens_user2 = [self.get_token(api_client, user2.username, constants.PASSWORD) for _ in range(3)]
        token_list1 = api_client.send_request(
            'ttltoken-list',
            data={'username': user.username, 'password': constants.PASSWORD},
            expected_status=HTTPStatus.OK,
            request_type=RequestType.POST,
        )
        token_list2 = api_client.send_request(
            'ttltoken-list',
            data={'username': user2.username, 'password': constants.PASSWORD},
            expected_status=HTTPStatus.OK,
            request_type=RequestType.POST,
        )
        assert token_list1.json() != token_list2.json()
        assert tokens_user1 != tokens_user2

    def test_unauthorized_token_access(self, api_client, user):
        api_client.send_request(
            'ttltoken-list',
            data={'username': user.username, 'password': constants.PASSWORD},
            expected_status=HTTPStatus.UNAUTHORIZED,
            request_type=RequestType.GET,
            additional_error_msg='Unauthorized user can see tokens list',
        )

    def test_detailed_token_view_access(self, api_client, user, user_factory):
        user2 = user_factory()
        tokens_user1 = [self.get_token(api_client, user.username, constants.PASSWORD) for _ in range(3)]
        api_client.send_request(
            'ttltoken-detail',
            reverse_kwargs={'key': tokens_user1[0]},
            expected_status=HTTPStatus.OK,
            request_type=RequestType.GET,
            headers={'HTTP_AUTHORIZATION': f'Token {tokens_user1[0]}'},
            additional_error_msg='Could not access token info with valid user/token',
        )
        api_client.force_login(user2)
        api_client.send_request(
            'ttltoken-detail',
            reverse_kwargs={'key': tokens_user1[0]},
            expected_status=HTTPStatus.NOT_FOUND,
            request_type=RequestType.GET,
            additional_error_msg='User could get private token info',
        )

    @classmethod
    def get_token(cls, api_client, username, password):
        response = api_client.send_request(
            'ttltoken-list',
            data={'username': username, 'password': password},
            expected_status=HTTPStatus.OK,
            request_type=RequestType.POST,
        )
        return response.json()['token']
