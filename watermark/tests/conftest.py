"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
import random
import struct
import zlib
from pathlib import Path
from typing import Union

import pytest


@pytest.fixture(scope="session")
def location() -> Path:
    """Return the folder containing test files."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def picture(location) -> str:
    """Return the test picture file."""
    return str(location / "arresto-momentum.png")


@pytest.fixture(scope="session")
def png():
    """Generate a random PNG file."""

    def generate_random_png(filename: Path) -> Union[bytes, Path]:
        """Generate a random PNG file.

        Source: http://www.tiger-222.fr/?d=2017/04/13/10/20/59

        :param filename: The output file name.
        :return mixed: None if given filename else bytes
        """

        size = random.randint(1, 1024)
        pack = struct.pack

        def chunk(header, data):
            return (
                pack(">I", len(data))
                + header
                + data
                + pack(">I", zlib.crc32(header + data) & 0xFFFFFFFF)
            )

        magic = pack(">8B", 137, 80, 78, 71, 13, 10, 26, 10)
        png_filter = pack(">B", 0)
        scanline = pack(">{}B".format(size * 3), *[0] * (size * 3))
        content = [png_filter + scanline for _ in range(size)]
        png = (
            magic
            + chunk(b"IHDR", pack(">2I5B", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(content)))
            + chunk(b"IEND", b"")
        )

        with open(filename, "wb") as fileo:
            fileo.write(png)

        return filename

    return generate_random_png
