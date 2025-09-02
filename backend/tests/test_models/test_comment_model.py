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

from tests.error_messages import NOT_NULL_ERR_MSG
from testy.comments.models import Comment


@pytest.mark.django_db
@pytest.mark.usefixtures('media_directory')
class TestCommentModel:
    @pytest.mark.parametrize('parameter_name', ['object_id', 'content_type_id'])
    def test_not_null_constraint(self, parameter_name, comment_test_factory):
        with pytest.raises(IntegrityError) as err:
            comment_test_factory(**{parameter_name: None})
        assert NOT_NULL_ERR_MSG.format(relation='comments_comment', column=parameter_name) in str(err.value), \
            'Expected error message was not found.'

    @pytest.mark.parametrize(
        'factory_name', [
            'comment_test_factory', 'comment_test_case_factory', 'comment_test_result_factory',
            'comment_test_suite_factory', 'comment_test_plan_factory',
        ],
    )
    def test_valid_model_creation(self, factory_name, request):
        factory = request.getfixturevalue(factory_name)
        instance = factory()
        assert Comment.objects.count() == 1
        assert Comment.objects.get(id=instance.id) == instance

    @pytest.mark.parametrize(
        'factory_name', [
            'comment_test_factory', 'comment_test_case_factory', 'comment_test_result_factory',
            'comment_test_suite_factory', 'comment_test_plan_factory',
        ],
    )
    def test_cascade_deletion(self, factory_name, request):
        factory = request.getfixturevalue(factory_name)
        instance = factory()
        model_class = instance.content_type.model_class()
        model_instance = model_class.objects.get(pk=instance.object_id)
        model_instance.hard_delete()
        assert not Comment.objects.count()
