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
from collections import defaultdict

import allure
import pytest

from testy.root.ltree.querysets import LtreeQuerySet
from testy.tests_representation.models import TestPlan


@pytest.mark.django_db
class TestLtree:

    @allure.title('Test new tree_ids are generated per root')
    def test_tree_ids(self, test_plan_factory, project):
        roots = [test_plan_factory(project=project) for _ in range(3)]
        for root in roots:
            root.refresh_from_db()
        tree_ids = {root.tree_id for root in roots}
        with allure.step('Validate number of roots matches number of tree ids'):
            assert len(roots) == len(tree_ids)

    @allure.title('Test get_descendants')
    @pytest.mark.parametrize('include_self', [True, False], ids=['include self enabled', 'include self disabled'])
    @pytest.mark.parametrize(
        'by_instance',
        [True, False],
        ids=['get_descendants from instance', 'get_descendants from queryset'],
    )
    def test_get_descendants(self, test_plan_factory, project, include_self, by_instance):
        expected_descendants_count = 5
        roots = [test_plan_factory(project=project), test_plan_factory(project=project)]
        root_pk_to_descendants = defaultdict(list)
        for root in roots:
            if include_self:
                root_pk_to_descendants[root.pk].append(root)
            parent = root
            for _ in range(expected_descendants_count):
                parent = test_plan_factory(parent=parent)
                assert root.tree_id == parent.tree_id
                root_pk_to_descendants[root.pk].append(parent)
        if include_self:
            expected_descendants_count += 1

        for root in roots:
            root.refresh_from_db()
            if by_instance:
                descendants = root.get_descendants(include_self=include_self)
            else:
                descendants = TestPlan.objects.filter(pk=root.pk).get_descendants(include_self=include_self)
            assert isinstance(descendants, LtreeQuerySet)
            assert descendants.count() == expected_descendants_count
            assert list(descendants) == root_pk_to_descendants[root.pk]
            assert TestPlan.objects.filter(tree_id=root.tree_id).count() == 6

    @allure.title('Test get_descendants by multiple instances in queryset')
    @pytest.mark.parametrize('include_self', [True, False], ids=['include self enabled', 'include self disabled'])
    def test_get_descendants_multiple_instances_qs(self, test_plan_factory, project, include_self):
        expected_descendants_count = 5
        expected_list = []
        roots = [test_plan_factory(project=project), test_plan_factory(project=project)]
        for root in roots:
            if include_self:
                expected_list.append(root)
            parent = root
            for _ in range(expected_descendants_count):
                parent = test_plan_factory(parent=parent)
                expected_list.append(parent)
        if include_self:
            expected_descendants_count += 1

        descendants = TestPlan.objects.filter(pk__in=[root.pk for root in roots]).get_descendants(
            include_self=include_self,
        )
        assert isinstance(descendants, LtreeQuerySet)
        assert descendants.count() == expected_descendants_count * 2
        assert list(descendants) == expected_list

    @allure.title('Test get_descendants does not pick up ancestors')
    def test_get_descendants_only(self, test_plan_factory, project):
        expected_descendants_count = 5
        root = test_plan_factory(project=project)
        child = test_plan_factory(project=project, parent=root)
        expected_list = []
        parent = child
        for _ in range(expected_descendants_count):
            parent = test_plan_factory(parent=parent)
            expected_list.append(parent)
        child.refresh_from_db()
        descendants = child.get_descendants(include_self=False)
        assert isinstance(descendants, LtreeQuerySet)
        assert descendants.count() == expected_descendants_count
        assert list(descendants) == expected_list
        assert not descendants.filter(pk=root.pk).exists()

    @allure.title('Test get_ancestors')
    @pytest.mark.parametrize('include_self', [True, False], ids=['include self enabled', 'include self disabled'])
    @pytest.mark.parametrize(
        'by_instance',
        [True, False],
        ids=['get_ancestors from instance', 'get_ancestors from queryset'],
    )
    def test_get_ancestors(self, test_plan_factory, project, include_self, by_instance):
        expected_ancestors_count = 5
        deepest_nodes = []
        pk_to_ancestors = {}
        for root in [test_plan_factory(project=project), test_plan_factory(project=project)]:
            expected = [root]
            parent = root
            for idx in range(expected_ancestors_count):
                parent = test_plan_factory(parent=parent)
                assert root.tree_id == parent.tree_id
                if not include_self and idx == expected_ancestors_count - 1:
                    continue
                expected.append(parent)
            deepest_nodes.append(parent)
            pk_to_ancestors[parent.pk] = expected

        if include_self:
            expected_ancestors_count += 1

        for node in deepest_nodes:
            node.refresh_from_db()
            if by_instance:
                ancestors = node.get_ancestors(include_self=include_self)
            else:
                ancestors = TestPlan.objects.filter(pk=node.pk).get_ancestors(include_self=include_self)
            assert isinstance(ancestors, LtreeQuerySet)
            assert ancestors.count() == expected_ancestors_count
            assert list(ancestors) == pk_to_ancestors[node.pk]
            assert TestPlan.objects.filter(tree_id=node.tree_id).count() == 6

    @allure.title('Test get_ancestors by multiple instances in queryset')
    @pytest.mark.parametrize('include_self', [True, False], ids=['include self enabled', 'include self disabled'])
    def test_get_ancestors_by_multiple_instances_qs(self, test_plan_factory, project, include_self):
        expected_ancestors_count = 5
        deepest_nodes = []
        expected_list = []
        for root in [test_plan_factory(project=project), test_plan_factory(project=project)]:
            parent = root
            expected_list.append(root)
            for idx in range(expected_ancestors_count):
                parent = test_plan_factory(parent=parent)
                if not include_self and idx == expected_ancestors_count - 1:
                    continue
                expected_list.append(parent)
            deepest_nodes.append(parent)

        if include_self:
            expected_ancestors_count += 1

        ancestors = TestPlan.objects.filter(pk__in=[node.pk for node in deepest_nodes]).get_ancestors(
            include_self=include_self,
        )
        assert isinstance(ancestors, LtreeQuerySet)
        assert ancestors.count() == expected_ancestors_count * 2
        assert list(ancestors) == expected_list

    @allure.title('Test get_ancestors does not pick up descendants')
    def test_get_ancestors_only(self, test_plan_factory, project):
        root = test_plan_factory(project=project)
        child = test_plan_factory(project=project, parent=root)
        ancestor = test_plan_factory(project=project, parent=child)
        child.refresh_from_db()
        ancestors = child.get_ancestors(include_self=False)
        assert isinstance(ancestors, LtreeQuerySet)
        assert ancestors.count() == 1
        assert list(ancestors) == [root]
        assert ancestor not in list(ancestors)
