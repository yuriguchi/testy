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
from functools import partial

from rest_framework.fields import BooleanField, CharField, DateTimeField, IntegerField, ListField, SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField, PrimaryKeyRelatedField
from rest_framework.reverse import reverse
from rest_framework.serializers import JSONField, ModelSerializer, Serializer

from testy.core.api.v2.serializers import AttachmentSerializer, ParentMinSerializer
from testy.core.selectors.attachments import AttachmentSelector
from testy.core.validators import RecursionValidator
from testy.serializer_fields import EstimateField
from testy.tests_description.api.v2.serializers import TestCaseLabelOutputSerializer
from testy.tests_description.selectors.cases import TestCaseStepSelector
from testy.tests_representation.models import Parameter, ResultStatus, Test, TestPlan, TestResult, TestStepResult
from testy.tests_representation.selectors.parameters import ParameterSelector
from testy.tests_representation.selectors.testplan import TestPlanSelector
from testy.tests_representation.selectors.tests import TestSelector
from testy.tests_representation.validators import (
    AssigneeValidator,
    BulkUpdateExcludeIncludeValidator,
    DateRangeValidator,
    MoveTestsSameProjectValidator,
    ResultStatusValidator,
    TestPlanCasesValidator,
    TestPlanCustomAttributeValuesValidator,
    TestPlanParentValidator,
    TestResultArchiveTestValidator,
    TestResultCustomAttributeValuesValidator,
    TestResultUpdateValidator,
)
from testy.users.selectors.users import UserSelector
from testy.utilities.tree import get_breadcrumbs_treeview
from testy.validators import compare_related_manager, compare_steps, validator_launcher


class ParameterSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v2:parameter-detail')

    class Meta:
        model = Parameter
        fields = ('id', 'project', 'data', 'group_name', 'url')


class TestPlanUpdateSerializer(ModelSerializer):
    test_cases = ListField(child=IntegerField(required=False, allow_null=False), required=False, default=list)
    attachments = PrimaryKeyRelatedField(
        many=True, queryset=AttachmentSelector().attachment_list(), required=False,
    )

    class Meta:
        model = TestPlan
        fields = (
            'id',
            'name',
            'parent',
            'test_cases',
            'started_at',
            'due_date',
            'finished_at',
            'is_archive',
            'project',
            'attributes',
            'description',
            'attachments',
        )
        validators = [
            partial(
                validator_launcher,
                validator_instance=DateRangeValidator(),
                fields_to_validate=['started_at', 'due_date'],
            ),
            partial(
                validator_launcher,
                validator_instance=TestPlanParentValidator(),
                fields_to_validate=['parent'],
            ),
            partial(
                validator_launcher,
                validator_instance=TestPlanCasesValidator(),
                fields_to_validate=['test_cases'],
            ),
            TestPlanCustomAttributeValuesValidator(),
            RecursionValidator(TestPlan),
        ]


class TestPlanInputSerializer(TestPlanUpdateSerializer):
    parameters = PrimaryKeyRelatedField(queryset=ParameterSelector().parameter_list(), many=True, required=False)

    class Meta(TestPlanUpdateSerializer.Meta):
        fields = TestPlanUpdateSerializer.Meta.fields + ('parameters',)


class TestSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v2:test-detail')
    name = SerializerMethodField(read_only=True)
    last_status = IntegerField(source='last_status.id', read_only=True, default=None)
    last_status_name = CharField(source='last_status.name', read_only=True, default=None)
    last_status_color = CharField(source='last_status.color', read_only=True, default=None)
    suite = SerializerMethodField(read_only=True)
    labels = SerializerMethodField()
    suite_path = CharField(read_only=True)
    assignee_username = SerializerMethodField(read_only=True)
    avatar_link = SerializerMethodField(read_only=True)
    test_suite_description = CharField(read_only=True)
    estimate = EstimateField(read_only=True, allow_null=True, allow_blank=True)
    plan_path = CharField(read_only=True)

    class Meta:
        model = Test
        fields = (
            'id', 'project', 'case', 'suite', 'name', 'last_status', 'last_status_name', 'last_status_color',
            'plan', 'assignee', 'assignee_username', 'is_archive', 'created_at', 'updated_at', 'url', 'labels',
            'suite_path', 'avatar_link', 'test_suite_description', 'estimate', 'plan_path',
        )
        read_only_fields = ('project',)
        validators = [AssigneeValidator()]

    def get_assignee_username(self, instance):
        if instance.assignee:
            return instance.assignee.username

    def get_name(self, instance):
        return instance.case.name

    def get_labels(self, instance):
        return TestCaseLabelOutputSerializer(instance.case.labeled_items.all(), many=True).data

    @classmethod
    def get_suite(cls, instance):
        return instance.case.suite.id

    def get_avatar_link(self, instance):
        if not instance.assignee:
            return ''
        if not instance.assignee.avatar:
            return ''
        return self.context['request'].build_absolute_uri(
            reverse('avatar-path', kwargs={'pk': instance.assignee.id}),
        )


class TestStepResultSerializer(ModelSerializer):
    id = IntegerField(required=False)
    name = SerializerMethodField()
    sort_order = SerializerMethodField()
    status_text = CharField(source='status.name', read_only=True)
    status_color = CharField(source='status.color', read_only=True)

    class Meta:
        model = TestStepResult
        fields = ('id', 'step', 'name', 'status', 'status_text', 'status_color', 'sort_order')

    def get_name(self, instance):
        step = TestCaseStepSelector().get_step_by_step_result(instance)
        return step.name if step else '-'

    def get_sort_order(self, instance):
        step = TestCaseStepSelector().get_step_by_step_result(instance)
        return step.sort_order if step else 0


class TestResultSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v2:testresult-detail')
    status_text = CharField(source='status.name', read_only=True)
    status_color = CharField(source='status.color', read_only=True)
    user_full_name = SerializerMethodField(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    steps_results = TestStepResultSerializer(many=True, required=False)
    avatar_link = SerializerMethodField(read_only=True)
    latest = SerializerMethodField()

    class Meta:
        model = TestResult
        fields = (
            'id', 'project', 'status', 'status_text', 'status_color', 'test', 'user', 'user_full_name', 'comment',
            'avatar_link', 'is_archive', 'test_case_version', 'created_at', 'updated_at', 'url', 'execution_time',
            'attachments', 'attributes', 'steps_results', 'latest',
        )

        read_only_fields = ('test_case_version', 'project', 'user', 'id')
        validators = [TestResultArchiveTestValidator()]
        extra_kwargs = {
            'status': {
                'required': True,
                'allow_null': False,
            },
        }

    def get_avatar_link(self, instance):
        if not instance.user:
            return ''
        if not instance.user.avatar:
            return ''
        return self.context['request'].build_absolute_uri(
            reverse('avatar-path', kwargs={'pk': instance.user.id}),
        )

    def get_user_full_name(self, instance):
        if instance.user:
            return instance.user.get_full_name()

    def get_latest(self, instance):
        if not hasattr(instance, 'latest_result_id'):
            return None
        return instance.id == instance.latest_result_id


class TestResultActivitySerializer(ModelSerializer):
    status_text = CharField(source='status.name', read_only=True)
    status_color = CharField(source='status.color', read_only=True)
    action = SerializerMethodField()
    plan_id = SerializerMethodField()
    test_id = IntegerField()
    test_name = SerializerMethodField()
    action_day = DateTimeField()
    action_timestamp = DateTimeField(source='history_date')
    username = SerializerMethodField()
    avatar_link = SerializerMethodField(read_only=True)

    class Meta:
        model = TestResult
        fields = (
            'id', 'status', 'status_text', 'status_color', 'username', 'action', 'plan_id', 'test_id', 'test_name',
            'action_day', 'action_timestamp', 'avatar_link', 'is_archive',
        )

    @classmethod
    def get_test_name(cls, instance):
        return instance.test.case.name

    @classmethod
    def get_username(cls, instance):
        if instance.history_user:
            return instance.history_user.username
        return None

    @classmethod
    def get_action(cls, instance):
        if instance.history_type == '+':
            return 'added'
        elif instance.history_type == '-':
            return 'deleted'
        elif instance.history_type == '~':
            return 'updated'
        return 'unknown'

    @classmethod
    def get_plan_id(cls, instance):
        return instance.test.plan.id

    @classmethod
    def get_project(cls, instance):
        return instance.project.id

    @classmethod
    def get_project_title(cls, instance):
        return instance.project.name

    def get_avatar_link(self, instance):
        if not instance.history_user:
            return ''
        if not instance.history_user.avatar:
            return ''
        return self.context['request'].build_absolute_uri(
            reverse('avatar-path', kwargs={'pk': instance.history_user.id}),
        )


class TestResultInputSerializer(TestResultSerializer):
    attachments = PrimaryKeyRelatedField(
        many=True, queryset=AttachmentSelector().attachment_list(), required=False,
    )

    class Meta(TestResultSerializer.Meta):
        validators = TestResultSerializer.Meta.validators + [
            TestResultUpdateValidator(
                fields_to_comparator=(
                    (['status', 'execution_time', 'attributes'], lambda old_val, new_val: old_val == new_val),
                    (['attachments'], compare_related_manager),
                    (['steps_results'], compare_steps),
                    (['test', 'project'], lambda old_val, new_val: old_val.pk == new_val.pk),
                ),
            ),
            TestResultCustomAttributeValuesValidator(),
        ]


class ParentPlanSerializer(ModelSerializer):
    class Meta:
        model = TestPlan
        fields = ('id', 'name')


class TestPlanOutputSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v2:testplan-detail')
    title = CharField(read_only=True)
    parent = ParentMinSerializer(read_only=True)
    has_children = BooleanField(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = TestPlan
        fields = (
            'id',
            'name',
            'parent',
            'parameters',
            'started_at',
            'created_at',
            'due_date',
            'finished_at',
            'is_archive',
            'project',
            'url',
            'description',
            'title',
            'has_children',
            'attributes',
            'attachments',
        )

    @classmethod
    def get_name(cls, instance: TestPlan):
        if parameters := instance.parameters.all():
            return '{0} [{1}]'.format(instance.name, ', '.join([parameter.data for parameter in parameters]))
        return instance.name


class TestPlanUnionSerializer(TestPlanOutputSerializer):
    url = None
    has_children = BooleanField(read_only=True)
    is_leaf = BooleanField(read_only=True)

    class Meta:
        model = TestPlan
        fields = (
            'id',
            'name',
            'parent',
            'parameters',
            'started_at',
            'due_date',
            'finished_at',
            'is_archive',
            'project',
            'description',
            'title',
            'is_leaf',
            'has_children',
            'created_at',
        )


class TestUnionSerializer(TestSerializer):
    is_leaf = BooleanField(read_only=True)

    class Meta:
        model = Test
        fields = (
            'id',
            'project',
            'case',
            'suite',
            'name',
            'last_status',
            'last_status_color',
            'last_status_name',
            'plan',
            'assignee',
            'assignee_username',
            'is_archive',
            'created_at',
            'updated_at',
            'labels',
            'suite_path',
            'avatar_link',
            'test_suite_description',
            'estimate',
            'is_leaf',
        )


class TestPlanRetrieveSerializer(TestPlanOutputSerializer):
    breadcrumbs = SerializerMethodField()
    child_count = SerializerMethodField()
    parent = ParentPlanSerializer(read_only=True)

    class Meta(TestPlanOutputSerializer.Meta):
        fields = TestPlanOutputSerializer.Meta.fields + ('breadcrumbs', 'child_count')

    @classmethod
    def get_breadcrumbs(cls, instance: TestPlan):
        tree = TestPlanSelector.testplan_list_ancestors(instance)
        return get_breadcrumbs_treeview(
            instances=tree,
            depth=len(tree) - 1,
            title_method=cls.get_name,
        )

    @classmethod
    def get_child_count(cls, instance: TestPlan):
        return instance.child_test_plans.exists()


class TestPlanProgressSerializer(Serializer):
    id = IntegerField(read_only=True)
    title = CharField(read_only=True)
    tests_total = IntegerField(read_only=True)
    tests_progress_period = IntegerField(read_only=True)
    tests_progress_total = IntegerField(read_only=True)


class TestPlanDetailSerializer(Serializer):
    plan = PrimaryKeyRelatedField(queryset=TestPlanSelector.testplan_list_raw(), required=True)
    new_name = CharField(required=False)
    started_at = DateTimeField(required=False)
    due_date = DateTimeField(required=False)


class TestPlanCopySerializer(Serializer):
    plans = TestPlanDetailSerializer(many=True, required=True)
    dst_plan = PrimaryKeyRelatedField(
        queryset=TestPlanSelector.testplan_list_raw(),
        required=False,
        allow_null=True,
        allow_empty=True,
    )
    keep_assignee = BooleanField(default=False)


class TestPlanMinSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v2:testplan-detail')
    parent = ParentMinSerializer(read_only=True)
    attachments = PrimaryKeyRelatedField(many=True, required=False, read_only=True)

    class Meta:
        model = TestPlan
        exclude = ('is_deleted', 'created_at', 'updated_at', 'tree_id')


class ResultStatusSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v2:status-detail')

    class Meta:
        model = ResultStatus
        fields = 'id', 'url', 'name', 'color', 'type', 'project'
        validators = [ResultStatusValidator()]


class BulkUpdateTestsSerializer(Serializer):
    current_plan = PrimaryKeyRelatedField(
        queryset=TestPlanSelector.testplan_list_raw(),
        required=True,
        allow_null=False,
        allow_empty=False,
    )
    included_tests = PrimaryKeyRelatedField(
        queryset=TestSelector.test_list(),
        many=True,
        allow_empty=True,
        allow_null=False,
        required=False,
    )
    excluded_tests = PrimaryKeyRelatedField(
        queryset=TestSelector.test_list(),
        many=True,
        allow_empty=True,
        allow_null=False,
        required=False,
    )
    plan = PrimaryKeyRelatedField(
        queryset=TestPlanSelector.testplan_list_raw(),
        required=False,
        allow_null=False,
        allow_empty=False,
    )
    assignee = PrimaryKeyRelatedField(
        queryset=UserSelector().user_list(),
        allow_empty=False,
        allow_null=True,
        required=False,
    )
    filter_conditions = JSONField(required=False, allow_null=False, initial=dict, default=dict)

    class Meta:
        validators = [
            partial(
                validator_launcher,
                validator_instance=MoveTestsSameProjectValidator(),
                fields_to_validate=['current_plan', 'plan'],
            ),
            partial(
                validator_launcher,
                validator_instance=BulkUpdateExcludeIncludeValidator(),
                fields_to_validate=['included_tests', 'excluded_tests', 'filter_conditions'],
                none_valid_fields=['included_tests', 'excluded_tests', 'filter_conditions'],
            ),
            AssigneeValidator(),
        ]


class TestPlanTreeBreadcrumbsSerializer(ModelSerializer):
    has_children = BooleanField(read_only=True)
    parent = ParentMinSerializer(read_only=True)
    children = SerializerMethodField()
    title = CharField(read_only=True)

    def get_children(self, instance):
        serializer_class = type(self)
        return serializer_class(instance.child_test_plans.all(), many=True).data

    class Meta:
        model = TestPlan
        fields = ('id', 'title', 'has_children', 'parent', 'children')
