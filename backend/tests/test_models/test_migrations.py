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

import pytest
from allure_commons.utils import uuid4
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils import timezone
from mptt import register
from mptt.models import MPTTOptions

from tests import constants
from tests.constants import WORKDAY_IN_SECONDS
from testy.core.choices import CustomFieldType
from testy.core.selectors.custom_attribute import CustomAttributeSelector
from testy.tests_representation.choices import ResultStatusType, TestStatuses

pytestmark = pytest.mark.django_db


class MPTTMeta(MPTTOptions):
    def __new__(cls, root_node_ordering: bool):
        cls.root_node_ordering = root_node_ordering
        cls.order_insertion_by = []
        cls.left_attr = 'lft'
        cls.right_attr = 'rght'
        cls.tree_id_attr = 'tree_id'
        cls.level_attr = 'level'
        cls.parent_attr = 'parent'
        return super().__new__(cls)


def test_changed_testplan_parameters_m2m(migrator):
    """Testing migrations 0011_added_testplan_parameters_m2m...0014_rename_parameters_m2m_testplan_parameters"""
    old_state = migrator.apply_initial_migration(
        ('tests_representation', '0010_added_updated_choices_to_tables'),
    )

    project_model = old_state.apps.get_model('core', 'Project')
    parameter_model = old_state.apps.get_model('tests_representation', 'Parameter')
    test_plan_model = old_state.apps.get_model('tests_representation', 'TestPlan')

    register(test_plan_model)

    project = project_model.objects.create(name='ProjectTest')
    parameters = parameter_model.objects.bulk_create([
        parameter_model(project=project, group_name='GroupTest1', data='Name1'),
        parameter_model(project=project, group_name='GroupTest2', data='Name2'),
    ])

    parameters_list_id = [p.id for p in parameters]

    test_plan = test_plan_model.objects.create(
        name='TestPlanTest',
        project=project,
        parameters=parameters_list_id,
        started_at=timezone.now(),
        due_date=timezone.now(),
    )

    assert isinstance(test_plan.parameters, list)
    assert test_plan.parameters == parameters_list_id

    new_state = migrator.apply_tested_migration(
        ('tests_representation', '0014_rename_parameters_m2m_testplan_parameters'),
    )
    test_plan_model = new_state.apps.get_model('tests_representation', 'TestPlan')
    new_test_plan = test_plan_model.objects.first()
    parameters_m2m = new_test_plan.parameters.all()

    assert isinstance(parameters_m2m, QuerySet)
    assert parameters_m2m[0].id == parameters[0].id
    assert parameters_m2m[1].id == parameters[1].id

    migrator.reset()


def test_changed_testplan_parameters_list(migrator):
    """
    Testing backwards migrations 0011_added_testplan_parameters_m2m...0014_rename_parameters_m2m_testplan_parameters
    """
    old_state = migrator.apply_initial_migration(
        ('tests_representation', '0014_rename_parameters_m2m_testplan_parameters'),
    )

    project_model = old_state.apps.get_model('core', 'Project')
    parameter_model = old_state.apps.get_model('tests_representation', 'Parameter')
    test_plan_model = old_state.apps.get_model('tests_representation', 'TestPlan')

    register(test_plan_model)

    project = project_model.objects.create(name='ProjectTest')
    parameters = parameter_model.objects.bulk_create([
        parameter_model(project=project, group_name='GroupTest1', data='Name1'),
        parameter_model(project=project, group_name='GroupTest2', data='Name2'),
    ])

    test_plan = test_plan_model.objects.create(
        name='TestPlanTest',
        project=project,
        started_at=timezone.now(),
        due_date=timezone.now(),
    )

    test_plan.parameters.set(parameters)
    parameters_m2m = test_plan.parameters.all()

    assert isinstance(parameters_m2m, QuerySet)
    assert parameters_m2m[0].id == parameters[0].id
    assert parameters_m2m[1].id == parameters[1].id

    new_state = migrator.apply_tested_migration(
        ('tests_representation', '0010_added_updated_choices_to_tables'),
    )

    test_plan_model = new_state.apps.get_model('tests_representation', 'TestPlan')
    new_test_plan = test_plan_model.objects.first()
    parameters_list_id = [p.id for p in parameters]

    assert isinstance(new_test_plan.parameters, list)
    assert new_test_plan.parameters == parameters_list_id

    migrator.reset()


