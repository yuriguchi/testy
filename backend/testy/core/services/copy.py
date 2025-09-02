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
import re
from collections import defaultdict
from copy import deepcopy
from typing import Any, Callable, Generator, Iterable, TypeAlias

from django.db import transaction
from django.db.models import Model, QuerySet
from mptt.querysets import TreeQuerySet
from simple_history.utils import bulk_create_with_history

from testy.core.models import Label, LabeledItem, Project
from testy.core.selectors.attachments import AttachmentSelector
from testy.core.selectors.labeled_items import LabeledItemSelector
from testy.core.selectors.labels import LabelSelector
from testy.tests_description.models import TestCase, TestCaseStep, TestSuite
from testy.tests_description.selectors.cases import TestCaseSelector, TestCaseStepSelector
from testy.tests_description.selectors.suites import TestSuiteSelector
from testy.tests_representation.models import Test, TestPlan
from testy.tests_representation.selectors.testplan import TestPlanSelector

_Mapping: TypeAlias = dict[int, int]
_PROJECT_ID = 'project_id'
_PK = 'pk'
_ID = 'id'
_TREE_ID = 'tree_id'
_NEW_NAME = 'new_name'
_TEST_CASE_ID = 'test_case_id'
_SCENARIO = 'scenario'
_EXPECTED = 'expected'


