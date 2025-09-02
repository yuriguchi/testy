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
from tests.commons import model_to_dict_via_serializer
from testy.core.api.v2.serializers import SystemMessageSerializer


@pytest.mark.django_db(reset_sequences=True)
class TestSystemMessagesEndpoints:
    view_name_list = 'api:v2:system-messages'

    def test_list(self, api_client, system_message_factory):
        expected_instances = []
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            if idx % 2:
                system_message_factory(is_active=False)
            else:
                expected_instances.append(
                    model_to_dict_via_serializer(
                        system_message_factory(is_active=True),
                        SystemMessageSerializer,
                    ),
                )

        expected_instances.sort(key=lambda obj: obj['updated_at'], reverse=True)
        response = api_client.send_request(
            self.view_name_list,
            expected_status=HTTPStatus.OK,
        )
        assert response.json() == expected_instances
