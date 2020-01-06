"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from pathlib import Path

import pytest
from watermark.utils import guess_output, sizeof_fmt


@pytest.mark.parametrize(
    "file, expected, optimized",
    [
        (Path("file.png"), Path("file-w.jpg"), False),
        (Path("file-w.png"), Path("file-w.jpg"), False),
        (Path("file-w.png"), Path("file-wo.jpg"), True),
        (Path("file-wo.png"), Path("file-wo.jpg"), True),
    ],
)
def test_guess_output(file, expected, optimized):
    assert guess_output(file, optimized=optimized) == expected


@pytest.mark.parametrize(
    "size, result",
    [
        (0, "0.0 B"),
        (1, "1.0 B"),
        (-1024, "-1.0 KiB"),
        (1024, "1.0 KiB"),
        (1024 * 1024, "1.0 MiB"),
        (pow(1024, 2), "1.0 MiB"),
        (pow(1024, 3), "1.0 GiB"),
        (pow(1024, 4), "1.0 TiB"),
        (pow(1024, 5), "1.0 PiB"),
        (pow(1024, 6), "1.0 EiB"),
        (pow(1024, 7), "1.0 ZiB"),
        (pow(1024, 8), "1.0 YiB"),
        (pow(1024, 9), "1,024.0 YiB"),
        (pow(1024, 10), "1,048,576.0 YiB"),
        (168_963_795_964, "157.4 GiB"),
    ],
)
def test_sizeof_fmt(size, result):
    assert sizeof_fmt(size) == result


def test_sizeof_fmt_custom_suffix():
    assert sizeof_fmt(168_963_795_964, suffix="o") == "157.4 Gio"
