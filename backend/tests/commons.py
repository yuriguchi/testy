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
from enum import Enum
from http import HTTPStatus
from typing import Any, Iterable, TypeAlias

import allure
from django.db.models import Model
from django.test.client import RequestFactory
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from testy.users.models import User

_JSON_SERIALIZABLE: TypeAlias = dict[str, Any]


class RequestType(Enum):
    POST = 'post'
    GET = 'get'
    PUT = 'put'
    PATCH = 'patch'
    DELETE = 'delete'


class RequestMock(RequestFactory):
    GET = {}

    @classmethod
    def build_absolute_uri(cls, url):
        return f'http://testserver{url}'


def json_strip(self, as_json: bool = False, is_paginated: bool = True):
    response_body = self.json()
    response_body = response_body['results'] if is_paginated else response_body
    if as_json:
        return JSONRenderer().render(response_body)
    return response_body


class CustomAPIClient(APIClient):
    def send_request(
        self,
        view_name: str,
        data: _JSON_SERIALIZABLE | None = None,
        expected_status: HTTPStatus = HTTPStatus.OK,
        request_type: RequestType = RequestType.GET,
        reverse_kwargs: dict[str, Any] | None = None,
        format='json',  # noqa: WPS125
        query_params: dict[str, Any] | None = None,
        additional_error_msg: str | None = None,
        headers: dict[str, Any] | None = None,
        validate_status: bool = True,
    ) -> Response:
        url = reverse(view_name, kwargs=reverse_kwargs)
        if query_params:
            url = f'{url}?{"&".join([f"{field}={field_value}" for field, field_value in query_params.items()])}'
        with allure.step(f'Send {request_type.value} to {url}'):
            http_request = getattr(self, request_type.value, None)
            if not http_request:
                raise TypeError('Request type is not known')
            if headers:
                response = http_request(url, data=data, format=format, **headers)
            else:
                response = http_request(url, data=data, format=format)
        additional_info = f'\nAdditional info: {additional_error_msg}' if additional_error_msg else ''
        err_msg = f'Expected response code "{expected_status}", actual: "{response.status_code}"' \
                  f'Response content: {getattr(response, "content", "No content")}{additional_info}'
        if validate_status:
            with allure.step(f'Validate status code is {expected_status}'):
                assert response.status_code == expected_status, err_msg
        response.json_strip = json_strip.__get__(response)  # noqa: WPS609
        return response


def model_to_dict_via_serializer(
    instances: Iterable[Model] | Model,
    serializer_class,
    many=False,
    nested_fields: list[str] = None,
    nested_fields_simple_list: list[str] = None,
    fields_to_add: dict[str, Any] = None,
    requested_user: User | None = None,
    as_json: bool = False,
    refresh_instances: bool = False,
) -> list[_JSON_SERIALIZABLE] | _JSON_SERIALIZABLE:
    if not nested_fields:
        nested_fields = []
    if not nested_fields_simple_list:
        nested_fields_simple_list = []
    request = RequestMock()
    setattr(request, 'user', requested_user)
    if refresh_instances:
        if isinstance(instances, Iterable):
            for instance in instances:
                instance.refresh_from_db()
        else:
            instances.refresh_from_db()
    serializer = serializer_class(instances, many=many, context={'request': request})
    if as_json:
        return JSONRenderer().render(serializer.data)
    result_dicts = [dict(elem) for elem in serializer.data] if many else [serializer.data]

    if fields_to_add:
        for name, value in fields_to_add.items():
            for result_dict in result_dicts:
                result_dict[name] = value

    for result_dict in result_dicts:
        for field_name in nested_fields_simple_list:
            result_dict[field_name] = list(result_dict[field_name])
        for field_name in nested_fields:
            result_dict[field_name] = [dict(elem) for elem in result_dict[field_name]]
    return result_dicts if many else result_dicts[0]
