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
import binascii
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()


class TTLToken(models.Model):
    key = models.CharField(_('Key'), max_length=settings.TOKEN_MAX_LEN, primary_key=True)
    user = models.ForeignKey(
        UserModel,
        related_name='auth_token',
        on_delete=models.CASCADE,
        verbose_name=_('User'),
    )
    created = models.DateTimeField(_('Created'), editable=False)
    expiration_date = models.DateTimeField(_('Expires at'), editable=False)
    description = models.CharField(
        _('Description'),
        max_length=settings.CHAR_FIELD_MAX_LEN,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('Token')
        verbose_name_plural = _('Tokens')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.created = timezone.now()
            self.expiration_date = timezone.now() + timezone.timedelta(days=settings.AUTH_TOKEN_TTL)
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        size = 20
        return binascii.hexlify(os.urandom(size)).decode()

    def __str__(self):
        return self.key
