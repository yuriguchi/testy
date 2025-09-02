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
import contextlib
import time
from collections import namedtuple
from enum import Enum

from django.conf import settings

_DAYS = 'days'

PeriodInfo = namedtuple('PeriodInfo', ['period', 'period_in_workday', 'is_period_in_workday'])


class Period(Enum):
    WEEK = PeriodInfo(60 * 60 * 24 * 7, None, is_period_in_workday=False)
    DAY = PeriodInfo(
        60 * 60 * 24,
        60 * 60 * settings.WORK_HOURS,
        is_period_in_workday=True,
    )
    HOUR = PeriodInfo(60 * 60, None, is_period_in_workday=True)
    MINUTE = PeriodInfo(60, None, is_period_in_workday=True)
    SECOND = PeriodInfo(1, None, is_period_in_workday=True)

    def in_seconds(self, in_workday=False):
        if in_workday:
            if not self.value.is_period_in_workday:
                return None
            if value_to_workday := self.value.period_in_workday:
                return value_to_workday
        return self.value.period

    @classmethod
    def list_of_workday(cls):
        return [period for period in list(cls) if period.value.is_period_in_workday]


class WorkTimeProcessor:

    @classmethod
    def format_duration(cls, seconds: int, to_workday: bool = True):
        periods = Period.list_of_workday() if to_workday else list(Period)
        result = []
        for period in periods:
            count = period.in_seconds(in_workday=to_workday)
            value = seconds // count
            if value:
                seconds -= value * count
                result.append('{0}{1}'.format(value, period.name[0].lower()))
        return ' '.join(result)

    @classmethod
    def seconds_to_day(cls, seconds: int, to_workday: bool = True):
        day_in_seconds = Period.DAY.in_seconds()
        workday_in_seconds = Period.DAY.in_seconds(in_workday=True)
        seconds_in_day = day_in_seconds if to_workday else workday_in_seconds
        n_days = seconds // seconds_in_day
        difference_in_seconds = n_days * (day_in_seconds - workday_in_seconds)
        seconds -= difference_in_seconds if to_workday else -difference_in_seconds
        return seconds


@contextlib.contextmanager
def timer(msg: str):
    start_time = time.time()
    yield
    print(msg, time.time() - start_time)