def test_username_caseinsesitive(migrator):
    old_state = migrator.apply_initial_migration(
        ('users', '0002_user_config'),
    )

    user_model = old_state.apps.get_model('users', 'User')

    for username in ['user', 'UsEr', 'USER']:
        user_model.objects.create(username=username, password='pass')

    new_state = migrator.apply_tested_migration(
        ('users', '0003_remove_ci_username_duplicates'),
    )

    user_model = new_state.apps.get_model('users', 'User')

    usernames = [user.username for user in user_model.objects.all()]
    assert len(usernames) == len({username.lower() for username in usernames})

    user = user_model(username='uSeR', password='pass')
    with pytest.raises(ValidationError):
        user.full_clean()

    migrator.reset()


def test_change_estimate_to_int(migrator):
    """Testing migrations 0008_added_estimate_tmp...0011_altered_estimate_tmp_field"""
    old_state = migrator.apply_initial_migration(
        ('tests_description', '0007_added_is_deleted_to_suite_cases'),
    )

    project_model = old_state.apps.get_model('core', 'Project')
    test_suite_model = old_state.apps.get_model('tests_description', 'TestSuite')
    test_case_model = old_state.apps.get_model('tests_description', 'TestCase')

    register(test_suite_model)

    project = project_model.objects.create(name='ProjectTest')
    suite = test_suite_model.objects.create(name='SuiteTest', project=project, lft=0, rght=0, tree_id=uuid4())
    test_case = test_case_model.objects.create(
        project=project,
        suite_id=suite.id,
        scenario='TestScenario',
        estimate=timezone.timedelta(days=1),
    )

    assert isinstance(test_case.estimate, timezone.timedelta)
    assert test_case.estimate == timezone.timedelta(days=1)

    new_state = migrator.apply_tested_migration(
        ('tests_description', '0012_alter_historicaltestcase_estimate'),
    )
    test_case_model = new_state.apps.get_model('tests_description', 'TestCase')
    new_test_case = test_case_model.objects.first()

    assert isinstance(new_test_case.estimate, int)
    assert new_test_case.estimate == WORKDAY_IN_SECONDS

    migrator.reset()


def test_rollback_change_estimate_to_int(migrator):
    """Testing rollback migrations 0008_added_estimate_tmp...0011_altered_estimate_tmp_field"""
    old_state = migrator.apply_initial_migration(
        ('tests_description', '0012_alter_historicaltestcase_estimate'),
    )

    project_model = old_state.apps.get_model('core', 'Project')
    test_suite_model = old_state.apps.get_model('tests_description', 'TestSuite')
    test_case_model = old_state.apps.get_model('tests_description', 'TestCase')

    register(test_suite_model)

    project = project_model.objects.create(name='ProjectTest')
    suite = test_suite_model.objects.create(name='SuiteTest', project=project, lft=0, rght=0, tree_id=uuid4())
    test_case = test_case_model.objects.create(
        project=project,
        suite_id=suite.id,
        scenario='TestScenario',
        estimate=WORKDAY_IN_SECONDS,
    )

    assert isinstance(test_case.estimate, int)
    assert test_case.estimate == WORKDAY_IN_SECONDS

    new_state = migrator.apply_tested_migration(
        ('tests_description', '0007_added_is_deleted_to_suite_cases'),
    )
    test_case_model = new_state.apps.get_model('tests_description', 'TestCase')
    new_test_case = test_case_model.objects.first()

    assert isinstance(new_test_case.estimate, timezone.timedelta)
    assert new_test_case.estimate == timezone.timedelta(days=1)

    migrator.reset()


