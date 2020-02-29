"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
import re
from os.path import expandvars, isfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict

import yaml

from .constants import CONF_DIR, DATA_DIR


Options = Dict[str, Any]


def default_font() -> str:
    """Get the default font file."""
    return str(DATA_DIR / "URWChanceryL-MediItal.ttf")


def default_config() -> Options:
    """Get default options."""
    return {
        "extensions": ("jpg", "png"),
        "font": default_font(),
        "lang": "",
        "opacity": 0.25,
        "optimize": False,
        "picture": "",
        "text": "",
        "text_color": "#ffffff",
        "tinify_key": "",
        "update": True,
    }


def read_config(folder: str = CONF_DIR) -> SimpleNamespace:
    """Read the configugration file."""
    file = Path(expandvars(folder)).expanduser() / "config.yml"
    file.parent.mkdir(parents=True, exist_ok=True)

    try:
        file_config = yaml.safe_load(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        file_config = {}
    else:
        if not isinstance(file_config, dict):
            file_config = {}

    config = {**default_config(), **file_config}

    # Ensure the font file is correct, fallback on the default one on any issue
    if not isfile(config["font"]):
        config["font"] = default_font()

    # Ensure the picture exists
    if not isfile(config["picture"]):
        config["picture"] = ""

    # Ensure the text color has the good format
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", config["text_color"]):
        config["text_color"] = "#ffffff"

    return SimpleNamespace(**config)


def save_config(folder: str = CONF_DIR) -> None:
    """Save options to the configugration file."""
    file = Path(expandvars(folder)).expanduser() / "config.yml"
    file.parent.mkdir(parents=True, exist_ok=True)

    with file.open(mode="w", encoding="utf-8") as fh:
        yaml.safe_dump(vars(CONF), fh)


CONF = read_config()
