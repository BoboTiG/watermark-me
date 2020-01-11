"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from pathlib import Path

from PyQt5.QtCore import QEvent, QTimer, QCoreApplication
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
import tinify

from .settings import Settings
from ..conf import CONF
from ..constants import RES_DIR, TITLE, WINDOWS
from ..optimizer import optimize, validate_key
from ..watermark import apply_watermarks
from ..utils import sizeof_fmt


class MainWindow(QMainWindow):
    """Main window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(TITLE)
        self.setWindowIcon(QIcon(str(RES_DIR / "logo.svg")))

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

        # Keep track of some metrics
        self.stats = {"count": 0, "size_before": 0, "size_after": 0}

        # Used to check if picture optimization is enabled and the provided key valid
        self._use_optimization = None
        self._old_key = None
        self._old_state = None

        if CONF.update:
            self._check_for_update()

        # Init the GUI
        self._settings = Settings()
        self._toolbar()
        self.addToolBar(self.toolbar)
        self._status_bar()
        self.setStatusBar(self.status_bar)
        self._status_msg()
        self._window()
        self.button_ok_state()

    @property
    def use_optimization(self) -> bool:
        """Check if picture optimization is enabled and valid."""
        if (
            self._use_optimization is None
            or CONF.tinify_key != self._old_key
            or CONF.optimize != self._old_state
        ):
            self._old_key = CONF.tinify_key
            self._old_state = CONF.optimize
            self._use_optimization = CONF.optimize and validate_key(self._old_key)
        return self._use_optimization

    def button_ok_state(self) -> None:
        """Handle the state of the OK button. It should be enabled when particular criterias are met."""

        self.buttons.setEnabled(
            bool(self.text.text() or self.picture.text())
            and self.paths_list.count() > 0
        )

    def _check_for_update(self) -> None:
        """Check for a new update."""
        if not WINDOWS:
            return

        from .. import __version__
        from ..updater.windows import Updater

        updater = Updater()
        try:
            updater.check(__version__)
        except Exception:
            self._status_msg("Erreur de MàJ automatique")

    def _select_one_file(self) -> None:
        """Choose an image to use as a watermark picture."""
        image = "Image (*.png *.jpg *.bmp)"
        path, _ = QFileDialog.getOpenFileName(
            caption="Select a watermark picture", filter=image
        )

        if path:
            self.picture.setText(path)
            CONF.picture = path

    def _status_bar(self) -> None:
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)

    def _status_msg(self, msg: str = "") -> None:
        """Display statistics in the status bar."""
        if not msg:
            win = self.stats["size_before"] - self.stats["size_after"]
            msg = f"{self.stats['count']} fichiers traité(s), {sizeof_fmt(win, suffix='o')} gagnés"

            if self.use_optimization:
                # Free account (500 compression / months)
                msg += f" [crédits restants : {500 - tinify.compression_count}]"

        self.status_bar.showMessage(msg)

    def _toolbar(self) -> QToolBar:
        """Create the toolbar."""
        self.toolbar = QToolBar()

        # Icon: settings
        settings_action = QAction(
            QIcon(str(RES_DIR / "settings.svg")), "Settings", self
        )
        settings_action.setShortcut("Ctrl+S")
        settings_action.triggered.connect(self._settings.exec_)
        self.toolbar.addAction(settings_action)

        # Icon: exit
        exit_action = QAction(QIcon(str(RES_DIR / "exit.svg")), "Exit", self)
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
        self.picture.setClearButtonEnabled(True)
        btn_choose_file = QPushButton(QIcon(str(RES_DIR / "open.svg")), "Choisir")
        btn_choose_file.setFlat(True)
        btn_choose_file.clicked.connect(self._select_one_file)
        layout_picture.addWidget(lbl_picture)
        layout_picture.addWidget(self.picture)
        layout_picture.addWidget(btn_choose_file)
        layout.insertLayout(2, layout_picture)

        # Files list
        self.paths_list = DroppableQList(self)
        layout.addWidget(self.paths_list)

        # Buttons
        self.buttons = QDialogButtonBox()
        self.buttons.setStandardButtons(QDialogButtonBox.Ok)
        self.buttons.clicked.connect(self._process_all)
        layout.addWidget(self.buttons)

        self.resize(640, 480)

    def _process_all(self) -> None:
        """Here we gooo!"""

        CONF.text = self.text.text()
        CONF.picture = self.picture.text()

        paths = [
            Path(self.paths_list.item(i).text()) for i in range(self.paths_list.count())
        ]
        if not paths:
            return

        # Add watermark(s) to all files
        for path_orig, path_new in apply_watermarks(paths, CONF.text, CONF.picture):
            if not path_new:
                continue

            # Optimize the picture
            if self.use_optimization:
                path_new_optimized = optimize(path_new)
                if path_new_optimized:
                    # Delete the "-w.jpg"
                    path_new.unlink()
                    # Keep the new "-wo.jpg"
                    path_new = path_new_optimized

            # Update statistics
            self.stats["count"] += 1
            self.stats["size_before"] += path_orig.stat().st_size
            self.stats["size_after"] += path_new.stat().st_size

            # Update the status bar message
            self._status_msg()
            QCoreApplication.processEvents()  # Important, keep it!

        # Empty the paths to handle
        self.paths_list.clear()

        # And update the OK button state
        self.button_ok_state()


class DroppableQList(QListWidget):
    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)

        self.parent = parent

        # Accept drag'n drop
        self.setAcceptDrops(True)

        # Automatically sort the list
        self.setSortingEnabled(True)

    def exists(self, path: str) -> bool:
        return any(self.item(i).text() == path for i in range(self.count()))

    def dragEnterEvent(self, event: QEvent) -> None:
        if event.mimeData().hasUrls:
            event.accept()

    def dragMoveEvent(self, event: QEvent) -> None:
        if event.mimeData().hasUrls:
            event.accept()

    def dropEvent(self, event: QEvent) -> None:
        if not event.mimeData().hasUrls:
            return

        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if self.exists(path):
                continue
            self.addItem(path)
        event.accept()

        # Check the OK button, it may need to be enabled
        self.parent.button_ok_state()