def test_create_base_system_status(migrator):
    """Testing migration 0024_resultstatus"""
    old_state = migrator.apply_tested_migration(
        ('tests_representation', '0023_alter_historicaltestresult_status_and_more'),
    )

    with pytest.raises(LookupError):
        old_state.apps.get_model('tests_representation', 'ResultStatus')

    new_state = migrator.apply_tested_migration(
        ('tests_representation', '0024_resultstatus'),
    )

    status_model = new_state.apps.get_model('tests_representation', 'ResultStatus')
    base_statuses = status_model.objects.all()
    labels = {label.lower() for label in TestStatuses.labels if label != TestStatuses.UNTESTED.label}

    assert base_statuses.count() == len(labels)
    for status in base_statuses:
        assert status.name.lower() in labels and status.type == ResultStatusType.SYSTEM

    migrator.reset()


def test_change_result_status_to_fk(migrator):
    """
    Testing migrations 0025_historicaltestresult_status_temp_and_more...

    0028_rename_status_temp_historicaltestresult_status_and_more
    """
    old_state = migrator.apply_initial_migration(
        ('tests_representation', '0021_alter_parameter_unique_together_and_more'),
    )

    project_model = old_state.apps.get_model('core', 'Project')
    test_suite_model = old_state.apps.get_model('tests_description', 'TestSuite')
    test_case_model = old_state.apps.get_model('tests_description', 'TestCase')
    test_case_with_steps = old_state.apps.get_model('tests_description', 'TestCaseStep')
    test_plan_model = old_state.apps.get_model('tests_representation', 'TestPlan')
    test_model = old_state.apps.get_model('tests_representation', 'Test')
    test_result_model = old_state.apps.get_model('tests_representation', 'TestResult')
    test_step_result_model = old_state.apps.get_model('tests_representation', 'TestStepResult')

    register(test_suite_model)
    register(test_plan_model)

    project = project_model.objects.create(name='ProjectTest')
    suite = test_suite_model.objects.create(name='SuiteTest', project=project, lft=0, rght=0, tree_id=uuid4())
    test_case = test_case_model.objects.create(
        project=project,
        suite_id=suite.id,
        scenario='TestScenario',
    )
    test_case_with_steps = test_case_with_steps.objects.create(
        project=project,
        scenario='TestScenario',
    )
    test_plan = test_plan_model.objects.create(
        name='TestPlanTest',
        project=project,
        started_at=timezone.now(),
        due_date=timezone.now(),
    )
    test = test_model.objects.create(plan=test_plan, case=test_case, project=project)
    test_result = test_result_model.objects.create(test=test, project=project, status=TestStatuses.PASSED)
    test_result_with_untested = test_result_model.objects.create(
        test=test, project=project, status=TestStatuses.UNTESTED,
    )
    test_step_result = test_step_result_model.objects.create(
        project=project,
        step=test_case_with_steps,
        test_result=test_result,
        status=TestStatuses.PASSED,
    )

    assert isinstance(test_result.status, int) and test_result.status == TestStatuses.PASSED
    assert isinstance(test_step_result.status, int) and test_result.status == TestStatuses.PASSED
    assert (isinstance(test_result_with_untested.status, int)
            and test_result_with_untested.status == TestStatuses.UNTESTED
            )

    new_state = migrator.apply_tested_migration(
        ('tests_representation', '0028_rename_status_temp_historicaltestresult_status_and_more'),
    )
    test_result_model = new_state.apps.get_model('tests_representation', 'TestResult')
    test_step_result_model = new_state.apps.get_model('tests_representation', 'TestStepResult')
    status_model = new_state.apps.get_model('tests_representation', 'ResultStatus')
    test_result = test_result_model.objects.get(pk=test_result.pk)
    test_result_with_untested = test_result_model.objects.get(pk=test_result_with_untested.pk)
    test_step_result = test_step_result_model.objects.first()

    passed_status = status_model.objects.filter(
        name__iexact=TestStatuses.PASSED.label,
        type=ResultStatusType.SYSTEM,
    ).first()
    custom_untested = status_model.objects.filter(
        name__iexact='Ext-Untested',
        type=ResultStatusType.CUSTOM,
    ).first()

    assert isinstance(test_result.status, status_model) and test_result.status == passed_status
    assert isinstance(test_step_result.status, status_model) and test_step_result.status == passed_status
    assert (isinstance(test_result_with_untested.status, status_model)
            and test_result_with_untested.status == custom_untested
            )

    migrator.reset()


