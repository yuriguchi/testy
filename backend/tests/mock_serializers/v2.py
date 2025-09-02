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
from rest_framework.fields import CharField, DateTimeField, SerializerMethodField

from tests.mock_serializers.base import (
    BaseIsManageableProject,
    BaseNotificationSettingMockSerializer,
    BaseProjectStatisticsMockSerializer,
    BaseTestMockSerializer,
    BaseTestSuiteMockOutputSerializer,
    BaseTestSuiteRetrieveMockSerializer,
)
from testy.core.api.v2.serializers import (
    NotificationSettingSerializer,
    ParentMinSerializer,
    ProjectRetrieveSerializer,
    ProjectStatisticsSerializer,
)
from testy.tests_description.api.v2.serializers import (
    TestCaseListSerializer,
    TestCaseRetrieveSerializer,
    TestCaseUnionSerializer,
    TestSuiteBaseSerializer,
    TestSuiteOutputSerializer,
    TestSuiteRetrieveSerializer,
    TestSuiteSerializer,
)
from testy.tests_description.models import TestSuite
from testy.tests_representation.api.v2.serializers import (
    TestPlanOutputSerializer,
    TestPlanUnionSerializer,
    TestSerializer,
    TestUnionSerializer,
)
from testy.tests_representation.models import TestPlan
from testy.tests_representation.selectors.testplan import TestPlanSelector
from testy.utilities.time import WorkTimeProcessor


class TestMockSerializer(BaseTestMockSerializer, TestSerializer):
    suite_path = SerializerMethodField(read_only=True)
    plan_path = SerializerMethodField()

    def get_suite_path(self, instance):
        return '/'.join([elem.name for elem in instance.case.suite.get_ancestors(include_self=True)])

    def get_plan_path(self, instance):
        plans = instance.plan.get_ancestors(include_self=True)
        plans = TestPlanSelector.annotate_title(plans)
        return '/'.join([elem.title for elem in plans])


class ProjectRetrieveMockSerializer(BaseIsManageableProject, ProjectRetrieveSerializer):
    """V2 implementation"""


class ProjectStatisticsMockSerializer(
    BaseProjectStatisticsMockSerializer,
    BaseIsManageableProject,
    ProjectStatisticsSerializer,
):
    """V2 implementation"""


class PathRetrieveMixin:
    def get_suite_path(self, instance):
        return '/'.join(suite.name for suite in instance.get_ancestors(include_self=True))


class TestCaseMockSerializer(TestCaseRetrieveSerializer):
    versions = SerializerMethodField()
    created_at = DateTimeField()

    def get_versions(self, instance):
        return list(instance.history.values_list('history_id', flat=True).order_by('-history_date'))

    class Meta(TestCaseRetrieveSerializer.Meta):
        fields = TestCaseRetrieveSerializer.Meta.fields + ('created_at',)


class TestCaseListMockSerializer(TestCaseListSerializer):
    suite_path = SerializerMethodField()
    versions = SerializerMethodField()

    def get_versions(self, instance):
        return list(instance.history.values_list('history_id', flat=True).order_by('-history_date'))

    def get_suite_path(self, instance):
        return '/'.join(suite.name for suite in instance.suite.get_ancestors(include_self=True))

    def get_current_version(self, instance):
        if self._version is not None:
            return self._version
        return instance.history.first().history_id


class TestSuiteBaseMockSerializer(TestSuiteBaseSerializer, PathRetrieveMixin):
    """V2 implementation"""


class TestSuiteMockSerializer(TestSuiteSerializer, PathRetrieveMixin):
    """V2 implementation"""


class TestSuiteMockOutputSerializer(BaseTestSuiteMockOutputSerializer, TestSuiteOutputSerializer):
    """V2 implementation"""


class TestSuiteRetrieveMockSerializer(BaseTestSuiteRetrieveMockSerializer, TestSuiteRetrieveSerializer):
    """V1 implementation"""


