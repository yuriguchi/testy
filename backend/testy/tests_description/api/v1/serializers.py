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

from rest_framework import serializers
from rest_framework.fields import BooleanField, CharField, IntegerField, ListField, SerializerMethodField, empty
from rest_framework.relations import HyperlinkedIdentityField, PrimaryKeyRelatedField

from testy.core.api.v1.serializers import AttachmentSerializer, CopyDetailSerializer
from testy.core.models import Label, LabeledItem
from testy.core.selectors.attachments import AttachmentSelector
from testy.core.selectors.projects import ProjectSelector
from testy.serializer_fields import EstimateField
from testy.tests_description.models import TestCase, TestCaseStep, TestSuite
from testy.tests_description.selectors.cases import TestCaseSelector, TestCaseStepSelector
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.tests_description.validators import (
    CasesCopyProjectValidator,
    EstimateValidator,
    TestCaseCustomAttributeValuesValidator,
)
from testy.users.api.v1.serializers import UserSerializer
from testy.utilities.tree import get_breadcrumbs_treeview
from testy.validators import validator_launcher


class TestCaseStepBaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = TestCaseStep
        fields = ('id', 'name', 'scenario', 'expected', 'sort_order')
        ref_name = 'TestCaseStepBaseV1'


class TestCaseStepInputSerializer(TestCaseStepBaseSerializer):
    attachments = PrimaryKeyRelatedField(
        many=True, queryset=AttachmentSelector().attachment_list(), required=False,
    )

    class Meta(TestCaseStepBaseSerializer.Meta):
        fields = TestCaseStepBaseSerializer.Meta.fields + ('attachments',)
        ref_name = 'TestCaseStepInputV1'


class TestCaseStepOutputSerializer(TestCaseStepBaseSerializer):
    attachments = SerializerMethodField(read_only=True)

    class Meta(TestCaseStepBaseSerializer.Meta):
        fields = TestCaseStepBaseSerializer.Meta.fields + ('attachments',)
        ref_name = 'TestCaseStepOutputV1'

    def get_attachments(self, instance):
        if (version := self.context.get('version', None)) is not None:
            attachments = TestCaseStepSelector.get_attachments_by_case_version(instance, version)
        else:
            attachments = instance.attachments.all()

        return AttachmentSerializer(attachments, many=True, context=self.context).data


class TestCaseBaseSerializer(serializers.ModelSerializer):
    estimate = EstimateField(allow_null=True, required=False)

    class Meta:
        model = TestCase
        fields = (
            'id',
            'name',
            'project',
            'suite',
            'setup',
            'scenario',
            'expected',
            'teardown',
            'estimate',
            'description',
            'is_steps',
            'is_archive',
            'attributes',
        )
        ref_name = 'TestCaseBaseV1'

    validators = [
        partial(
            validator_launcher,
            validator_instance=EstimateValidator(),
            fields_to_validate=['estimate'],
        ),
        TestCaseCustomAttributeValuesValidator(),
    ]


class TestCaseLabelOutputSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='label.id')
    name = serializers.CharField(source='label.name')

    class Meta:
        model = LabeledItem
        fields = ('id', 'name')
        ref_name = 'TestCaseLabelOutputV1'


class TestCaseLabelInputSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Label
        fields = ('id', 'name')
        ref_name = 'TestCaseLabelInputV1'


class TestCaseInputBaseSerializer(TestCaseBaseSerializer):
    attachments = PrimaryKeyRelatedField(
        many=True, queryset=AttachmentSelector().attachment_list(), required=False,
    )
    labels = TestCaseLabelInputSerializer(many=True, required=False)
    skip_history = serializers.BooleanField(default=False, initial=False)

    class Meta(TestCaseBaseSerializer.Meta):
        fields = TestCaseBaseSerializer.Meta.fields + ('attachments', 'labels', 'skip_history')
        ref_name = 'TestCaseInputV1'

    def validate(self, attrs):
        if attrs['skip_history']:
            request = self.context['request']
            history_latest = TestCaseSelector.get_last_history(self.instance.pk)
            if request.user != history_latest.history_user:
                raise serializers.ValidationError('Only author of latest change can skip version')

        return attrs


class TestCaseInputSerializer(TestCaseInputBaseSerializer):
    scenario = serializers.CharField(required=True)

    class Meta(TestCaseInputBaseSerializer.Meta):
        ref_name = 'TestCaseBaseInputV1'