@pytest.mark.parametrize('status_type', (ResultStatusType.SYSTEM, ResultStatusType.CUSTOM))
def test_rollback_change_result_status_to_fk(migrator, status_type):
    """
    Testing rollback migrations 0023_alter_historicaltestresult_status_and_more...

    0028_rename_status_temp_historicaltestresult_status_and_more
    """
    old_state = migrator.apply_initial_migration(
        [
            ('tests_representation', '0028_rename_status_temp_historicaltestresult_status_and_more'),
            ('tests_description', '0016_alter_testsuite_level_alter_testsuite_lft_and_more'),
        ],
    )

    project_model = old_state.apps.get_model('core', 'Project')
    test_suite_model = old_state.apps.get_model('tests_description', 'TestSuite')
    test_suite_model._mptt_meta = MPTTMeta(root_node_ordering=False)
    test_case_model = old_state.apps.get_model('tests_description', 'TestCase')
    test_case_with_steps = old_state.apps.get_model('tests_description', 'TestCaseStep')
    test_plan_model = old_state.apps.get_model('tests_representation', 'TestPlan')
    test_plan_model._mptt_meta = MPTTMeta(root_node_ordering=False)
    test_model = old_state.apps.get_model('tests_representation', 'Test')
    test_result_model = old_state.apps.get_model('tests_representation', 'TestResult')
    test_step_result_model = old_state.apps.get_model('tests_representation', 'TestStepResult')
    status_model = old_state.apps.get_model('tests_representation', 'ResultStatus')

    register(test_suite_model)
    register(test_plan_model)

    project = project_model.objects.create(name='ProjectTest')
    suite = test_suite_model.objects.create(name='SuiteTest', project=project, lft=0, rght=0, tree_id=uuid4())
    test_case = test_case_model.objects.create(project=project, suite_id=suite.id, scenario='TestScenario')
    test_case_with_steps = test_case_with_steps.objects.create(project=project, scenario='TestScenario')
    test_plan = test_plan_model.objects.create(
        name='TestPlanTest',
        project=project,
        started_at=timezone.now(),
        due_date=timezone.now(),
    )
    test = test_model.objects.create(plan=test_plan, case=test_case, project=project)

    if status_type == ResultStatusType.SYSTEM:
        status = status_model.objects.filter(
            name__iexact=TestStatuses.PASSED.label,
            type=ResultStatusType.SYSTEM,
        ).first()
    else:
        status = status_model.objects.create(name=constants.STATUS_NAME, project=project)

    test_result = test_result_model.objects.create(test=test, project=project, status=status)
    test_step_result = test_step_result_model.objects.create(
        project=project,
        step=test_case_with_steps,
        test_result=test_result,
        status=status,
    )

    assert isinstance(test_result.status, status_model) and test_result.status == status
    assert isinstance(test_step_result.status, status_model) and test_step_result.status == status

    new_state = migrator.apply_tested_migration(
        ('tests_representation', '0023_alter_historicaltestresult_status_and_more'),
    )
    test_result_model = new_state.apps.get_model('tests_representation', 'TestResult')
    test_step_result_model = new_state.apps.get_model('tests_representation', 'TestStepResult')

    test_result = test_result_model.objects.first()
    test_step_result = test_step_result_model.objects.first()

    expected_status = TestStatuses.PASSED if status_type == ResultStatusType.SYSTEM else TestStatuses.ROLLBACKED

    assert isinstance(test_result.status, int) and test_result.status == expected_status
    assert isinstance(test_step_result.status, int) and test_step_result.status == expected_status

    migrator.reset()


