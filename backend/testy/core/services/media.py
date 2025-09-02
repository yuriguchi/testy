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
from pathlib import Path

from django.conf import settings
from django.db.models.fields.files import FieldFile
from PIL import Image, ImageFile

from testy.utilities.string import strip_suffixes

ImageFile.LOAD_TRUNCATED_IMAGES = True

logger = logging.getLogger(__name__)

err_msg = 'Could not open image for populating thumbnails for file: {filepath}, source error: {err}'


class MediaService:

    def populate_image_thumbnails(self, file: FieldFile, old_file: FieldFile | None = None) -> None:
        """
        Create basic images thumbnails for resolutions specified in config.

        Args:
            file: field file from instance.
            old_file: field file from instance that was replaced.
        """
        if old_file:
            src_path = Path(old_file.path)
            self.remove_media(src_path)
        if not file or not Path(file.path).exists():
            return
        try:
            full_image = Image.open(file.path)
        except Exception as err:
            logger.warning(err_msg.format(filepath=file.path, err=err))
            return
        path, suffixes = strip_suffixes(file.path)
        for resolution in settings.TESTY_THUMBNAIL_RESOLUTIONS:
            width, height = resolution
            thumbnail = full_image.copy()
            thumbnail.thumbnail(resolution)
            thumbnail.save(
                Path(f'{path}@{width}x{height}{suffixes}'),
            )

    @classmethod
    def remove_media(cls, src_file_path: Path):
        """
        Remove media file and all related files by name from filesystem.

        Args:
            src_file_path: path to source file
        """
        curr_attachment_dir = Path(*src_file_path.parts[:-1])
        if not curr_attachment_dir.exists():
            return
        attachment_files_path = list(curr_attachment_dir.iterdir())
        for attachment_file_path in attachment_files_path:
            if src_file_path.stem != attachment_file_path.stem.split('@')[0]:
                continue
            if attachment_file_path.is_file():
                attachment_file_path.unlink(missing_ok=True)
        src_file_path.unlink(missing_ok=True)

    @classmethod
    def crop_src_img(cls, file: FieldFile, crop: dict[str, float]):
        """
        Crop image uploaded to model and replace src image with cropped one.

        Args:
            file: field file from model instance.
            crop: dictionary containing float coefficients to crop image.
        """
        if not file:
            return
        if not Path(file.path).exists() or not crop:
            return
        full_image = Image.open(file.path)
        cropped_img = full_image.crop(
            box=(
                int(full_image.width * crop['left']),
                int(full_image.height * crop['upper']),
                int(full_image.width * crop['right']),
                int(full_image.height * crop['lower']),
            ),
        )
        cropped_img.save(file.path)
