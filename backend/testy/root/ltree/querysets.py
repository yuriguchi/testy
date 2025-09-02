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
from django.db import models

_PATH = 'path'


class LtreeQuerySet(models.QuerySet):
    def get_ancestors(self, include_self=False):
        return self.get_ancestors_for_qs(self, include_self).order_by(_PATH)

    def get_descendants(self, include_self=False):
        return self.get_descendants_for_qs(self, include_self).order_by(_PATH)

    def get_descendants_for_qs(self, qs, include_self=False, manager_name: str = 'objects'):
        lookup = models.Q()
        for node_path in qs.values_list(_PATH, flat=True):
            lookup |= models.Q(path__descendant=node_path)
            if not include_self:
                lookup &= ~models.Q(path=node_path)
        if not len(lookup):
            return qs
        manager = getattr(qs.model, manager_name)
        return manager.filter(lookup).order_by(_PATH)

    def get_ancestors_for_qs(self, qs, include_self=False, manager_name: str = 'objects'):
        lookup = models.Q()
        for node_path in qs.values_list(_PATH, flat=True):
            lookup |= models.Q(path__ancestor=node_path)
            if not include_self:
                lookup &= ~models.Q(path=node_path)
        if not len(lookup):
            return qs
        manager = getattr(qs.model, manager_name)
        return manager.filter(lookup).order_by(_PATH)
