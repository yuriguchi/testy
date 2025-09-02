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

from django.conf import settings
from django.contrib.auth import login, logout
from rest_framework import parsers, renderers
from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from testy.root.auth.models import TTLToken
from testy.root.auth.serializers import (
    RememberMeAuthTokenSerializer,
    TTLAuthTokenInputSerializer,
    TTLTokenOutputSerializer,
)
from testy.root.selectors import TTLTokenSelector

_REQUEST = 'request'


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        """
        Skip csrf validation for some views.

        Args:
            request: django request.
        """


class TTLTokenViewSet(ModelViewSet):
    serializer_class = TTLTokenOutputSerializer
    queryset = TTLToken.objects.none()
    lookup_field = 'key'
    permission_classes = []
    schema_tags = ['Token']

    def get_queryset(self):
        return TTLTokenSelector.token_list_by_user_id(self.request.user.pk)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = TTLToken.objects.create(user=user, description=serializer.validated_data.get('description'))
        return Response(TTLTokenOutputSerializer(token, context={_REQUEST: request}).data)

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise AuthenticationFailed('Authentication required')
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            raise AuthenticationFailed('Only author can view this')
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        description = request.data.get('description')
        serializer_class = self.get_serializer_class()
        if instance.user != request.user:
            raise AuthenticationFailed('Only author can edit token description')
        if not description:
            return Response(serializer_class(instance, context={_REQUEST: request}).data)
        serializer = serializer_class(
            instance,
            data={'description': description},
            partial=True,
            context={_REQUEST: request},
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return TTLAuthTokenInputSerializer
        return TTLTokenOutputSerializer


class LoginView(APIView):
    throttle_classes = ()
    permission_classes = ()
    authentication_classes = (CsrfExemptSessionAuthentication,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = RememberMeAuthTokenSerializer

    def get_serializer_context(self):
        return {
            _REQUEST: self.request,
            'format': self.format_kwarg,
            'view': self,
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        remember_me = serializer.validated_data['remember_me']
        if remember_me:
            request.session.set_expiry(settings.SESSION_COOKIE_AGE_REMEMBER_ME)
        user = serializer.validated_data['user']
        login(request, user)
        return Response({'details': 'logged in successfully'})


class LogoutView(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def get_serializer_context(self):
        return {
            _REQUEST: self.request,
            'format': self.format_kwarg,
            'view': self,
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'details': 'logged out successfully'})