class TestCaseInputWithStepsSerializer(TestCaseInputBaseSerializer):
    scenario = serializers.CharField(allow_blank=True, required=False)
    steps = TestCaseStepInputSerializer(many=True, required=True)

    class Meta(TestCaseInputBaseSerializer.Meta):
        fields = TestCaseInputBaseSerializer.Meta.fields + ('steps',)
        ref_name = 'TestCaseInputWithStepsV1'

    def validate_steps(self, value):
        if not len(value):
            raise serializers.ValidationError('At least one step required')
        return value


class TestCaseListSerializer(TestCaseBaseSerializer):
    steps = SerializerMethodField(read_only=True)
    url = HyperlinkedIdentityField(view_name='api:v1:testcase-detail')
    attachments = SerializerMethodField()
    labels = SerializerMethodField(read_only=True)
    versions = ListField(child=IntegerField(), read_only=True)
    current_version = SerializerMethodField(read_only=True)
    suite_name = CharField(source='suite.name', read_only=True)

    def __init__(self, instance=None, version=None, data=empty, **kwargs):
        self._version = version
        super().__init__(instance, data, **kwargs)

    class Meta(TestCaseBaseSerializer.Meta):
        fields = TestCaseBaseSerializer.Meta.fields + (
            'attachments', 'url', 'steps', 'labels', 'versions', 'current_version', 'suite_name',
        )
        ref_name = 'TestCaseListSerializerV1'

    def get_current_version(self, instance):
        if self._version is not None:
            return self._version
        return instance.current_version

    def get_labels(self, instance):
        if self._version is not None:
            labels = LabeledItem.history.filter(content_object_history_id=self._version).as_instances()
        else:
            labels = instance.labeled_items.all()
        return TestCaseLabelOutputSerializer(labels, many=True, context=self.context).data

    def get_steps(self, instance):
        if self._version is not None:
            steps = TestCaseStepSelector.get_steps_by_case_version_id(self._version)
        else:
            steps = instance.steps.all()
        return TestCaseStepOutputSerializer(steps, many=True, context={'version': self._version, **self.context}).data

    def get_attachments(self, instance):
        if self._version is None:
            attachments = instance.attachments.all()
        else:
            attachments = AttachmentSelector.attachment_list_by_parent_object_and_history_ids(
                instance, instance.id, [self._version],
            )
        return AttachmentSerializer(attachments, many=True, context=self.context).data


class TestCaseRetrieveSerializer(TestCaseListSerializer):
    versions = SerializerMethodField(read_only=True)
    current_version = SerializerMethodField(read_only=True)

    def get_versions(self, instance):
        return instance.history.values_list('history_id', flat=True).order_by('-history_id').all()

    def get_current_version(self, instance):
        if self._version is not None:
            return self._version
        return instance.history.first().history_id

    class Meta(TestCaseListSerializer.Meta):
        ref_name = 'TestCaseRetrieveV1'


class TestCaseTreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ('id', 'name')


class ParentSuiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSuite
        fields = ('id', 'name')


class TestSuiteBaseSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:testsuite-detail')
    suite_path = serializers.CharField(read_only=True)

    class Meta:
        model = TestSuite
        fields = ('id', 'name', 'parent', 'project', 'url', 'description', 'path', 'suite_path')
        ref_name = 'TestSuiteBaseSerializerV1'


class TestSuiteSerializer(TestSuiteBaseSerializer):
    test_cases = TestCaseListSerializer(many=True, read_only=True)

    class Meta:
        model = TestSuite
        fields = TestSuiteBaseSerializer.Meta.fields + ('test_cases',)
        ref_name = 'TestSuiteSerializerV1'


class TestSuiteTreeSerializer(TestSuiteBaseSerializer):
    children = SerializerMethodField()
    title = serializers.CharField(source='name')
    descendant_count = IntegerField()
    cases_count = IntegerField()
    parent = ParentSuiteSerializer()
    total_cases_count = IntegerField()
    estimates = EstimateField()
    total_estimates = EstimateField()

    class Meta:
        model = TestSuite
        fields = TestSuiteBaseSerializer.Meta.fields + (
            'children', 'title', 'descendant_count', 'cases_count', 'total_cases_count', 'total_estimates', 'estimates',
        )

    def get_children(self, value):
        return self.__class__(value.child_test_suites.all(), many=True, context=self.context).data


