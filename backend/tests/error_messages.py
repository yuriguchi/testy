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

NOT_NULL_ERR_MSG = 'null value in column "{column}" of relation "{relation}" violates not-null constraint'
CHAR_LENGTH_ERR_MSG = 'value too long for type character varying(255)\n'
ALREADY_EXISTS_ERR_MSG = 'Key ({column_name})=({column_value}) already exists.'
INVALID_EMAIL_MSG = 'Enter a valid email address.'
UNAUTHORIZED_MSG = 'Authentication credentials were not provided.'
REQUIRED_FIELD_MSG = 'This field is required.'
BOOL_VALUE_ERR_MSG = '“{value}” value must be either True or False.'
MODEL_VALUE_ERR_MSG = 'Cannot assign "\'{value}\'": "{model_name}.{column_name}" must be a "{column_model}" instance.'
INT_VALUE_ERR_MSG = "Field '{column}' expected a number but got '{value}'."
ARRAY_VALUE_ERR_MSG = 'Array value must start with "{" or dimension information.'
TYPE_ERR_MSG = 'expected string or bytes-like object'
PERMISSION_ERR_MSG = 'You do not have permission to perform this action.'
NEGATIVE_ESTIMATE_ERR_MSG = 'Estimate value cannot be negative.'
INVALID_ESTIMATE_ERR_MSG = 'Invalid estimate format.'
TOO_BIG_ESTIMATE_ERR_MSG = 'Estimate value is too big.'
WEEK_ESTIMATE_ERR_MSG = 'Max estimate period is a day'
USERNAME_ALREADY_EXISTS = 'A user with that username already exists.'
CASE_INSENSITIVE_USERNAME_ALREADY_EXISTS = 'A user with that username in a different letter case already exists.'
DUPLICATE_LABEL_ERR_MSG = 'Label name "{0}" clashes with already existing label name "{1}" in project {2}.'
DUPLICATE_CUSTOM_ATTRIBUTE_ERR_MSG = (
    'Custom attribute name "{0}" clashes with already existing custom attribute '
    'name "{1}" in project {2}.'
)
EMPTY_SUITES_WHILE_SUITE_SPECIFIC_ERR_MSG = 'Empty suites list, while attribute is suite-specific'
FILLED_SUITES_WHILE_NOT_SUITE_SPECIFIC_ERR_MSG = 'Provided suites list, while attribute is not suite-specific'
SUITE_IDS_CONTAINS_NOT_RELATED_ITEMS = 'Field suite_ids contains non project-related items'
DATE_RANGE_ERROR = 'End date must be greater than start date.'
FORBIDDEN_USER_TEST_CASE = 'Only author of latest change can skip version'
EMPTY_COMMENT = 'Comment cannot be empty'
MISSING_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG = 'Missing following required attributes: {0}'
FOUND_EMPTY_REQUIRED_CUSTOM_ATTRIBUTES_ERR_MSG = 'Found empty required attributes: {0}'
CREATE_RESULT_IN_ARCHIVE_TEST = 'Cannot create a result in an archived test'
UPDATE_ARCHIVE_RESULT = 'Cannot update result in an archived test/archived result'
ATTRIBUTES_PARAMETER_NOT_PASSED = 'Attribute parameters are not passed'
RESULTS_ARE_NOT_EDITABLE = 'Results in this project are not editable. Contact with project admin'
SHORT_PASS = 'This password is too short. It must contain at least 8 characters.'
UPPERCASE_PASS = 'Password must have at least one uppercase character.'
LOWERCASE_PASS = 'Password must have at least one lowercase character.'
DIGIT_PASS = 'Password must have at least one digit.'
SPECIAL_SYMB_PASS = 'Password must have at least one special character.'
DUPLICATE_STATUS_ERR_MSG = 'Status name "{0}" clashes with already existing status name "{1}" in project {2}.'
