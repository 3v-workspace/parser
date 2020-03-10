# Copyright Bors LTD
# This file is part of django-icons-mimetypes.
#
#    django-icons-mimetypes is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Django-icons-mimetypes is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with django-icons-mimetypes.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os

from django.contrib.staticfiles.storage import staticfiles_storage


ICONS_MIMETYPES_ROOT = os.path.join(os.path.dirname(__file__), "static", "mimetypes")

ICON_FOLDER = "folder.png"
ICON_DEFAULT = "application-x-executable.png"
SIZE_DEFAULT = "64x64"

# Preload available icons with the static file URL
ICONS_CACHE = {}

MIMETYPE_FALLBACK = {
    'application/rtf': "x-office-eservice",
    'application/vnd.oasis.opendocument.text': "x-office-eservice",
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': "application/msexcel",
    'application/zip': "package-x-generic",
}

MAIN_PART_FALLBACK = {
    'image': "image-x-generic",
    'text': "text-x-generic",
}


logger = logging.getLogger(__name__)


def _load_icons_cache():
    for size in os.listdir(ICONS_MIMETYPES_ROOT):
        size_path = os.path.join(ICONS_MIMETYPES_ROOT, size)
        for icon in os.listdir(size_path):
            icon_path = os.path.join("mimetypes", size, icon)
            # Compute static URL
            ICONS_CACHE[(size, icon)] = staticfiles_storage.url(icon_path)

_load_icons_cache()


def get_icon(mimetype, size=SIZE_DEFAULT):
    # Folder
    if not mimetype:
        return ICONS_CACHE[(size, ICON_FOLDER)]

    mimetype = MIMETYPE_FALLBACK.get(mimetype, mimetype)
    key = "{0}.png".format(mimetype.replace("/", "-"))

    try:
        return ICONS_CACHE[(size, key)]
    except KeyError:
        main, _sub = mimetype.split("/")
        try:
            key = "{0}.png".format(MAIN_PART_FALLBACK[main])
            return ICONS_CACHE[(size, key)]
        except KeyError:
            logger.warn('missing icon for mimetype "%s"' % (mimetype,))
            return ICONS_CACHE[(size, ICON_DEFAULT)]
