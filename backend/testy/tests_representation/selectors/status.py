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
from django.db.models import Case, IntegerField, Q, QuerySet, When

from testy.core.models import Project
from testy.tests_representation.choices import ResultStatusType
from testy.tests_representation.models import ResultStatus


class ResultStatusSelector:

    @classmethod
    def status_list_raw(cls) -> QuerySet[ResultStatus]:
        return ResultStatus.objects.all()

    @classmethod
    def extended_status_list_by_ids(cls, statuses_ids: list[int]) -> QuerySet[ResultStatus]:
        return QuerySet(ResultStatus).filter(pk__in=statuses_ids)

    @classmethod
    def sort_status_queryset(cls, queryset: QuerySet, project: Project) -> QuerySet[ResultStatus]:
        conditions_list = []
        for status_pk, status_position in project.settings.get('status_order', {}).items():
            conditions_list.append(When(pk=int(status_pk), then=int(status_position)))
        case = Case(*conditions_list, output_field=IntegerField())
        return queryset.annotate(ordering=case).order_by('ordering')

    @classmethod
    def status_list(cls, project: Project, ordering: bool = False) -> QuerySet[ResultStatus]:
        queryset = (
            ResultStatusSelector
            .status_list_raw()
            .filter(
                Q(type=ResultStatusType.SYSTEM) | Q(project=project),
            )
        )
        if ordering:
            queryset = cls.sort_status_queryset(queryset, project)
        return queryset

    @classmethod
    def status_list_by_project_and_name(cls, project: Project | None, name: str) -> QuerySet[ResultStatus]:
        return ResultStatusSelector.status_list(project=project).filter(name__iexact=name)

    @classmethod
    def status_deleted_list(cls) -> QuerySet[ResultStatus]:
        return ResultStatus.deleted_objects.all()

    @classmethod
    def status_by_project_exists(cls, status_id: int, project_id: int) -> bool:
        return ResultStatus.objects.filter(
            Q(project_id=project_id) | Q(project_id__isnull=True),
            id=status_id,
        ).exists()
