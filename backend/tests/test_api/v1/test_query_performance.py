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
from unittest import mock

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from tests import constants


@pytest.mark.django_db
class TestNumberOfQueries:
    max_num_of_queries = 35
    max_num_of_queries_detailed = 20

    # TODO: add separated more complex tests to catch n+1 for nested objects
    @pytest.mark.parametrize(
        'model_name, treeview_exists, factory_name',
        [
            ('test', False, 'test_factory'),
            ('testplan', True, 'test_plan_factory'),
            ('testsuite', True, 'test_suite_factory'),
            ('testcase', False, 'test_case_factory'),
            ('user', False, 'user_factory'),
            ('parameter', False, 'parameter_factory'),
        ],
    )
    def test_list_views_queries_num(
        self,
        request,
        authorized_superuser_client,
        project,
        model_name,
        treeview_exists,
        factory_name,
    ):
        err_msg = 'Number of queries increased for {model_name}, treeview {treeview_state}, look for n+1'
        view_name_list = f'api:v1:{model_name}-list'
        factory = request.getfixturevalue(factory_name)
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            factory(project=project)

        query_params = {
            'project': project.id,
        }
        for treeview in range(2 if treeview_exists else 1):
            with CaptureQueriesContext(connection) as context:
                authorized_superuser_client.send_request(view_name_list, query_params=query_params)
                num_of_queries_initial = len(context.captured_queries)
            factory(project=project)

            with CaptureQueriesContext(connection) as context:
                authorized_superuser_client.send_request(view_name_list, query_params=query_params)
                num_of_queries_after = len(context.captured_queries)

            assert num_of_queries_initial >= num_of_queries_after, err_msg.format(
                model_name=model_name,
                treeview_state='enabled' if treeview else 'disabled',
            )

    def test_number_of_queries_projects(self, authorized_superuser_client, project_factory):
        for _ in range(constants.NUMBER_OF_OBJECTS_TO_CREATE):
            project_factory()
        view_name_list = constants.LIST_VIEW_NAMES['project']
        with CaptureQueriesContext(connection) as context:
            authorized_superuser_client.send_request(view_name_list)
            num_of_queries_initial = len(context.captured_queries)
        project_factory()
        with CaptureQueriesContext(connection) as context:
            authorized_superuser_client.send_request(view_name_list)
            num_of_queries_after = len(context.captured_queries)
        assert num_of_queries_initial == num_of_queries_after, 'Number of queries increased, look for n+1'

    @pytest.mark.django_db(reset_sequences=True)
    def test_detail_views_queries_num(self, api_client, authorized_superuser, generate_objects):
        for view_name in constants.DETAIL_VIEW_NAMES.values():
            with CaptureQueriesContext(connection) as context:
                api_client.send_request(view_name, reverse_kwargs={'pk': 1})
                num_of_queries = len(context.captured_queries)
                assert num_of_queries <= self.max_num_of_queries_detailed, f'Number of queries in {view_name} ' \
                                                                           f'is exceeding allowed maximum.\n' \
                                                                           f'Number of queries: "{num_of_queries}"'

    @pytest.mark.skip('Increase queries for speed up statistic')
    def test_project_progress_queries(
        self, api_client, project, authorized_superuser, test_factory,
        test_result_factory, test_plan_factory,
    ):
        plan = test_plan_factory(project=project, parent=test_plan_factory(project=project))
        with mock.patch(
            'django.utils.timezone.now',
            return_value=timezone.make_aware(timezone.datetime(2000, 1, 2), timezone.utc),
        ):
            for _ in range(5):
                test_result_factory(test=test_factory(plan=plan), project=project)

        start, end = timezone.datetime(2000, 1, 1), timezone.datetime(2000, 1, 3)

        with CaptureQueriesContext(connection) as context:
            api_client.send_request(
                'api:v1:project-progress',
                reverse_kwargs={'pk': project.pk},
                query_params={
                    'start_date': start.isoformat(),
                    'end_date': end.isoformat(),
                },
            )
            first_num_of_queries = len(context.captured_queries)
        plan = test_plan_factory(project=project, parent=test_plan_factory(project=project))
        with mock.patch(
            'django.utils.timezone.now',
            return_value=timezone.make_aware(timezone.datetime(2000, 1, 2), timezone.utc),
        ):
            for _ in range(5):
                test_result_factory(test=test_factory(plan=plan), project=project)
        with CaptureQueriesContext(connection) as context:
            api_client.send_request(
                'api:v1:project-progress',
                reverse_kwargs={'pk': project.pk},
                query_params={
                    'start_date': start.isoformat(),
                    'end_date': end.isoformat(),
                },
            )
            second_num_of_queries = len(context.captured_queries)
        assert first_num_of_queries == second_num_of_queries, 'Number of queries grew with more instances'
        assert self.max_num_of_queries >= second_num_of_queries
