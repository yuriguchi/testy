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
import mimetypes
from typing import TypeAlias

from django.conf import settings
from django.db.models.fields.files import FieldFile
from django.http import FileResponse, HttpResponse
from rest_framework import status
from rest_framework.request import Request

from testy.utilities.string import strip_suffixes

suffix_properties: TypeAlias = tuple[str, str, str] | tuple[str, int, int]


class MediaViewMixin:

    @classmethod
    def format_response(
        cls,
        file: FieldFile,
        request: Request,
        filename: str | None = None,
    ) -> HttpResponse | FileResponse:
        filename = filename or file.name
        try:
            if settings.TESTY_ALLOW_FILE_RESPONSE:
                return cls.file_response(file, request, filename)
            return cls.redirect_response(file, request, filename)
        except IOError:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    @classmethod
    def redirect_response(cls, file: FieldFile, request: Request, filename: str | None) -> HttpResponse:
        content_type = cls._get_content_type(filename)
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = cls._get_content_disposition(filename, content_type)
        response['X-Accel-Redirect'] = cls._populate_resolution(file.url, request)
        return response

    @classmethod
    def file_response(cls, file: FieldFile, request: Request, filename: str | None) -> FileResponse:
        content_type = cls._get_content_type(filename)
        is_attachment = 'image/' not in content_type
        path = cls._populate_resolution(file.path, request)
        # https://docs.djangoproject.com/en/5.0/ref/request-response/#fileresponse-objects
        return FileResponse(open(path, 'rb'), as_attachment=is_attachment, content_type=content_type)  # noqa: WPS515

    @classmethod
    def _get_content_type(cls, filename: str) -> str:
        content_type, _ = mimetypes.guess_type(filename, strict=False)
        return content_type or 'text/plain'

    @classmethod
    def _get_content_disposition(cls, filename: str, content_type: str) -> str:
        is_attachment = 'image/' not in content_type
        content_disposition = 'attachment' if is_attachment else 'inline'
        return f'{content_disposition}; filename={filename}'

    @classmethod
    def _get_resolution(cls, request: Request) -> str:
        """
        Get file suffix and image parameters based on size from request parameters.

        Args:
            request: user request

        Returns:
            Suffix to add at the end of src file name to find or create file and size parameters.
        """
        if width := request.query_params.get('width', ''):
            width = int(width)
        if height := request.query_params.get('height', ''):
            height = int(height)
        modification_params = (width, height)
        if not any(modification_params):
            return ''
        return f'@{width}x{height}'

    @classmethod
    def _populate_resolution(cls, filepath: str, request: Request) -> str:
        path, suffix = strip_suffixes(filepath)
        resolution_suffix = cls._get_resolution(request)
        return f'{path}{resolution_suffix}{suffix}'


class CallableChoicesMixin:
    """Mixin for providing all values from choices as callable for default values in migrations."""

    @classmethod
    def cb_values(cls):
        return cls.values
