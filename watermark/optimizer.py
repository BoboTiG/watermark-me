"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from pathlib import Path
from typing import Optional

import tinify

from .utils import guess_output


def validate_key(key: str) -> bool:
    """Validate the Tinify API key."""
    if not key:
        return False

    tinify.key = key
    try:
        return tinify.validate()
    except tinify.Error:
        return False


def optimize(file: Path, retry: int = 3) -> Optional[Path]:
    """Optimize a given *file* using the Tinify API."""

    # Last retry, all previous attemps failed
    if retry < 0:
        return None

    output = guess_output(file, optimized=True)

    # Already processed
    if output.is_file():
        return output

    # No enough credits for this month :/
    # Note: this is for the free account only.
    if tinify.compression_count > 500:
        return None

    try:
        tinify.from_file(str(file)).to_file(str(output))
    except (tinify.ServerError, tinify.ConnectionError):
        # Network issue, retry
        return optimize(file, retry=retry - 1)

    return output
