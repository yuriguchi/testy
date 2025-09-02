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
from testy.core.models import Attachment


@pytest.mark.django_db
@pytest.mark.usefixtures('media_directory')
class TestAttachmentModel:
    @pytest.mark.parametrize('parameter_name', ['project_id', 'name', 'filename', 'size', 'file_extension'])
    def test_not_null_constraint(self, parameter_name, attachment_test_case_factory):
        with pytest.raises(IntegrityError) as err:
            attachment_test_case_factory(**{parameter_name: None})
        assert NOT_NULL_ERR_MSG.format(relation='core_attachment', column=parameter_name) in str(err.value), \
            'Expected error message was not found.'

    def test_valid_model_creation(self, attachment_test_case):
        assert Attachment.objects.count() == 1
        assert Attachment.objects.get(id=attachment_test_case.id) == attachment_test_case

    @pytest.mark.parametrize('factory_name', ['attachment_test_case', 'attachment_test_result'])
    def test_cascade_deletion(self, factory_name, request):
        instance = request.getfixturevalue(factory_name)
        model_class = instance.content_type.model_class()
        model_instance = model_class.objects.get(pk=instance.object_id)
        model_instance.hard_delete()
        assert not Attachment.objects.count()
