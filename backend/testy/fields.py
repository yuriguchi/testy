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
import datetime
import re

import pytimeparse
from django.core import exceptions
from django.db import models
from forms import EstimateFormField

from testy.utilities.time import WorkTimeProcessor


class BaseEstimateField(models.Field):
    default_error_message = 'Invalid value for estimate.'
    estimate_day_regexs = [r'.*\d+\s*(d|days).*', r'\d+:\d+:\d+:\d+(\.\d+)?']
    default_type = None

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, self.default_type):
            return value

        parsed, err = self.parse_duration(value)

        if parsed is not None:
            return parsed

        raise exceptions.ValidationError(str(err) if err else self.default_error_message)

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                'form_class': EstimateFormField,
                **kwargs,
            },
        )

    @classmethod
    def get_value_in_seconds(cls, value):
        value = value.strip()

        if value[0] == '-':
            return None, exceptions.ValidationError('Estimate value must be positive')

        if value.isnumeric():
            value = f'{value}m'

        seconds_by_wd = pytimeparse.parse(value)

        if not seconds_by_wd:
            return None, None

        if any(re.match(regex, value) for regex in cls.estimate_day_regexs):
            seconds_by_wd = WorkTimeProcessor.seconds_to_day(int(seconds_by_wd))

        try:
            datetime.timedelta(seconds=seconds_by_wd)
        except OverflowError:
            return None, exceptions.ValidationError('Estimate value is too big')
        return seconds_by_wd, None

    @classmethod
    def parse_duration(cls, value):
        raise NotImplementedError


class EstimateField(BaseEstimateField):
    default_type = datetime.timedelta

    @classmethod
    def parse_duration(cls, value):
        seconds, err = cls.get_value_in_seconds(value)
        return datetime.timedelta(seconds=seconds), err

    def get_internal_type(self):
        return 'DurationField'


class IntegerEstimateField(BaseEstimateField):
    default_type = int

    @classmethod
    def parse_duration(cls, value):
        return cls.get_value_in_seconds(value)

    def get_internal_type(self):
        return 'IntegerField'
