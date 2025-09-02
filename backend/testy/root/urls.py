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
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from testy.core.views import AttachmentView
from testy.plugins.url import plugin_urls
from testy.root.auth.views import LoginView, LogoutView, TTLTokenViewSet
from testy.root.views import sql_log_query
from testy.swagger.custom_schema_generation import SchemaGenerator
from testy.users.views import AvatarView

schema_view = get_schema_view(
    openapi.Info(
        title='testy API',
        default_version='v2',
        description='testy API',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    generator_class=SchemaGenerator,
)

ttl_token_list_view = TTLTokenViewSet.as_view({'get': 'list', 'post': 'create'})
ttl_token_detail_view = TTLTokenViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

urlpatterns = [
    # API
    path('api/', include('testy.root.api.urls', namespace='api')),
    path('api/token/obtain/', ttl_token_list_view, name='ttltoken-list'),
    path('api/token/obtain/<str:key>/', ttl_token_detail_view, name='ttltoken-detail'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Authorization
    path('auth/login/', LoginView.as_view(), name='user-login'),
    path('auth/logout/', LogoutView.as_view(), name='user-logout'),

    # Admin
    path('admin/', admin.site.urls),

    # Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(
        r'^api/(?P<version>v1|v2)/swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='swagger-ui',
    ),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Plugins
    # # !!!! REVERSE FOR PLUGINS IS plugins:<your_app_label>:<your view name>
    path('plugins/', include((plugin_urls, 'plugins'), namespace='plugins')),

    # Media
    path('attachments/<int:pk>/', AttachmentView.as_view(), name='attachment-path'),
    path('avatars/<int:pk>/', AvatarView.as_view(), name='avatar-path'),

    # Celery progress
    re_path('^celery-progress/', include('celery_progress.urls')),

    # Sentry Debug
    # SQL Debug
    path('debug/sql-long-query/', sql_log_query),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
