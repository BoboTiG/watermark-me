"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""

from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .utils import set_style
from ..conf import CONF, save_config
from ..constants import RES_DIR, TITLE
from ..translator import TR


class Settings(QDialog):
    """Settings window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(TR.get("TITLE_SETTINGS", [TITLE]))
        self.setWindowIcon(QIcon(str(RES_DIR / "logo.svg")))

        self.conf = type(CONF)(**vars(CONF).copy())

        layout = QVBoxLayout()
        tabs = QTabWidget(self)
        layout.addWidget(tabs)

        tabs.addTab(self._tab_general(), TR.get("GENERAL"))
        tabs.addTab(self._tab_watermark(), TR.get("WATERMARK"))
        tabs.setCurrentIndex(1)

        # Buttons
        buttons = QDialogButtonBox()
        buttons.setStandardButtons(QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)
        buttons.clicked.connect(self.close)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.resize(400, 400)

    def _on_lang_toggled(self, key: str, value: bool) -> None:
        """Signal triggered when the lang radio buttons are toggled."""
        if value:
            self.conf.lang = key

    def _tab_general(self) -> QWidget:
        """Generate the General tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        tab.setLayout(layout)

        # Lang
        groupbox = QGroupBox(TR.get("LANG"))
        layout.addWidget(groupbox)
        box = QVBoxLayout()
        # box.setAlignment(Qt.AlignHCenter)
        box.setSizeConstraint(QLayout.SetMinAndMaxSize)
        groupbox.setLayout(box)
        for key, name in sorted(TR.langs.values()):
            radio = QRadioButton(name)
            box.addWidget(radio)
            radio.toggled.connect(partial(self._on_lang_toggled, key))
            if CONF.lang == key:
                radio.setChecked(True)

        # Auto-update
        groupbox = QGroupBox(TR.get("UPDATE"))
        layout.addWidget(groupbox)
        groupbox.setCheckable(True)
        groupbox.toggled.connect(lambda value: setattr(self.conf, "update", value))
        groupbox.setChecked(CONF.update)
        box = QVBoxLayout()
        box.setSizeConstraint(QLayout.SetMinAndMaxSize)
        groupbox.setLayout(box)
        box.addWidget(QLabel(TR.get("UPDATE_INFO")))

        # Extensions
        # TODO: to be done when someone needs it

        return tab

    def _tab_watermark(self) -> QWidget:
        """Generate the Watermark tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        tab.setLayout(layout)

        # Opacity
        groupbox = QGroupBox(TR.get("OPACITY"))
        layout.addWidget(groupbox)
        box = QHBoxLayout()
        box.setAlignment(Qt.AlignHCenter)
        box.setSizeConstraint(QLayout.SetMinAndMaxSize)
        groupbox.setLayout(box)
        slider = QSlider()
        box.addWidget(slider)
        opacity_lbl = QLabel()
        box.addWidget(opacity_lbl)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setOrientation(Qt.Horizontal)
        slider.valueChanged.connect(lambda v: setattr(self.conf, "opacity", v / 100))
        slider.valueChanged.connect(lambda v: opacity_lbl.setText(f"{v}%"))
        slider.setValue(CONF.opacity * 100)

        # Font
        groupbox = QGroupBox(TR.get("FONT"))
        layout.addWidget(groupbox)
        box = QHBoxLayout()
        box.setAlignment(Qt.AlignHCenter)
        box.setSizeConstraint(QLayout.SetMinAndMaxSize)
        groupbox.setLayout(box)
        font = QLineEdit(CONF.font)
        box.addWidget(font)
        font.setPlaceholderText(TR.get("FONT_PLACEHOLDER"))
        font.setReadOnly(True)
        font.textChanged.connect(lambda t: setattr(self.conf, "font", t))
        set_style(font)
        icon = QIcon(str(RES_DIR / "open.svg"))
        select = QPushButton(icon, TR.get("CHOOSE"), self)
        select.setFlat(True)
        select.clicked.connect(self.choose_font)
        box.addWidget(select)

        # Optimization
        groupbox = QGroupBox(TR.get("OPTIMIZE_PICTURES"))
        layout.addWidget(groupbox)
        groupbox.setCheckable(True)
        groupbox.toggled.connect(lambda value: setattr(self.conf, "optimize", value))
        groupbox.setChecked(CONF.optimize)
        box = QVBoxLayout()
        box.setSizeConstraint(QLayout.SetMinAndMaxSize)
        groupbox.setLayout(box)
        label = QLabel(TR.get("OPTIMIZE_INFO"))
        box.addWidget(label)
        label.setTextFormat(Qt.RichText)
        label.setOpenExternalLinks(True)
        tinify_key = QLineEdit(CONF.tinify_key)
        box.addWidget(tinify_key)
        tinify_key.setClearButtonEnabled(True)
        tinify_key.setPlaceholderText(TR.get("OPTIMIZE_PLACEHOLDER"))
        tinify_key.textChanged.connect(lambda t: setattr(self.conf, "tinify_key", t))
        set_style(tinify_key)

        return tab

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
