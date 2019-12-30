"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from pathlib import Path

import pytest
from watermark.utils import guess_output


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