def test_change_status_specific_choices_to_pk(migrator):
    """
    Testing migrations 0014_customattribute_status_specific_and_more...

    0020_rename_status_specific_temp_customattribute_status_specific
    """
    old_state = migrator.apply_initial_migration(
        ('core', '0014_customattribute_status_specific_and_more'),
    )

    project_model = old_state.apps.get_model('core', 'Project')
    custom_attribute_model = old_state.apps.get_model('core', 'CustomAttribute')
    project = project_model.objects.create(name='ProjectTest')
    custom_attribute = custom_attribute_model.objects.create(
        project=project,
        name='CustomAttributeTest',
        type=CustomFieldType.TXT,
        status_specific=[TestStatuses.PASSED, TestStatuses.FAILED],
        content_types=list(CustomAttributeSelector.get_allowed_content_types().values_list('id', flat=True)),
    )

    assert custom_attribute.status_specific == [TestStatuses.PASSED, TestStatuses.FAILED]

    new_state = migrator.apply_tested_migration(
        ('core', '0020_rename_status_specific_temp_customattribute_status_specific'),
    )
    custom_attribute_model = new_state.apps.get_model('core', 'CustomAttribute')
    status_model = new_state.apps.get_model('tests_representation', 'ResultStatus')
    custom_attribute = custom_attribute_model.objects.first()

    passed_status = status_model.objects.filter(
        name__iexact=TestStatuses.PASSED.label,
        type=ResultStatusType.SYSTEM,
    ).first()
    failed_status = status_model.objects.filter(
        name__iexact=TestStatuses.FAILED.label,
        type=ResultStatusType.SYSTEM,
    ).first()

    assert custom_attribute.status_specific == [passed_status.pk, failed_status.pk]
    migrator.reset()


def test_rollback_status_specific_to_choices(migrator):
    """
    Testing rollback migrations 0020_rename_status_specific_temp_customattribute_status_specific...

    0014_customattribute_status_specific_and_more
    """
    old_state = migrator.apply_initial_migration(
        ('core', '0020_rename_status_specific_temp_customattribute_status_specific'),
    )

    project_model = old_state.apps.get_model('core', 'Project')
    custom_attribute_model = old_state.apps.get_model('core', 'CustomAttribute')
    project = project_model.objects.create(name='ProjectTest')
    status_model = old_state.apps.get_model('tests_representation', 'ResultStatus')

    passed_status = status_model.objects.filter(
        name__iexact=TestStatuses.PASSED.label,
        type=ResultStatusType.SYSTEM,
    ).first()
    failed_status = status_model.objects.filter(
        name__iexact=TestStatuses.FAILED.label,
        type=ResultStatusType.SYSTEM,
    ).first()
    status_test = status_model.objects.create(project=project, name='StatusTest')

    custom_attribute = custom_attribute_model.objects.create(
        project=project,
        name='CustomAttributeTest',
        type=CustomFieldType.TXT,
        status_specific=[passed_status.pk, failed_status.pk, status_test.pk],
        content_types=list(CustomAttributeSelector.get_allowed_content_types().values_list('id', flat=True)),
    )

    assert custom_attribute.status_specific == [passed_status.pk, failed_status.pk, status_test.pk]

    new_state = migrator.apply_tested_migration(
        ('core', '0014_customattribute_status_specific_and_more'),
    )
    custom_attribute_model = new_state.apps.get_model('core', 'CustomAttribute')
    custom_attribute = custom_attribute_model.objects.first()

    assert custom_attribute.status_specific == [TestStatuses.PASSED, TestStatuses.FAILED]
    migrator.reset()


