"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from ..conf import CONF, save_config
from ..constants import RES_DIR, TITLE
from ..translator import TR


OPTIONS_TO_SKIP = {"picture", "text"}


class Settings(QDialog):
    """Settings window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(TR.get("TITLE_SETTINGS", [TITLE]))
        self.setWindowIcon(QIcon(str(RES_DIR / "logo.svg")))

        layout = QVBoxLayout()

        self.conf = type(CONF)(**vars(CONF).copy())

        # Add a line by option
        for idx, (option, value) in enumerate(vars(CONF).items()):
            if option in OPTIONS_TO_SKIP:
                continue
            layout.insertLayout(idx, self.add_option(option, value))

        # Buttons
        buttons = QDialogButtonBox()
        buttons.setStandardButtons(QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)
        buttons.clicked.connect(self.close)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.resize(400, 400)

    def add_option(self, option: str, value: Any) -> QHBoxLayout:
        """Add a new row with a given option and its value."""
        layout = QHBoxLayout()

        label = QLabel(option)
        layout.addWidget(label)

        if isinstance(value, bool):
            data_obj = QCheckBox()
            data_obj.setTristate(False)
            if value:
                data_obj.setCheckState(Qt.Checked)
            data_obj.stateChanged.connect(
                lambda state: setattr(self.conf, option, bool(state))
            )
        elif isinstance(value, float):
            data_obj = QLineEdit(str(value))
            data_obj.setInputMask("0.00")
            data_obj.textChanged.connect(
                lambda text: setattr(self.conf, option, float(text))
            )
        elif isinstance(value, (list, tuple)):
            data_obj = QLineEdit(" ".join(value))
            data_obj.setClearButtonEnabled(True)
            data_obj.textChanged.connect(
                lambda text: setattr(self.conf, option, text.split(" "))
            )
        elif isinstance(value, str):
            data_obj = QLineEdit(value)
            data_obj.setClearButtonEnabled(True)
            data_obj.textChanged.connect(lambda text: setattr(self.conf, option, text))
        else:
            data_obj = QLineEdit(f"{type(value)} is not yet handled.")
            data_obj.setReadOnly(True)

        layout.addWidget(data_obj)

        if option == "font":
            data_obj.setClearButtonEnabled(False)
            data_obj.setReadOnly(True)

            icon = QIcon(str(RES_DIR / "open.svg"))
            select = QPushButton(icon, TR.get("CHOOSE"), self)
            select.setFlat(True)
            select.clicked.connect(self.choose_font)
            layout.addWidget(select)

        return layout

    def apply_changes(self) -> None:
        """Save configuration changes."""
        for option, value in vars(self.conf).items():
            setattr(CONF, option, value)

        save_config()

    def choose_font(self) -> str:
        """Select a font file."""
        title = TR.get("TITLE_SEL_FONT", [TITLE])
        ttf = "Font (*.ttf)"
        path, _ = QFileDialog.getOpenFileName(caption=title, filter=ttf)
        return path
