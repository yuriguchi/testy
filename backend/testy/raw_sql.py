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

INSERT_LABELED_ITEM_TRIGGER = pgtrigger.Func(
"""BEGIN
    IF EXISTS (SELECT 1
               FROM core_labelids
               WHERE content_type_id = NEW.content_type_id
                 AND object_id = NEW.object_id) THEN
        UPDATE core_labelids
        SET ids = array_append(ids, NEW.label_id)
        WHERE content_type_id = NEW.content_type_id
          AND object_id = NEW.object_id;
    ELSE
        INSERT INTO core_labelids (ids, is_deleted, content_type_id, object_id)
        VALUES (ARRAY [NEW.label_id], FALSE, NEW.content_type_id, NEW.object_id);
    END IF;

    RETURN NEW;
END;"""
)
DELETE_LABELED_ITEM_TRIGGER = pgtrigger.Func(
"""BEGIN
    UPDATE core_labelids
    SET ids = array_remove(ids, OLD.label_id)
    WHERE content_type_id = OLD.content_type_id
      AND object_id = OLD.object_id;
    DELETE FROM core_labelids
    WHERE content_type_id = OLD.content_type_id
      AND object_id = OLD.object_id
      AND array_length(ids, 1) = 0;
RETURN OLD;
END;"""
)
