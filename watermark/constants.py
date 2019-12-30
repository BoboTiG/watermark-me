"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from sys import platform

# Current OS
LINUX = platform == "linux"
MAC = platform == "darwin"
WINDOWS = platform == "win32"

# The company name
COMPANY = "Schoentgen Inc."

# Product details
PRODUCT = "watermark"
TITLE = "Watermark me!"

# The default folder where to get/put the configuration file
if LINUX:
    CONF_DIR = f"$XDG_CONFIG_HOME/{PRODUCT}"
elif MAC:
    CONF_DIR = f"~/.{PRODUCT}"
elif WINDOWS:
    CONF_DIR = f"%LOCALAPPDATA%/{COMPANY}/{PRODUCT}"
