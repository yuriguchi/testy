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
from pgtrigger import Before, Delete, Insert, Q, Trigger, Update


def get_statistic_triggers(
    count_field: str,
    decrement_cond: Q | None = None,
    increment_cond: Q | None = None,
) -> list[Trigger]:
    if decrement_cond is None:
        decrement_cond = Q(old__is_deleted=False, new__is_deleted=True) | Q(old__is_archive=False, new__is_archive=True)
    if increment_cond is None:
        increment_cond = Q(old__is_deleted=True, new__is_deleted=False) | Q(old__is_archive=True, new__is_archive=False)
    return [
        Trigger(
            name=f'{count_field}_increment_statistics_on_insert',
            operation=Insert,
            when=Before,
            func=""" 
            UPDATE core_projectstatistics 
            SET {count_field} = {count_field} + 1 
            WHERE project_id = NEW.project_id;
            RETURN NEW;
            """.format(count_field=count_field),  # noqa: S608
        ),
        Trigger(
            name=f'{count_field}_decrement_statistics_on_update',
            operation=Update,
            when=Before,
            func="""
            UPDATE core_projectstatistics 
            SET {count_field} = {count_field} - 1 
            WHERE project_id = NEW.project_id;
            RETURN NEW;
            """.format(count_field=count_field),  # noqa: S608
            condition=decrement_cond,
        ),
        Trigger(
            name=f'{count_field}_increment_statistics_on_update',
            operation=Update,
            when=Before,
            func="""
            UPDATE core_projectstatistics 
            SET {count_field} = {count_field} + 1 
            WHERE project_id = NEW.project_id;
            RETURN NEW;
            """.format(count_field=count_field),  # noqa: S608
            condition=increment_cond,
        ),
        Trigger(
            name=f'{count_field}_decrement_statistics_on_delete',
            operation=Delete,
            when=Before,
            func="""
            UPDATE core_projectstatistics 
            SET {count_field} = {count_field} - 1 
            WHERE project_id = OLD.project_id;
            RETURN OLD;
            """.format(count_field=count_field),  # noqa: S608
        ),
    ]
