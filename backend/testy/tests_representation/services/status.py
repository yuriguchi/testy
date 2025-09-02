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
from testy.tests_representation.choices import ResultStatusType
from testy.tests_representation.models import ResultStatus


class ResultStatusService:
    non_side_effects_fields = ['name', 'color', 'project', 'type']

    def status_create(self, data: dict[str, Any]) -> ResultStatus:
        name = data.get('name')
        project = data.get('project')
        type_value = data.get('type', ResultStatusType.CUSTOM)
        if status := ResultStatus.deleted_objects.filter(name__iexact=name, type=type_value, project=project).first():
            status.is_deleted = False
            status.color = data.get('color', status.color)
            status.save()
            return status
        return ResultStatus.model_create(fields=self.non_side_effects_fields, data=data)

    def status_update(self, status: ResultStatus, data: dict[str, Any]) -> ResultStatus:
        status, _ = status.model_update(fields=self.non_side_effects_fields, data=data)
        return status

    @classmethod
    @transaction.atomic
    def delete_status(cls, status: ResultStatus) -> None:
        projects_to_update = []
        projects = Project.objects.filter(settings__default_status=status.pk)
        for project in projects:
            project.settings['default_status'] = None
            projects_to_update.append(project)
        Project.objects.bulk_update(projects_to_update, ['settings'])
        status.delete()
