"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
import sys

from watermark.conf import save_config
from watermark.gui import Application


if __name__ == "__main__":
    app = Application()
    try:
        sys.exit(app.exec_())
    finally:
        save_config()