def test_change_custom_attributes_to_json(migrator):
    """
    Testing migrations 0024_customattribute_applied_to_and_more

    0026_remove_customattribute_content_types_and_more
    """
    old_state = migrator.apply_initial_migration(
        [
            ('core', '0024_customattribute_applied_to_and_more'),
        ],
    )

    project_model = old_state.apps.get_model('core', 'Project')
    custom_attribute_model = old_state.apps.get_model('core', 'CustomAttribute')
    test_suite_model = old_state.apps.get_model('tests_description', 'TestSuite')
    project = project_model.objects.create(name='ProjectTest')
    status_model = old_state.apps.get_model('tests_representation', 'ResultStatus')
    result_model = old_state.apps.get_model('tests_representation', 'testresult')
    ContentType.objects.get_for_model(result_model)
    first_status = status_model.objects.create(project=project, name='first_status')
    second_status = status_model.objects.create(project=project, name='second_status')
    status_ids = [first_status.pk, second_status.pk]
    ContentType.objects.get_for_model(status_model)
    test_suite = test_suite_model.objects.create(name='SuiteTest', project=project, tree_id=1, lft=0, rght=0, level=0)
    custom_attribute_model.objects.create(
        project=project,
        name='CustomAttributeTest',
        type=CustomFieldType.TXT,
        status_specific=status_ids,
        content_types=list(CustomAttributeSelector.get_allowed_content_types().values_list('id', flat=True)),
        is_suite_specific=True,
        suite_ids=[test_suite.pk],
        is_required=True,
    )
    custom_attribute = custom_attribute_model.objects.last()
    assert custom_attribute.status_specific == status_ids
    assert custom_attribute.suite_ids == [test_suite.pk]
    assert custom_attribute.is_required

    new_state = migrator.apply_tested_migration(
        ('core', '0026_remove_customattribute_content_types_and_more'),
    )

    custom_attribute_model = new_state.apps.get_model('core', 'CustomAttribute')
    custom_attribute = custom_attribute_model.objects.get(id=custom_attribute.id)
    assert custom_attribute.applied_to
    for ct_name in custom_attribute.applied_to.keys():
        assert custom_attribute.applied_to[ct_name]['is_required']
        assert custom_attribute.applied_to[ct_name]['suite_ids'] == [test_suite.pk]
        assert custom_attribute.applied_to[ct_name]['status_specific'] == status_ids
    migrator.reset()


def test_rollback_custom_attributes_from_json(migrator):
    """
    Testing rollback migrations 0024_customattribute_applied_to

    0026_remove_customattribute_content_types_and_more
    """
    old_state = migrator.apply_initial_migration(
        [
            ('core', '0026_remove_customattribute_content_types_and_more'),
        ],
    )

    project_model = old_state.apps.get_model('core', 'Project')
    custom_attribute_model = old_state.apps.get_model('core', 'CustomAttribute')
    test_suite_model = old_state.apps.get_model('tests_description', 'TestSuite')
    project = project_model.objects.create(name='ProjectTest')
    status_model = old_state.apps.get_model('tests_representation', 'ResultStatus')
    result_model = old_state.apps.get_model('tests_representation', 'testresult')
    ContentType.objects.get_for_model(result_model)
    first_status = status_model.objects.create(project=project, name='first_status')
    second_status = status_model.objects.create(project=project, name='second_status')
    case_model = old_state.apps.get_model('tests_description', 'TestCase')
    ContentType.objects.get_for_model(case_model)
    status_ids = [first_status.pk, second_status.pk]
    ContentType.objects.get_for_model(status_model)
    test_suite = test_suite_model.objects.create(name='SuiteTest', project=project, tree_id=1, lft=0, rght=0, level=0)
    is_required = True
    applied_to = {
        'testcase': {
            'is_required': is_required,
            'suite_ids': [test_suite.pk],
            'status_specific': status_ids,
        },
    }
    custom_attribute_model.objects.create(
        project=project,
        name='CustomAttributeTest',
        type=CustomFieldType.TXT,
        applied_to=applied_to,
    )
    custom_attribute = custom_attribute_model.objects.last()
    assert custom_attribute.applied_to == applied_to

    new_state = migrator.apply_tested_migration(
        ('core', '0024_customattribute_applied_to_and_more'),
    )

    custom_attribute_model = new_state.apps.get_model('core', 'CustomAttribute')
    custom_attribute = custom_attribute_model.objects.get(id=custom_attribute.id)
    assert custom_attribute.is_required is is_required
    assert custom_attribute.is_suite_specific
    assert custom_attribute.suite_ids == [test_suite.pk]
    assert custom_attribute.status_specific == status_ids
    ct_ids = list(ContentType.objects.filter(model='testcase').values_list('id', flat=True))
    assert custom_attribute.content_types == ct_ids
    migrator.reset()
