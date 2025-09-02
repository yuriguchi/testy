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
from django.db.models import IntegerChoices, TextChoices


class RoleTypes(IntegerChoices):
    SYSTEM = 0, 'System'
    CUSTOM = 1, 'Custom'
    SUPERUSER_ONLY = 3, 'Superuser Only'


class UserAllowedPermissionCodenames(TextChoices):
    CHANGE_PROJECT = 'change_project', 'User can modify project'
    VIEW_PROJECT = 'view_project', 'User can view project'
    CHANGE_CASE = 'change_testcase', 'User can modify test case'
    CHANGE_SUITE = 'change_testsuite', 'User can modify test suite'
    CHANGE_PLAN = 'change_testplan', 'User can modify test plan'
    CHANGE_RESULT = 'change_testresult', 'User can change test results inside project'
    ADD_PLAN = 'add_testplan', 'User can add test plan'
    ADD_SUITE = 'add_testsuite', 'User can add test suite'
    ADD_CASE = 'add_testcase', 'User can add test case'
    ADD_ROLE = 'add_role', 'User can add new roles inside project'
    ADD_RESULT = 'add_testresult', 'User can add test results inside project'
    DELETE_PLAN = 'delete_testplan', 'User can delete test plan'
    DELETE_SUITE = 'delete_testsuite', 'User can delete test suite'
    DELETE_CASE = 'delete_testcase', 'User can delete test case'
    DELETE_PROJECT = 'delete_project', 'User can delete project case'
    DELETE_RESULT = 'delete_testresult', 'User can delete project case'
    ADD_LABEL = 'add_label', 'User can add labels'
    CHANGE_LABEL = 'change_label', 'User can change labels'
    DELETE_LABEL = 'delete_label', 'User can delete labels'
    VIEW_PROJECT_RESTRICTION = 'project_restricted', 'User can only see projects he is a member of'
    ADD_STATUS = 'add_resultstatus', 'User can add status'
    CHANGE_STATUS = 'change_resultstatus', 'User can change status'
    DELETE_STATUS = 'delete_resultstatus', 'User can delete status'
