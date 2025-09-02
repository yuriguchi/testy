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

from django.db.models import Case, Count, Exists, F, IntegerField, OuterRef, Q, QuerySet, Value, When
from rest_framework.generics import get_object_or_404

from testy.core.exceptions import UserMissingError
from testy.core.models import Project
from testy.tests_description.models import TestCase, TestSuite
from testy.tests_representation.models import Test, TestPlan
from testy.tests_representation.selectors.testplan import TestPlanSelector
from testy.users.choices import UserAllowedPermissionCodenames
from testy.users.models import Membership, User
from testy.users.selectors.roles import RoleSelector
from testy.utilities.request import PeriodDateTime

_PK = 'pk'


class ProjectSelector:

    def __init__(self, user: User | None = None):
        self._user = user

    def project_list(self) -> QuerySet[Project]:
        qs = self._user_project_qs()
        return qs.order_by('name')

    @classmethod
    def project_list_raw(cls) -> QuerySet[Project]:
        return Project.objects.all().order_by('name')

    @classmethod
    def project_deleted_list(cls) -> QuerySet[Project]:
        return Project.deleted_objects.all()

    @classmethod
    def project_by_id(cls, project_id: int) -> Project:
        return get_object_or_404(Project, pk=project_id)

    def project_list_statistics(self):
        membership_exists = Exists(
            Membership.objects.filter(user__pk=self._user.pk, project=OuterRef(_PK)),
        )
        visible_condition = Case(
            When(
                condition=membership_exists | Value(self._user.is_superuser) | Q(is_private=False),
                then=True,
            ),
            default=False,
        )
        qs = self._user_project_qs()
        return qs.annotate(
            cases_count=F('projectstatistics__cases_count'),
            suites_count=F('projectstatistics__suites_count'),
            plans_count=F('projectstatistics__plans_count'),
            tests_count=F('projectstatistics__tests_count'),
            is_visible=visible_condition,
            is_manageable=Value(True) if self._user.is_superuser else Exists(
                Membership.objects.filter(
                    user__pk=self._user.pk,
                    project=OuterRef(_PK),
                    role__permissions__codename=UserAllowedPermissionCodenames.CHANGE_PROJECT,
                ),
            ),
        ).distinct().order_by('name')

    def all_projects_statistic(self):
        projects = self._user_project_qs().filter(is_archive=False)
        return {
            'projects_count': projects.count(),
            'cases_count': TestCase.objects.filter(is_archive=False, project__in=projects).count(),
            'suites_count': TestSuite.objects.filter(project__in=projects).count(),
            'plans_count': TestPlan.objects.filter(is_archive=False, project__in=projects).count(),
            'tests_count': Test.objects.filter(is_archive=False, project__in=projects).count(),
        }

    def project_progress(self, project_id: int, period: PeriodDateTime):
        root_plans = (
            TestPlan
            .objects
            .filter(parent=None, project=project_id, is_archive=False)
            .prefetch_related('parameters')
        )
        root_plans = TestPlanSelector.annotate_title(root_plans).order_by('-id')
        tests_count_filter_mapping = {
            'tests_total': None,
            'tests_progress_period': [
                Q(results__created_at__range=(period.start, period.end)),
                Q(last_status_id__isnull=False),
            ],
            'tests_progress_total': [Q(last_status_id__isnull=False)],
        }
        for plan in root_plans:
            for test_field, test_filter in tests_count_filter_mapping.items():
                setattr(plan, test_field, self._test_count(plan, test_filter))
        return root_plans

    @classmethod
    def favorites_annotation(cls, favorite_conditions: Q) -> Case:
        return Case(
            When(favorite_conditions, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )

    @classmethod
    def _get_tests_subquery(cls, last_status_subquery):
        return Test.objects.filter(
            plan__tree_id=OuterRef('tree_id'),
            last_status__isnull=False,
        ).values(_PK)

    @classmethod
    def _test_count(cls, plan: TestPlan, filter_conditions: list[Q] | None = None) -> int:
        if not filter_conditions:
            filter_conditions = []
        return (
            Test.objects
            .filter(*filter_conditions, plan__tree_id=plan.tree_id)
            .values('plan__tree_id')
            .annotate(count=Count('id', distinct=True))
            .values_list('count', flat=True)
            .order_by('count')
            .first() or 0
        )

    def _user_project_qs(self, manager_name: str = 'objects') -> QuerySet[Project]:
        if not self._user:
            raise UserMissingError('User must be set to get queryset')
        is_external = RoleSelector.restricted_project_access(self._user)
        manager = getattr(Project, manager_name)
        return manager.filter(members=self._user) if is_external else manager.all()
