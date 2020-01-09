"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from pathlib import Path


def guess_output(file: Path, optimized: bool = False) -> Path:
    """Guess the output filename from a given *file*.
    "-w" is added when the file is being watermarked.
    "-wo" is added when the file is being optimized.

    "-o" and "-ow" cannot exist because the watermarking is always done first.

    A filename for a JEPG is returned.
    """
    basename = file.stem

    if optimized:
        if not basename.endswith("-wo"):
            basename += "o"
    elif not basename.endswith("-w"):
        basename += "-w"

    return file.with_name(f"{basename}.jpg")


def sizeof_fmt(num: int, suffix: str = "B") -> str:
    """
    Human readable version of file size.
    Supports:
        - all currently known binary prefixes (https://en.wikipedia.org/wiki/Binary_prefix)
        - negative and positive numbers
        - numbers larger than 1,000 Yobibytes
        - arbitrary units
    Examples:
        >>> sizeof_fmt(168963795964)
        "157.4 GiB"
        >>> sizeof_fmt(168963795964, suffix="o")
        "157.4 Gio"
    Source: https://stackoverflow.com/a/1094933/1117028
    """
    val = float(num)
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(val) < 1024.0:
            return f"{val:3.1f} {unit}{suffix}"
        val /= 1024.0
    return f"{val:,.1f} Yi{suffix}"
