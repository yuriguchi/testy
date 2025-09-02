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
from django.db.models import OuterRef, Q, Sum
from rest_framework.fields import SerializerMethodField
from rest_framework.reverse import reverse

from testy.core.api.v1.serializers import (
    NotificationSettingSerializer,
    ProjectRetrieveSerializer,
    ProjectStatisticsSerializer,
)
from testy.tests_description.api.v1.serializers import (
    TestCaseRetrieveSerializer,
    TestSuiteBaseSerializer,
    TestSuiteRetrieveSerializer,
    TestSuiteSerializer,
    TestSuiteTreeSerializer,
)
from testy.tests_description.models import TestCase, TestSuite
from testy.tests_representation.api.v1.serializers import TestSerializer
from testy.tests_representation.models import Test, TestPlan
from testy.users.models import Membership
from testy.users.selectors.roles import RoleSelector
from testy.utilities.time import WorkTimeProcessor


class TestMockSerializer(TestSerializer):
    suite_path = SerializerMethodField(read_only=True)
    test_suite_description = SerializerMethodField(read_only=True)
    estimate = SerializerMethodField()

    def get_suite_path(self, instance):
        return '/'.join([elem.name for elem in instance.case.suite.get_ancestors(include_self=True)])

    def get_test_suite_description(self, instance):
        return instance.case.suite.description

    def get_estimate(self, instance):
        if not instance.case.estimate:
            return None
        return WorkTimeProcessor.format_duration(instance.case.estimate)


class TestSuiteMockTreeSerializer(TestSuiteTreeSerializer):
    descendant_count = SerializerMethodField()
    cases_count = SerializerMethodField()
    total_cases_count = SerializerMethodField()
    estimates = SerializerMethodField()
    total_estimates = SerializerMethodField()

    class Meta:
        model = TestSuite
        fields = TestSuiteBaseSerializer.Meta.fields + (
            'children', 'title', 'descendant_count', 'cases_count', 'total_cases_count', 'total_estimates', 'estimates',
        )

    def get_descendant_count(self, instance):
        return instance.get_descendant_count()

    def get_cases_count(self, instance):
        return instance.test_cases.count()

    def get_total_cases_count(self, instance):
        return TestCase.objects.filter(suite__in=instance.get_descendants(include_self=True)).count()

    def get_total_estimates(self, instance):
        sum_condition = Q(test_cases__is_deleted=False) & Q(test_cases__is_archive=False)
        filter_condition = (
            Q(tree_id=OuterRef('tree_id')) &  # noqa: W504
            Q(lft__gte=OuterRef('lft')) &  # noqa: W504
            Q(rght__lte=OuterRef('rght'))
        )
        return self._get_suites_query(filter_condition, sum_condition)

    def get_estimates(self, instance):
        sum_condition = Q(test_cases__is_deleted=False) & Q(test_cases__is_archive=False)
        return self._get_suites_query(Q(pk=OuterRef('pk')), sum_condition)

    @classmethod
    def _get_suites_query(cls, filter_condition, sum_condition):
        (
            TestSuite.objects.filter(filter_condition)
            .prefetch_related('test_cases')
            .values('tree_id')
            .annotate(
                total=Sum('test_cases__estimate', filter=sum_condition),
            )
            .values('total')
        )


class ProjectRetrieveMockSerializer(ProjectRetrieveSerializer):
    is_manageable = SerializerMethodField()

    def get_is_manageable(self, instance):
        user = self.context.get('request').user
        return RoleSelector.can_assign_role(user, instance.pk) or user.is_superuser


class ProjectStatisticsMockSerializer(ProjectRetrieveMockSerializer):
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
            reverse('api:v1:project-icon', kwargs={'pk': instance.id}),
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

    class Meta(ProjectStatisticsSerializer.Meta):
        """Get fields configuration."""


class TestCaseMockSerializer(TestCaseRetrieveSerializer):
    """Test case mock serializer to avoid prefetching in tests."""


class PathRetrieveMixin:
    def get_path(self, instance):
        return '/'.join(suite.name for suite in instance.get_ancestors(include_self=True))


class TestSuiteBaseMockSerializer(TestSuiteBaseSerializer, PathRetrieveMixin):
    path = SerializerMethodField()


class TestSuiteMockSerializer(TestSuiteSerializer, PathRetrieveMixin):
    path = SerializerMethodField()


class TestSuiteRetrieveMockSerializer(TestSuiteRetrieveSerializer, PathRetrieveMixin):
    path = SerializerMethodField()
    descendant_count = SerializerMethodField()
    cases_count = SerializerMethodField()
    total_cases_count = SerializerMethodField()
    estimates = SerializerMethodField()
    total_estimates = SerializerMethodField()

    @classmethod
    def get_descendant_count(cls, instance):
        return instance.get_descendant_count()

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
        sum_condition = Q(test_cases__is_deleted=False) & Q(test_cases__is_archive=False)
        filter_condition = Q(tree_id=instance.tree_id) & Q(lft__gte=instance.lft) & Q(rght__lte=instance.rght)
        return (
            TestSuite.objects.filter(filter_condition)
            .prefetch_related('test_cases')
            .values('tree_id')
            .annotate(
                total=Sum('test_cases__estimate', filter=sum_condition),
            )
            .values_list('total', flat=True)[0]
        )


class NotificationSettingMockSerializer(NotificationSettingSerializer):
    enabled = SerializerMethodField()

    def get_enabled(self, instance):
        user = self.context.get('request').user
        return instance.subscribers.filter(pk=user.pk).exists()
