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

from typing import Any

from django.db import transaction

from testy.core.models import Project
from testy.core.services.media import MediaService
from testy.users.models import User
from testy.users.selectors.roles import RoleSelector
from testy.users.services.roles import RoleService


class ProjectService(MediaService):
    non_side_effect_fields = ['name', 'description', 'is_archive', 'icon', 'is_private']

    @transaction.atomic
    def project_create(self, data: dict[str, Any], user: User) -> Project:
        project = Project.model_create(
            fields=self.non_side_effect_fields + ['settings'],
            data=data,
            commit=False,
        )
        self.populate_image_thumbnails(project.icon)
        project.save()
        if not user.is_superuser:
            role = RoleSelector.admin_user_role()
            RoleService.roles_assign(payload={'project': project, 'user': user, 'roles': [role]})
        return project

    def project_update(self, project: Project, data: dict[str, Any]) -> Project:
        old_icon = project.icon
        project, _ = project.model_update(
            fields=self.non_side_effect_fields,
            data=data,
            commit=False,
        )
        if settings := data.get('settings'):
            self.update_settings(project, settings)
        if 'icon' in data:
            self.populate_image_thumbnails(project.icon, old_icon)
        project.save()
        return project

    def update_settings(self, project, data) -> None:
        for field, value in data.items():
            project.settings[field] = value
