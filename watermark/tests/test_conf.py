"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from os.path import isfile
from types import SimpleNamespace

from watermark.conf import read_config, save_config


def test_read_file_ok(location):
    config = read_config(location / "conf_ok")
    assert isinstance(config, SimpleNamespace)


def test_read_file_not_found(location):
    config = read_config(location)
    assert isinstance(config, SimpleNamespace)


def test_read_empty_file(location):
    config = read_config(location / "conf_empty")
    assert isinstance(config, SimpleNamespace)


def test_read_bad_font_path(location):
    config = read_config(location / "conf_bad_font_path")
    assert isinstance(config, SimpleNamespace)
    assert isfile(config.font)


def test_save(tmp_path):
    save_config(tmp_path / "conf_saved")
