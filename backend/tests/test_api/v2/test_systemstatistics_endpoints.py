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

from tests import constants


@pytest.mark.django_db
class TestStatisticsEndpoints:
    view_name_statistics = 'api:v2:system-statistics'

    def test_statistics(
        self,
        api_client,
        authorized_superuser,
        project_factory,
        test_suite_factory,
        test_case_factory,
        test_plan_factory,
    ):
        expected_statistic = {
            'projects_count': constants.NUMBER_OF_OBJECTS_TO_CREATE,
            'cases_count': constants.NUMBER_OF_OBJECTS_TO_CREATE ** 3,
            'plans_count': constants.NUMBER_OF_OBJECTS_TO_CREATE // 2,
            'suites_count': constants.NUMBER_OF_OBJECTS_TO_CREATE ** 2,
            'tests_count': 0,
        }
        for idx in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            project = project_factory()
            is_archive = idx % 2
            test_plan_factory(project=project, is_archive=is_archive)
            for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
                suite = test_suite_factory(project=project)

                for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
                    test_case_factory(project=project, suite=suite)

        response = api_client.send_request(self.view_name_statistics)
        for count_name, count_value in response.json().items():
            assert count_value == expected_statistic[count_name]
