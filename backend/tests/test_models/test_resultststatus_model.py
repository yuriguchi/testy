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
from django.db import IntegrityError

from tests.error_messages import INT_VALUE_ERR_MSG, MODEL_VALUE_ERR_MSG, NOT_NULL_ERR_MSG
from testy.tests_representation.choices import ResultStatusType
from testy.tests_representation.models import ResultStatus


@pytest.mark.django_db
class TestResultStatusModelModel:
    relation_name = ResultStatus._meta.label_lower.replace('.', '_')

    @pytest.mark.parametrize('parameter_name', ['name'])
    def test_not_null_constraint(self, parameter_name, result_status_factory):
        with pytest.raises(IntegrityError) as err:
            result_status_factory(**{parameter_name: None})
        assert NOT_NULL_ERR_MSG.format(
            relation=self.relation_name, column=parameter_name,
        ) in str(err.value), 'Expected error message was not found.'

    @pytest.mark.parametrize(
        'parameter_name, incorrect_value, error_type, err_msg', [
            (
                'project', 'abc', ValueError, MODEL_VALUE_ERR_MSG.format(
                    value='abc', model_name='ResultStatus', column_name='project',
                    column_model='Project',
                ),
            ),
            ('type', 'abc', ValueError, INT_VALUE_ERR_MSG.format(column='type', value='abc')),
        ],
    )
    def test_fields_type_constraint(self, parameter_name, incorrect_value, error_type, result_status_factory, err_msg):
        with pytest.raises(error_type) as err:
            result_status_factory(**{parameter_name: incorrect_value})
        assert err_msg in str(err.value)

    def test_valid_model_creation(self, result_status):
        systems_count = ResultStatus.objects.filter(type=ResultStatusType.SYSTEM).count()
        assert ResultStatus.objects.count() == systems_count + 1
        assert ResultStatus.objects.get(id=result_status.id) == result_status
