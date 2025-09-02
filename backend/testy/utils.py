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
import logging
import time
from contextlib import contextmanager
from hashlib import md5
from pathlib import PurePath

from celery_progress.backend import ProgressRecorder

from testy.utilities.string import strip_suffixes


class ProgressRecorderContext(ProgressRecorder):
    def __init__(self, task, total, debug=False, description='Task started'):
        self.debug = debug
        self.current = 0
        self.total = total
        if self.debug:
            return
        super().__init__(task)
        self.set_progress(current=self.current, total=total, description=description)

    @contextmanager
    def progress_context(self, description):
        if self.debug:
            logging.info(description)
            yield
            return
        self.current += 1
        self.set_progress(self.current, self.total, description)
        yield

    def clear_progress(self):
        self.current = 0


def get_attachments_file_path(instance, filename):  # Exists because we don't want to alter older migrations
    return get_media_file_path(instance, filename, 'attachments')


def get_media_file_path(instance, original_filename, media_name):
    name, suffix = strip_suffixes(original_filename)
    hash_source = str(time.time()) + str(name)
    timestamp_hash = md5(hash_source.encode(), usedforsecurity=False).hexdigest()
    new_filename = f'{timestamp_hash}{suffix}'
    return PurePath(media_name, new_filename[:2], new_filename)
