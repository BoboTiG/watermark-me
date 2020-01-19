"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
import sys
from pathlib import Path


# Current OS
LINUX = sys.platform == "linux"
MAC = sys.platform == "darwin"
WINDOWS = sys.platform == "win32"

# The company name
COMPANY = "Schoentgen Inc."

# Product details
PRODUCT = "watermark"
TITLE = "Watermark me!"

# Auto-update URL
UPDATE_URL = "https://api.github.com/repos/BoboTiG/watermark-me/releases"

# The default folder where to get/put the configuration file
if LINUX:
    CONF_DIR = f"$XDG_CONFIG_HOME/{PRODUCT}"
elif MAC:
    CONF_DIR = f"~/.{PRODUCT}"
elif WINDOWS:
    CONF_DIR = f"%LOCALAPPDATA%/{COMPANY}/{PRODUCT}"

# Data and resources folders
if hasattr(sys, "frozen"):
    # PyInstaller
    DATA_DIR = Path(getattr(sys, "_MEIPASS")) / "data"
    RES_DIR = Path(getattr(sys, "_MEIPASS")) / "res"
    FREEZER = "pyinstaller"
else:
    # None and Nuitka
    DATA_DIR = Path(__file__).parent / "data"
    RES_DIR = Path(__file__).parent / "res"
    FREEZER = ""
    if "__compiled__" in globals():
        FREEZER = "nuikta"
