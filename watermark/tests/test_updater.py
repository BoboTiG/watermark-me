"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from watermark import __version__
from watermark.updater.base import BaseUpdater
from watermark.updater.utils import get_update_status


def test_get_update_status_no_versions():
    """Simple test with no versions yet."""
    assert get_update_status(__version__, []) == ""


def test_get_update_status_beta():
    """Simple test with betas."""
    versions = [
        {"name": "0.1b1", "prerelease": True, "assets": []},
        {"name": "0.1b2", "prerelease": True, "assets": []},
    ]
    assert get_update_status("0.1b1", versions) == "0.1b2"
    assert get_update_status("0.1b2", versions) == ""


def test_get_update_status_beta_to_release():
    """Test beta -> release."""
    versions = [
        {"name": "0.1b2", "prerelease": True, "assets": []},
        {"name": "0.1", "prerelease": False, "assets": []},
    ]
    assert get_update_status("0.1b2", versions) == "0.1"
    assert get_update_status("0.1", versions) == ""


def test_get_update_status_release_to_beta():
    """Test release -> beta."""
    versions = [
        {"name": "0.1", "prerelease": False, "assets": []},
        {"name": "0.1.1b1", "prerelease": True, "assets": []},
    ]
    assert get_update_status("0.1", versions) == "0.1.1b1"
    assert get_update_status("0.1.1b1", versions) == ""


def test_base_updater():

    checkpoint = False

    class Updater(BaseUpdater):
        def install(self, filename: str) -> None:
            nonlocal checkpoint
            checkpoint = True

    updater = Updater()
    updater.check(__version__)

    # Append versions
    assets = [{"name": "example.exe", "browser_download_url": "https://example.org"}]
    versions = [
        {"name": "0.1b1", "prerelease": True, "assets": []},
        {"name": "0.1b2", "prerelease": True, "assets": assets},
    ]
    updater.versions = versions
    updater.check("0.1b1")
    assert checkpoint
