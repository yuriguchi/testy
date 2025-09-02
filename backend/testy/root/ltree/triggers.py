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
import pgtrigger

_PARENT_DISTINCT = pgtrigger.Q(old__parent_id__df=pgtrigger.F('new__parent_id'))
_PATH_DISTINCT = pgtrigger.Condition(
    'not("new"."path" operator("public".=) "old"."path") and (coalesce("new"."path", "old"."path") is not null)',
)
_DESCENDANTS_FUNC = pgtrigger.Func(
    'UPDATE {meta.db_table} '
    'SET path = NEW.path || subpath({columns.path}, nlevel(OLD.path)), '
    '    tree_id = NEW.tree_id '
    'WHERE {columns.path} <@ OLD.path AND id != NEW.id AND tree_id = OLD.tree_id; '
    'RETURN NEW;',
)
_INSERT_UPDATE_FUNC = pgtrigger.Func(
    'IF NEW.parent_id IS NULL THEN '
    '    NEW.path = NEW.id::text::ltree; '
    '    NEW.tree_id = NEW.id; '
    'ELSE '
    '    SELECT path || NEW.id::text, tree_id FROM {meta.db_table} '
    '    WHERE id = NEW.parent_id INTO NEW.path, NEW.tree_id; '
    'END IF; '
    'RETURN NEW;',
)


def get_triggers(name: str) -> list[pgtrigger.Trigger]:
    return [
        pgtrigger.Trigger(
            name=f'{name}_insert_trg',
            operation=pgtrigger.Insert,
            when=pgtrigger.Before,
            func=_INSERT_UPDATE_FUNC,
        ),
        pgtrigger.Trigger(
            name=f'{name}_path_change_trg',
            operation=pgtrigger.Update,
            when=pgtrigger.Before,
            condition=_PARENT_DISTINCT,
            func=_INSERT_UPDATE_FUNC,
        ),
        pgtrigger.Trigger(
            name=f'{name}_path_descendants_trg',
            operation=pgtrigger.Update,
            when=pgtrigger.After,
            condition=_PATH_DISTINCT,
            func=_DESCENDANTS_FUNC,
        ),
    ]
