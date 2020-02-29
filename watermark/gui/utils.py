"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QLineEdit


def set_cursor(obj: QObject, cursor: QCursor = Qt.PointingHandCursor) -> None:
    """Set the *cursor* for the given *obj*."""
    obj.setCursor(QCursor(cursor))


def set_style(line: QLineEdit) -> None:
    """Set the line edit style."""
    line.setStyleSheet("QLineEdit{padding: 5px 10px}")
