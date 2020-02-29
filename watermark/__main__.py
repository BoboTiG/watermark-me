"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
import sys

from PyQt5.QtWidgets import QApplication
from tendo.singleton import SingleInstance, SingleInstanceException
from watermark.conf import save_config
from watermark.gui.app import MainWindow


def main() -> int:
    """Entry point."""
    # Allow only one instance
    try:
        me = SingleInstance()  # noqa
    except SingleInstanceException:
        return 1

    try:
        app = QApplication([])
        window = MainWindow()
        window.show()
        return app.exec_()
    finally:
        save_config()


if __name__ == "__main__":
    sys.exit(main())