class TestPlanOutputMockSerializer(TestPlanOutputSerializer):
    title = SerializerMethodField()
    has_children = SerializerMethodField()

    @classmethod
    def get_title(cls, instance: TestPlan):
        if parameters := instance.parameters.all().order_by('id'):
            return '{0} [{1}]'.format(instance.name, ', '.join([parameter.data for parameter in parameters]))
        return instance.name

    @classmethod
    def get_has_children(cls, instance: TestPlan) -> bool:
        return instance.child_test_plans.exists() or instance.tests.exists()


class NotificationSettingMockSerializer(BaseNotificationSettingMockSerializer, NotificationSettingSerializer):
    """V2 implementation"""


class TestPlanUnionMockSerializer(TestPlanUnionSerializer):
    is_leaf = SerializerMethodField()
    has_children = SerializerMethodField()
    title = SerializerMethodField()

    def get_is_leaf(self, instance):
        return False

    def get_has_children(self, instance):
        return instance.child_test_plans.exists() or instance.tests.exists()

    def get_title(self, instance: TestPlan):
        if parameters := instance.parameters.all().order_by('id'):
            return '{0} [{1}]'.format(instance.name, ', '.join([parameter.data for parameter in parameters]))
        return instance.name


class TestUnionMockSerializer(TestUnionSerializer):
    is_leaf = SerializerMethodField()
    last_status = SerializerMethodField()
    last_status_color = SerializerMethodField()
    last_status_name = SerializerMethodField()
    assignee_username = SerializerMethodField()
    suite_path = SerializerMethodField()
    estimate = SerializerMethodField()
    test_suite_description = CharField(source='case.suite.description')

    def get_is_leaf(self, instance):
        return True

    def get_last_status(self, instance):
        result = instance.results.order_by('-created_at').first()
        if not result:
            return None
        return result.status.pk

    def get_last_status_color(self, instance):
        result = instance.results.order_by('-created_at').first()
        if not result:
            return None
        return result.status.color

    def get_last_status_name(self, instance):
        result = instance.results.order_by('-created_at').first()
        if not result:
            return None
        return result.status.name

    def get_assignee_username(self, instance):
        return instance.assignee.username

    def get_suite_path(self, instance):
        return '/'.join(suite.name for suite in instance.case.suite.get_ancestors(include_self=True))

    def get_estimate(self, instance):
        if not instance.case.estimate:
            return None
        return WorkTimeProcessor.format_duration(instance.case.estimate)


class TestSuiteUnionMockSerializer(TestSuiteMockOutputSerializer):
    is_leaf = SerializerMethodField()
    has_children = SerializerMethodField()
    url = None

    def get_is_leaf(self, instance):
        return False

    def get_has_children(self, instance):
        return instance.child_test_suites.exists() or instance.test_cases.exists()

    class Meta:
        model = TestSuite
        fields = (
            'id',
            'name',
            'parent',
            'project',
            'description',
            'descendant_count',
            'cases_count',
            'total_cases_count',
            'total_estimates',
            'estimates',
            'is_leaf',
            'has_children',
            'created_at',
            'suite_path',
        )


class TestCaseUnionMockSerializer(TestCaseUnionSerializer):
    is_leaf = SerializerMethodField()
    parent = ParentMinSerializer(read_only=True, source='suite')
    labels = SerializerMethodField()
    current_version = SerializerMethodField()
    versions = SerializerMethodField()
    suite_path = SerializerMethodField()

    def get_current_version(self, instance):
        if self._version is not None:
            return self._version
        return instance.history.first().history_id

    def get_suite_path(self, instance):
        return '/'.join(suite.name for suite in instance.suite.get_ancestors(include_self=True))

    def get_versions(self, instance):
        return list(instance.history.values_list('history_id', flat=True).order_by('-history_date'))

    def get_is_leaf(self, instance):
        return True
