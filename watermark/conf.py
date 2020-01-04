"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from os.path import expandvars, isfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict

import yaml

from .constants import CONF_DIR


Options = Dict[str, Any]


def default_font() -> str:
    """Get the default font file."""
    here = Path(__file__).parent / "data"
    font = here / "URWChanceryL-MediItal.ttf"
    return str(font)


def default_config() -> Options:
    """Get default options."""
    return {
        "extensions": ("jpg", "png"),
        "font": default_font(),
        "opacity": 0.25,
        "picture": "",
        "text": "www.arresto-momentum.com",
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

    return SimpleNamespace(**config)


def save_config(folder: str = CONF_DIR) -> None:
    """Save options to the configugration file."""
    file = Path(expandvars(folder)).expanduser() / "config.yml"
    file.parent.mkdir(parents=True, exist_ok=True)

    with file.open(mode="w", encoding="utf-8") as fh:
        yaml.safe_dump(vars(CONF), fh)


CONF = read_config()
