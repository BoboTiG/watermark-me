"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from pathlib import Path

from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
    qApp,
)

from .settings import Settings
from ..conf import CONF
from ..constants import TITLE
from ..watermark import apply_watermarks


class MainWindow(QMainWindow):
    """Main window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(TITLE)
        # self.setWindowIcon(icon)

        # Little trick here!
        #
        # Qt strongly builds on a concept called event loop.
        # Such an event loop enables you to write parallel applications without multithreading.
        # The concept of event loops is especially useful for applications where
        # a long living process needs to handle interactions from a user or client.
        # Therefore, you often will find event loops being used in GUI or web frameworks.
        #
        # However, the pitfall here is that Qt is implemented in C++ and not in Python.
        # When we execute app.exec_() we start the Qt/C++ event loop, which loops
        # forever until it is stopped.
        #
        # The problem here is that we don't have any Python events set up yet.
        # So our event loop never churns the Python interpreter and so our signal
        # delivered to the Python process is never processed. Therefore, our
        # Python process never sees the signal until we hit some button of
        # our Qt application window.
        #
        # To circumvent this problem is very easy. We just need to set up a timer
        # kicking off our event loop every few milliseconds.
        #
        # https://machinekoder.com/how-to-not-shoot-yourself-in-the-foot-using-python-qt/
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)

        self.res = Path(__file__).parent.parent / "res"
        self.stats = {"count": 0, "size_before": 0, "size_after": 0}

        self._settings = Settings()

        self._toolbar()
        self.addToolBar(self.toolbar)

        self._status_bar()
        self.setStatusBar(self.status_bar)

        self._window()
        self._button_ok_state()

    def _button_ok_state(self) -> None:
        """Handle the state of the OK button. It should be enabled when particular criterias are met."""

        self.buttons.setEnabled(
            bool(self.text.text() or self.picture) and self.paths_list.count() > 0
        )

    def _select_one_file(self) -> None:
        """Choose an image to use as a watermark picture."""
        image = "Image (*.png *.jpg *.bmp)"
        path, _ = QFileDialog.getOpenFileName(
            caption="Select a watermark picture", filter=image
        )

        if path:
            self.picture.setText(path)

    def _status_bar(self) -> None:
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)

    def _status_msg(self) -> None:
        """Display statistics in the status bar."""
        msg = str(self.stats["count"])
        self.status_bar.showMessage(msg)

    def _toolbar(self) -> QToolBar:
        """Create the toolbar."""
        self.toolbar = QToolBar()

        # Icon: settings
        settings_action = QAction(
            QIcon(str(self.res / "settings.svg")), "Settings", self
        )
        settings_action.setShortcut("Ctrl+S")
        settings_action.triggered.connect(self._settings.exec_)
        self.toolbar.addAction(settings_action)

        # Icon: exit
        exit_action = QAction(QIcon(str(self.res / "exit.svg")), "Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(qApp.quit)
        self.toolbar.addAction(exit_action)

    def _window(self) -> None:
        """Construct the main window."""

        layout = QVBoxLayout()
        # left, top, right, bottom

        # The central widget
        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(layout)

        # 1st line: label + watermark text
        layout_text = QHBoxLayout()
        lbl_text = QLabel("Texte")
        layout.addWidget(lbl_text)
        self.text = QLineEdit(CONF.text)
        self.text.setClearButtonEnabled(True)
        layout_text.addWidget(lbl_text)
        layout_text.addWidget(self.text)
        layout.insertLayout(1, layout_text)

        # 2nd line: label + watermark icon
        layout_picture = QHBoxLayout()
        lbl_picture = QLabel("Icône")
        self.picture = QLineEdit(CONF.picture)
        self.picture.setReadOnly(True)
        btn_choose_file = QPushButton(QIcon(str(self.res / "open.svg")), "Choisir")
        btn_choose_file.setFlat(True)
        btn_choose_file.clicked.connect(self._select_one_file)
        layout_picture.addWidget(lbl_picture)
        layout_picture.addWidget(self.picture)
        layout_picture.addWidget(btn_choose_file)
        layout.insertLayout(2, layout_picture)

        # Files list
        self.paths_list = MyListWidget()
        layout.addWidget(self.paths_list)

        # Buttons
        self.buttons = QDialogButtonBox()
        self.buttons.setStandardButtons(QDialogButtonBox.Ok)
        self.buttons.clicked.connect(self._watermark_everything)
        layout.addWidget(self.buttons)

        self.resize(400, 400)

    def _watermark_everything(self) -> None:
        """Here we gooo!"""

        CONF.text = self.text.text()
        CONF.picture = self.picture.text()

        paths = [
            Path(self.paths_list.item(i).text()) for i in range(self.paths_list.count())
        ]
        if paths:
            for path_orig, path_new in apply_watermarks(paths, CONF.text, CONF.picture):
                if not path_new:
                    continue

                self.stats["count"] += 1
                self.stats["size_before"] += path_orig.stat().st_size
                self.stats["size_after"] += path_new.stat().st_size
                self._status_msg()

            self.paths_list.clear()

        self._button_ok_state()


class MyListWidget(QListWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setSortingEnabled(True)

    def dropEvent(self, event: QEvent) -> None:
        for url in event.mimeData().urls():
            self.addItem(url.path())
            event.acceptProposedAction()