class CopyService:
    @classmethod
    @transaction.atomic
    def plans_copy(cls, payload: dict[str, Any]) -> QuerySet[Model]:
        dst_plan = payload.get('dst_plan')
        plans_mapping = {}
        for plan_details in payload['plans']:
            plan_to_copy = plan_details.get('plan')
            copied_objects_generator = cls._create_tree_objects(
                dst_plan,
                [plan_to_copy],
                TestPlan,
                name=plan_details.get(_NEW_NAME, plan_to_copy.name),
                started_at=plan_details.get('started_at', plan_to_copy.started_at),
                due_date=plan_details.get('due_date', plan_to_copy.due_date),
                finished_at=None,
            )
            mapping = {}
            for src_instance, cpy_instance in list(copied_objects_generator):
                cpy_instance.save()
                mapping[src_instance.pk] = cpy_instance.pk
            plans_mapping.update(mapping)

        tests_to_copy = Test.objects.filter(plan__in=plans_mapping.keys(), is_archive=False)
        mapped_fields = defaultdict(dict)

        for test in tests_to_copy:
            mapped_fields['plan_id'][test.pk] = plans_mapping.get(test.plan_id)
            mapped_fields['assignee_id'][test.pk] = test.assignee_id if payload.get('keep_assignee') else None
            mapped_fields['last_status'][test.pk] = None

        cls._copy_objects(tests_to_copy, Test, mapped_fields)
        cls._copy_attachments(
            TestPlan,
            list(plans_mapping.keys()),
            plans_mapping,
            None,
            ['description'],
            TestPlanSelector.plans_by_ids,
        )
        return TestPlanSelector.plans_by_ids(plans_mapping.values())

    @classmethod
    @transaction.atomic
    def suites_copy(cls, data: dict[str, Any]):  # noqa: WPS231, WPS210
        dst_suite_id = None
        project_data = {}
        if project := data.get('dst_project_id'):
            project_data = {_PROJECT_ID: project.id}
        if suite := data.get('dst_suite_id'):
            dst_suite_id = suite.id

        suite_ids = [suite.get(_ID) for suite in data.get('suites', [])]

        root_suites = TestSuiteSelector.suites_by_ids(suite_ids, _PK)
        root_suite_mappings, copied_root_suites = cls._copy_suites(
            root_suites,
            parent_id=dst_suite_id,
            **project_data,
        )

        suite_mappings, copied_bulk_suites = cls._copy_suites_bulk(
            root_suites.get_descendants(include_self=False),
            **project_data,
        )
        suite_mappings.update(root_suite_mappings)
        cls._update_suite_relations(copied_bulk_suites, suite_mappings)
        cases_to_copy = TestCaseSelector.cases_by_ids(
            root_suites.get_descendants(include_self=True).values_list(_ID, flat=True),
            'suite_id',
        )

        field_mappings = defaultdict(dict)
        for case in cases_to_copy:
            field_mappings['suite_id'][case.pk] = suite_mappings.get(case.suite_id)
            field_mappings['project_id'][case.pk] = project.id if project else case.project_id

        case_mappings = cls._copy_objects(
            cases_to_copy,
            TestCase,
            field_mappings,
        )

        steps_to_copy = TestCaseStepSelector.steps_by_ids_list(
            cases_to_copy.values_list(_ID, flat=True),
            _TEST_CASE_ID,
        )
        copied_cases = TestCaseSelector.cases_by_ids(case_mappings.values(), _PK)
        steps_mapping = cls._steps_copy(copied_cases, case_mappings, steps_to_copy, project)
        cls._copy_attachments(
            TestCase,
            cases_to_copy.values_list(_ID, flat=True),
            case_mappings,
            project_data.get(_PROJECT_ID),
            ['setup', _SCENARIO, _EXPECTED, 'teardown', 'description'],
            TestCaseSelector.cases_by_ids,
        )
        cls._copy_attachments(
            TestCaseStep,
            steps_to_copy.values_list(_ID, flat=True),
            steps_mapping,
            project_data.get(_PROJECT_ID),
            [_SCENARIO, _EXPECTED],
            TestCaseStepSelector.steps_by_ids_list,
        )
        labeled_cases = LabeledItemSelector.items_list_by_ids(
            cases_to_copy.values_list(_ID, flat=True),
            TestCase,
        )

        cls._copy_labels_and_items(labeled_cases, case_mappings, project_data.get(_PROJECT_ID))
        for suite_dict in data.get('suites', []):
            if suite_dict.get(_NEW_NAME) is None:
                continue
            copied_suite_id = root_suite_mappings.get(suite_dict.get(_ID))
            TestSuite.objects.filter(pk=copied_suite_id).update(name=suite_dict.get(_NEW_NAME))
        return copied_root_suites.all()

    @classmethod
    @transaction.atomic
    def cases_copy(cls, data: dict[str, Any]):
        cases_data = data.get('cases', [])

        case_ids = []
        pk_to_new_name = {}
        mapped_fields = defaultdict(dict)

        for case in cases_data:
            case_ids.append(case.get(_ID))
            if new_name := case.get(_NEW_NAME):
                pk_to_new_name[case.get(_ID)] = new_name

        cases_to_copy = TestCaseSelector.cases_by_ids(case_ids, _PK)
        dst_suite = data.get('dst_suite_id')
        for case in cases_to_copy:
            mapped_fields['suite_id'][case.id] = dst_suite.pk if dst_suite else case.suite_id
            mapped_fields['name'][case.id] = pk_to_new_name.get(case.id, case.name)

        case_mappings = cls._copy_objects(
            cases_to_copy,
            TestCase,
            custom_fields=mapped_fields,
        )

        steps_to_copy = TestCaseStepSelector.steps_by_ids_list(
            case_ids,
            _TEST_CASE_ID,
        )

        copied_cases = TestCaseSelector.cases_by_ids(case_mappings.values(), _PK)
        steps_mapping = cls._steps_copy(copied_cases, case_mappings, steps_to_copy)

        cls._copy_attachments(
            TestCase,
            case_ids,
            case_mappings,
            None,
            ['setup', _SCENARIO, _EXPECTED, 'teardown', 'description'],
            TestCaseSelector.cases_by_ids,
        )
        cls._copy_attachments(
            TestCaseStep,
            steps_to_copy.values_list(_ID, flat=True),
            steps_mapping,
            None,
            [_SCENARIO, _EXPECTED],
            TestCaseStepSelector.steps_by_ids_list,
        )
        labeled_cases = LabeledItemSelector.items_list_by_ids(case_ids, TestCase)
        project_id = dst_suite.project_id if dst_suite else None
        cls._copy_labels_and_items(labeled_cases, case_mappings, project_id)
        return TestCaseSelector.cases_by_ids(case_mappings.values(), _PK)

    @classmethod
    def _copy_suites(
        cls,
        suites: QuerySet[TestSuite],
        **kwargs,
    ) -> tuple[_Mapping, TreeQuerySet[TestSuite]]:
        suite_mappings = {}
        copied_suites = []
        copied_suites_ids = []
        for suite in suites:
            copied_suite = deepcopy(suite)
            copied_suite.pk = None
            for field_name, field_value in kwargs.items():
                setattr(copied_suite, field_name, field_value)
            if parent_id := suite_mappings.get(copied_suite.parent_id):
                copied_suite.parent_id = parent_id
            copied_suite.save()
            copied_suites.append(copied_suite)
            copied_suites_ids.append(copied_suite.id)
            suite_mappings[suite.id] = copied_suite.id
        new_suites = TestSuiteSelector.suites_by_ids(copied_suites_ids, _PK)
        return suite_mappings, new_suites

    @classmethod
    def _copy_suites_bulk(
        cls,
        suites: TreeQuerySet[TestSuite],
        **kwargs,
    ) -> tuple[_Mapping, list[TestSuite]]:
        copied_suites = []
        for suite in suites:
            copied_suite = deepcopy(suite)
            copied_suite.pk = None
            for field_name, field_value in kwargs.items():
                setattr(copied_suite, field_name, field_value)
            copied_suites.append(copied_suite)
        new_suites = TestSuite.objects.bulk_create(copied_suites)
        resulting_mapping = cls._map_ids(suites, new_suites)
        return resulting_mapping, new_suites

    @classmethod
    def _update_suite_relations(
        cls,
        suites: list[TestSuite] | TreeQuerySet[TestSuite],
        suite_mappings: _Mapping,
    ) -> list[TestSuite]:
        updated_instances = []
        for suite in suites:
            if suite.parent_id:
                suite.parent_id = suite_mappings.get(suite.parent_id)
            updated_instances.append(suite)
        fields_to_update = ['parent_id']
        TestSuite.objects.bulk_update(
            updated_instances,
            fields_to_update,
        )
        return updated_instances

    @classmethod
    def _copy_labels_and_items(
        cls,
        labeled_items: QuerySet[LabeledItem],
        mapping: _Mapping,
        project_id: int | None,
    ) -> _Mapping:
        labels = LabelSelector.label_list_by_ids(
            labeled_items.values_list('label_id', flat=True),
            _PK,
        )
        label_mappings = {}
        for label in labels:
            filter_conditions = {}
            default = {'name': label.name, 'user_id': label.user_id}
            if project_id:
                default[_PROJECT_ID] = project_id
            new_label, _ = Label.objects.get_or_create(
                name__iexact=label.name,
                type=label.type,
                project_id=project_id or label.project_id,
                defaults=default,
                **filter_conditions,
            )
            label_mappings[label.id] = new_label.id

        copied_labeled_items = []
        for labeled_item in labeled_items:
            labeled_item_copy = deepcopy(labeled_item)
            labeled_item_copy.pk = None
            labeled_item_copy.label_id = label_mappings.get(labeled_item_copy.label_id)
            labeled_item_copy.object_id = mapping.get(labeled_item_copy.object_id)
            labeled_item_copy.content_object_history_id = labeled_item_copy.content_object.history.first().history_id
            copied_labeled_items.append(labeled_item_copy)
        LabeledItem.objects.bulk_create(copied_labeled_items)
        return label_mappings

    @classmethod
    def _create_tree_objects(
        cls,
        new_parent: Model | None,
        instances: Iterable[Model],
        model: type[Model],
        parent_field_name: str = 'parent',
        **kwargs,
    ) -> Generator[tuple[int, int], None, None]:
        inherited_attrs = {'started_at', 'due_date', 'finished_at'}
        for instance in instances:
            copied_instance = deepcopy(instance)
            copied_instance.pk = None
            setattr(copied_instance, parent_field_name, new_parent)
            for field_name, field_value in kwargs.items():
                setattr(copied_instance, field_name, field_value)
            child_instances = list(model.objects.filter(**{parent_field_name: instance.pk}))
            yield instance, copied_instance
            yield from cls._create_tree_objects(
                copied_instance,
                child_instances,
                model,
                parent_field_name,
                **{key: value for key, value in kwargs.items() if key in inherited_attrs},
            )

    @classmethod
    def _copy_attachments(
        cls,
        model: type[Model],
        obj_ids: list[int],
        mapping: _Mapping,
        project_id: int | None,
        attachment_references_fields: list[str],
        selector_method: Callable[[list[int], str], QuerySet[Any]],
    ) -> None:
        attachments = AttachmentSelector.attachment_list_by_ids(obj_ids, model)
        attachments_mapping = {}
        for attachment in attachments:
            attrs_to_change = {'object_id': mapping.get(attachment.object_id)}
            if project_id:
                attrs_to_change[_PROJECT_ID] = project_id
            attachments_mapping[attachment.id] = attachment.model_clone(common_attrs_to_change=attrs_to_change).id
        updated_objs = []
        objs_to_update = selector_method(list(mapping.values()), _PK)
        for obj in objs_to_update.filter(attachments__isnull=False):
            for field_name in attachment_references_fields:
                for old_id, new_id in attachments_mapping.items():
                    formatted_text = cls._change_attachments_reference(
                        getattr(obj, field_name), old_id, new_id,
                    )
                    setattr(obj, field_name, formatted_text)
            updated_objs.append(obj)
        model.objects.bulk_update(updated_objs, attachment_references_fields)

    @classmethod
    def _copy_objects(
        cls,
        objs_to_copy: Iterable[Model],
        model: type[Model],
        custom_fields: dict[str, dict[int, Any]] | None = None,
    ) -> _Mapping:
        copied_instances = []
        if not custom_fields:
            custom_fields = {}
        for instance in objs_to_copy:
            copied_instance = deepcopy(instance)
            for field_name, mapping in custom_fields.items():
                setattr(copied_instance, field_name, mapping.get(copied_instance.pk))
            copied_instance.pk = None
            copied_instances.append(copied_instance)
        if getattr(model, 'history', None):
            copied_instances = bulk_create_with_history(copied_instances, model)
        else:
            copied_instances = model.objects.bulk_create(copied_instances)
        return cls._map_ids(objs_to_copy, copied_instances)

    @classmethod
    def _map_ids(
        cls,
        key_objs: Iterable[Any],
        value_objs: Iterable[Any],
        *,
        mapping_key: str = _ID,
        mapping_key_objs: str = _ID,
    ) -> _Mapping:
        mapping = {}
        for key_obj, value_obj in zip(key_objs, value_objs):
            mapping[getattr(key_obj, mapping_key)] = getattr(value_obj, mapping_key_objs)
        return mapping

    @classmethod
    def _change_attachments_reference(cls, src_text: str, old_id: int, new_id: int) -> str:
        return re.sub(f'attachments/{old_id}/', f'attachments/{new_id}/', src_text)

    @classmethod
    def _steps_copy(
        cls,
        copied_cases: QuerySet[TestCase],
        case_mappings: _Mapping,
        steps_to_copy: QuerySet[TestCaseStep],
        project: Project | None = None,
    ):
        pk_to_copied_case_history = {}
        for copied_case in copied_cases:
            pk_to_copied_case_history[copied_case.id] = copied_case.history.first().history_id

        mapped_fields = defaultdict(dict)
        for step in steps_to_copy:
            mapped_fields['test_case_history_id'][step.pk] = pk_to_copied_case_history.get(
                case_mappings[step.test_case_id],
            )
            mapped_fields[_TEST_CASE_ID][step.pk] = case_mappings.get(step.test_case_id)
            mapped_fields['project_id'][step.pk] = project.id if project else step.project_id
        return cls._copy_objects(
            steps_to_copy,
            TestCaseStep,
            custom_fields=mapped_fields,
        )
