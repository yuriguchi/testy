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
from django.db.models import Count

from tests import constants
from tests.commons import RequestMock
from testy.tests_representation.models import Test
from testy.utilities.request import get_boolean
from testy.utilities.tree import form_tree_prefetch_lookups, form_tree_prefetch_objects

_TREEVIEW = 'treeview'


class TestTestyUtilities:

    def test_get_boolean(self):
        request = RequestMock()
        valid_positive_yes = ['1', 'yes', 'true', 'True', 'YES', 1, 'TRue']
        invalid_yes = ['2', '0', 'ye', 'y', 't', 'truee', 0, '']
        for option in valid_positive_yes:
            request.GET = {_TREEVIEW: option}
            assert get_boolean(request, _TREEVIEW), f'Valid option "{option}" was recognised as invalid.'
        for option in invalid_yes:
            request.GET = {_TREEVIEW: option}
            assert not get_boolean(request, _TREEVIEW), f'Invalid option "{option}" was recognised as valid.'

    def test_form_tree_prefetch_lookups(self):
        tree_depth = 4
        nested_prefetch_field = 'child_instance'
        prefetch_field = 'parameter'
        result_list = form_tree_prefetch_lookups(nested_prefetch_field, prefetch_field, tree_depth)
        assert len(result_list) == tree_depth + 1  # plus one is for root level
        for idx, result in enumerate(result_list):
            assert result.count(nested_prefetch_field) == idx, 'Nested prefetch is not with expected depth'
            assert result.count(prefetch_field) == 1, 'Field that is being prefetched should be prefetched on every lvl'

    @pytest.mark.django_db
    def test_form_tree_prefetch_objects(self, test_factory, test_result_factory):
        tree_depth = 4
        number_of_results = 3
        nested_prefetch_field = 'child_instance'
        prefetch_field = 'parameter'
        prefetch_lookups = form_tree_prefetch_lookups(nested_prefetch_field, prefetch_field, tree_depth)
        archived_ids = []
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            if idx % 2 == 0:
                test = test_factory(is_archive=True)
                for _ in range(number_of_results):
                    test_result_factory(test=test)
                archived_ids.append(test.id)
            else:
                test_factory(is_archive=False)
        archived_ids.reverse()
        prefetches = form_tree_prefetch_objects(
            nested_prefetch_field=nested_prefetch_field,
            prefetch_field=prefetch_field,
            tree_depth=tree_depth,
            queryset_class=Test,
            queryset_filter={'is_archive': True},
            order_by_fields=['-id'],
            annotation={'results_count': Count('results')},
        )
        for prefetch, prefetch_lookup in zip(prefetches, prefetch_lookups):
            assert len(prefetch.queryset) == constants.NUMBER_OF_OBJECTS_TO_CREATE / 2, 'Number of objects in ' \
                                                                                        'queryset is incorrect'
            assert prefetch.prefetch_through == prefetch_lookup, 'Expected lookup was not in prefetch object'
            assert archived_ids == [prefetch_object.id for prefetch_object in prefetch.queryset], 'Ordering was ' \
                                                                                                  'not applied'
            for instance in prefetch.queryset:
                assert instance.results_count == number_of_results, 'Annotation did not work properly'
