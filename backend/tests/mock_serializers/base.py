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
from django.db.models import Q, Sum
from rest_framework.fields import SerializerMethodField
from rest_framework.reverse import reverse
from rest_framework.serializers import Serializer

from testy.tests_description.models import TestCase, TestSuite
from testy.tests_representation.models import Test, TestPlan
from testy.users.models import Membership
from testy.users.selectors.roles import RoleSelector
from testy.utilities.time import WorkTimeProcessor


class BaseIsManageableProject(Serializer):
    is_manageable = SerializerMethodField()

    def get_is_manageable(self, instance):
        user = self.context.get('request').user
        return RoleSelector.can_assign_role(user, instance.pk) or user.is_superuser


class BaseProjectStatisticsMockSerializer(Serializer):
    cases_count = SerializerMethodField()
    suites_count = SerializerMethodField()
    plans_count = SerializerMethodField()
    tests_count = SerializerMethodField()
    is_visible = SerializerMethodField()

    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)
        self._user = user

    def get_icon(self, instance):
        if not instance.icon:
            return ''
        return self.context['request'].build_absolute_uri(
            reverse('api:v2:project-icon', kwargs={'pk': instance.id}),
        )

    @classmethod
    def get_cases_count(cls, instance):
        return TestCase.objects.filter(project=instance).count()

    @classmethod
    def get_suites_count(cls, instance):
        return TestSuite.objects.filter(project=instance).count()

    @classmethod
    def get_plans_count(cls, instance):
        return TestPlan.objects.filter(project=instance).count()

    @classmethod
    def get_tests_count(cls, instance):
        return Test.objects.filter(project=instance).count()

    def get_is_visible(self, instance):
        user = self.context.get('request').user
        membership_exists = Membership.objects.filter(user__pk=user.pk, project=instance).exists()
        not_private = instance.is_private and not RoleSelector.restricted_project_access(user)
        return membership_exists or not_private or user.is_superuser


class BaseNotificationSettingMockSerializer(Serializer):
    enabled = SerializerMethodField()

    def get_enabled(self, instance):
        user = self.context.get('request').user
        return instance.subscribers.filter(pk=user.pk).exists()


class PathRetrieveMixin(Serializer):
    suite_path = SerializerMethodField()

    def get_suite_path(self, instance):
        return '/'.join(suite.name for suite in instance.get_ancestors(include_self=True))


class BaseTestSuiteMockOutputSerializer(PathRetrieveMixin):
    descendant_count = SerializerMethodField()
    cases_count = SerializerMethodField()
    total_cases_count = SerializerMethodField()
    total_estimates = SerializerMethodField()
    estimates = SerializerMethodField()
    suite_path = SerializerMethodField()
    has_children = SerializerMethodField()

    def get_descendant_count(self, instance):
        return instance.get_descendants().count()

    def get_cases_count(self, instance):
        return instance.test_cases.count()

    def get_total_cases_count(self, instance):
        return TestCase.objects.filter(suite__in=instance.get_descendants(include_self=True)).count()

    def get_total_estimates(self, instance):
        count = sum(
            TestCase.objects.filter(
                suite__in=TestSuite.objects.filter(path__descendant=instance.path),
                is_archive=False,
            ).values_list('estimate', flat=True),
        )
        return count if count > 0 else None

    def get_estimates(self, instance):
        count = sum(
            TestCase.objects.filter(
                suite=instance,
                is_archive=False,
            ).values_list('estimate', flat=True),
        )
        return count if count > 0 else None

    def get_has_children(self, instance):
        return instance.child_test_suites.exists()


class BaseTestSuiteRetrieveMockSerializer(Serializer):
    descendant_count = SerializerMethodField()
    cases_count = SerializerMethodField()
    total_cases_count = SerializerMethodField()
    estimates = SerializerMethodField()
    total_estimates = SerializerMethodField()
    suite_path = SerializerMethodField()

    @classmethod
    def get_descendant_count(cls, instance):
        return instance.get_descendants().count()

    @classmethod
    def get_suite_path(cls, instance):
        return '/'.join([elem.name for elem in instance.get_ancestors(include_self=True)])

    @classmethod
    def get_cases_count(cls, instance):
        return TestCase.objects.filter(suite=instance).count()

    @classmethod
    def get_total_cases_count(cls, instance):
        return TestCase.objects.filter(suite__in=instance.get_descendants(include_self=True)).count()

    @classmethod
    def get_estimates(cls, instance):
        sum_condition = Q(test_cases__is_deleted=False) & Q(test_cases__is_archive=False)
        return (
            TestSuite.objects.filter(pk=instance.pk)
            .prefetch_related('test_cases')
            .values('tree_id')
            .annotate(
                total=Sum('test_cases__estimate', filter=sum_condition),
            )
            .values_list('total', flat=True)[0]
        )

    @classmethod
    def get_total_estimates(cls, instance):
        count = sum(
            TestCase.objects.filter(
                suite__in=TestSuite.objects.filter(path__descendant=instance.path),
                is_archive=False,
            ).values_list('estimate', flat=True),
        )
        return count if count > 0 else None


class BaseTestMockSerializer(Serializer):
    test_suite_description = SerializerMethodField(read_only=True)
    estimate = SerializerMethodField()

    def get_test_suite_description(self, instance):
        return instance.case.suite.description

    def get_estimate(self, instance):
        if not instance.case.estimate:
            return None
        return WorkTimeProcessor.format_duration(instance.case.estimate)
