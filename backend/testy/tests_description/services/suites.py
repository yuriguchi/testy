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
from typing import Any

from django.db.models import QuerySet

from testy.core.models import CustomAttribute
from testy.tests_description.models import TestSuite


class TestSuiteService:
    non_side_effect_fields = ['parent', 'project', 'name', 'description', 'attributes']

    def suite_create(self, data: dict[str, Any]) -> TestSuite:
        return TestSuite.model_create(
            fields=self.non_side_effect_fields,
            data=data,
        )

    def suite_update(self, suite: TestSuite, data: dict[str, Any]) -> TestSuite:
        suite, _ = suite.model_update(
            fields=self.non_side_effect_fields,
            data=data,
        )
        return suite

    @classmethod
    def unlink_custom_attributes(cls, suites: QuerySet[TestSuite]) -> None:
        ids = list(suites.values_list('id', flat=True))
        attributes_to_update = []
        for content_type in ('testcase', 'testresult'):
            attributes = CustomAttribute.objects.filter(
                **{f'applied_to__{content_type}__suite_ids__overlap': ids},
            )
            for attribute in attributes:
                suite_ids = attribute.applied_to[content_type]['suite_ids']
                attribute.applied_to[content_type]['suite_ids'] = list(
                    set(suite_ids) - set(ids),
                )
                attributes_to_update.append(attribute)
            CustomAttribute.objects.bulk_update(attributes_to_update, fields=['applied_to'])
