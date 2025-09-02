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

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from testy.users.models import User


class TestyPasswordValidator:
    """Password validator for django default password validation."""

    def validate(self, password: str, user: User = None):
        if not any(char.isupper() for char in password):
            self._raise_error(
                'Password must have at least one uppercase character.',
                'password_no_uppercase',
            )
        if not any(char.islower() for char in password):
            self._raise_error(
                'Password must have at least one lowercase character.',
                'password_no_lowercase',
            )
        if not any(char.isdigit() for char in password):
            self._raise_error(
                'Password must have at least one digit.',
                'password_no_digit',
            )
        if not any(True for char in password if not char.isalnum() and not char.isspace()):  # noqa: WPS221
            self._raise_error(
                'Password must have at least one special character.',
                'password_no_special',
            )

    def get_help_text(self) -> str:
        return _('Password must have upper, lower, digit, and special characters.')

    def _raise_error(self, message: str, code: str) -> None:
        raise ValidationError(_(message), code=code)


class PasswordValidator:
    def __call__(self, password: str):
        validate_password(password)