class TestSuiteTreeBreadcrumbsSerializer(TestSuiteTreeSerializer):
    is_used = BooleanField()

    class Meta:
        model = TestSuite
        fields = ('id', 'title', 'children', 'is_used')
        ref_name = 'TestSuiteTreeBreadcrumbsSerializerV1'


class TestSuiteTreeCasesSerializer(TestSuiteTreeSerializer):
    test_cases = TestCaseTreeSerializer(many=True, read_only=True)

    class Meta:
        model = TestSuite
        fields = TestSuiteTreeSerializer.Meta.fields + ('test_cases',)


class TestCaseCopySerializer(serializers.Serializer):
    cases = CopyDetailSerializer(many=True, required=True)
    dst_suite_id = serializers.PrimaryKeyRelatedField(queryset=TestSuiteSelector.suite_list_raw(), required=False)

    class Meta:
        validators = [
            partial(
                validator_launcher,
                validator_instance=CasesCopyProjectValidator(),
                fields_to_validate=['dst_suite_id', 'cases'],
            ),
        ]
        ref_name = 'TestCaseCopyV1'


class TestSuiteCopySerializer(serializers.Serializer):
    suites = CopyDetailSerializer(many=True, required=True)
    dst_project_id = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        queryset=ProjectSelector.project_list_raw(),
    )
    dst_suite_id = serializers.PrimaryKeyRelatedField(
        queryset=TestSuiteSelector.suite_list_raw(),
        required=False,
        allow_null=True,
    )

    class Meta:
        ref_name = 'TestCaseCopyV1'


class TestCaseHistorySerializer(serializers.Serializer):
    HISTORY_TYPES = {
        '+': 'Created',
        '~': 'Updated',
        '-': 'Deleted',
    }
    user = SerializerMethodField(read_only=True)
    version = IntegerField(source='history_id')
    action = SerializerMethodField(read_only=True)
    history_date = serializers.DateTimeField()

    def get_user(self, instance):
        if instance.history_user:
            return UserSerializer(instance.history_user, context=self.context).data
        return None

    def get_action(self, instance):
        return self.HISTORY_TYPES.get(instance.history_type)

    class Meta:
        ref_name = 'TestCaseHistoryV1'


class TestCaseRestoreSerializer(serializers.Serializer):
    version = IntegerField(required=True)

    def validate_version(self, version):
        if not TestCaseSelector.version_exists(version=version, pk=self.instance.id):
            raise serializers.ValidationError('Incorrect version')
        return version

    class Meta:
        ref_name = 'TestCaseRestoreV1'


class TestSuiteRetrieveSerializer(TestSuiteBaseSerializer):
    breadcrumbs = SerializerMethodField()
    title = serializers.CharField(source='name')
    descendant_count = IntegerField()
    cases_count = IntegerField()
    parent = ParentSuiteSerializer()
    total_cases_count = IntegerField()
    estimates = EstimateField()
    total_estimates = EstimateField()
    child_count = SerializerMethodField()

    class Meta(TestSuiteBaseSerializer.Meta):
        fields = TestSuiteBaseSerializer.Meta.fields + (
            'breadcrumbs',
            'title',
            'descendant_count',
            'cases_count',
            'total_cases_count',
            'estimates',
            'total_estimates',
            'child_count',
        )
        ref_name = 'TestSuiteRetrieveV1'

    @classmethod
    def get_breadcrumbs(cls, instance: TestSuite):
        tree = TestSuiteSelector.suite_list_ancestors(instance)
        return get_breadcrumbs_treeview(
            instances=tree,
            depth=len(tree) - 1,
            title_method=lambda obj: obj.name,
        )

    @classmethod
    def get_child_count(cls, instance: TestSuite):
        return instance.child_test_suites.count()


class TestSuiteTreeSerializer(TestSuiteBaseSerializer):
    children = SerializerMethodField()
    title = serializers.CharField(source='name')
    descendant_count = IntegerField()
    cases_count = IntegerField()
    parent = ParentSuiteSerializer()
    total_cases_count = IntegerField()
    estimates = EstimateField()
    total_estimates = EstimateField()

    class Meta:
        model = TestSuite
        fields = TestSuiteBaseSerializer.Meta.fields + (
            'children', 'title', 'descendant_count', 'cases_count', 'total_cases_count', 'total_estimates', 'estimates',
        )

    def get_children(self, value):
        return self.__class__(value.child_test_suites.all(), many=True, context=self.context).data
