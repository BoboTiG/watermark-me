"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
import logging
import os
import uuid
from abc import abstractmethod
from tempfile import gettempdir
from typing import Any, Dict, List

import requests

from .utils import get_update_status
from ..constants import UPDATE_URL


class BaseUpdater:
    """ Updater class for frozen application. """

    def __init__(self, url: str = "") -> None:
        self.url = url or UPDATE_URL
        self.versions: List[Dict[str, Any]] = []
        self.chunk_size = 8192

    #
    # Public methods that can be overrided
    #

    @abstractmethod
    def install(self, filename: str) -> None:
        """
        Install the new version.
        Uninstallation of the old one or any actions needed to install
        the new one has to be handled by this method.
        """

    def update(self, version: str) -> None:
        logging.info(f"Starting application update process to version {version}")
        self._install(version, self._download(version))

    #
    # Private methods, should not try to override
    #

    def _download(self, version: str) -> str:
        """ Download a given version to a temporary file. """

        url = ""
        name = ""
        for version_info in self.versions:
            if version_info["name"] == version:
                asset = version_info["assets"][0]
                url = asset["browser_download_url"]
                name = asset["name"]
                break

        path = os.path.join(gettempdir(), uuid.uuid4().hex + "_" + name)

        logging.info(f"Fetching version {version!r} into {path!r}")
        with requests.get(url, stream=True) as req, open(path, "wb") as tmp:
            for chunk in req.iter_content(self.chunk_size):
                tmp.write(chunk)

            # Force write of file to disk
            tmp.flush()
            os.fsync(tmp.fileno())

        return path

    def _fetch_versions(self) -> None:
        """ Fetch available versions. It sets `self.versions` on success. """
        with requests.get(self.url) as resp:
            resp.raise_for_status()
            self.version = resp.json()

    def _install(self, version: str, filename: str) -> None:
        """
        OS-specific method to install the new version.
        It must take care of uninstalling the current one.
        """
        logging.info(f"Installing version {version}")
        self.install(filename)

    def check(self, version: str) -> None:
        """ Retrieve available versions and install an eventual found candidate. """
        self._fetch_versions()
        new_version = get_update_status(version, self.versions)
        if new_version:
            logging.debug(f"Found a new version: {new_version!r}")
            self.update(new_version)
