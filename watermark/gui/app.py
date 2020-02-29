"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from pathlib import Path
from threading import Thread

from PyQt5.QtCore import QEvent, QTimer, Qt, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
    qApp,
)
import tinify

from .settings import Settings
from .utils import set_style
from ..translator import TR
from .. import __version__
from ..conf import CONF
from ..constants import COMPANY, FREEZER, RES_DIR, TITLE, WINDOWS
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

        # Init the GUI
        self._settings = Settings()
        self._toolbar()
        self.addToolBar(self.toolbar)
        self._status_bar()
        self.setStatusBar(self.status_bar)
        self._status_msg()
        self._window()
        self.button_ok_state()

        self._check_for_update()

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
        if not (CONF.update and FREEZER and WINDOWS):
            return

        from ..updater.windows import Updater

        updater = Updater(self._status_msg)
        Thread(target=updater.check, args=(__version__,)).start()

    def _select_one_file(self) -> None:
        """Choose an image to use as a watermark picture."""
        image = "Image (*.png *.jpg *.bmp)"
        path, _ = QFileDialog.getOpenFileName(
            caption=TR.get("TITLE_SEL_PICTURE", [TITLE]), filter=image
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
            values = [str(self.stats["count"]), sizeof_fmt(win, suffix=TR.get("BYTE"))]
            msg = TR.get("STATISTICS", values)
            if self.use_optimization:
                msg += TR.get("STATISTICS_TINIFY", [tinify.compression_count])

        self.status_bar.showMessage(msg)
        QCoreApplication.processEvents()  # Important, keep it!

    def _toolbar(self) -> QToolBar:
        """Create the toolbar."""
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setMovable(False)

        # Icon: settings
        settings_action = QAction(
            QIcon(str(RES_DIR / "settings.svg")), TR.get("TB_SETTINGS"), self
        )
        settings_action.triggered.connect(self._settings.exec_)
        self.toolbar.addAction(settings_action)

        # Icon: about
        about_action = QAction(
            QIcon(str(RES_DIR / "about.svg")), TR.get("TB_ABOUT"), self
        )
        about_action.triggered.connect(show_about)
        self.toolbar.addAction(about_action)

        self.toolbar.addSeparator()

        # Icon: exit
        exit_action = QAction(QIcon(str(RES_DIR / "exit.svg")), TR.get("TB_EXIT"), self)
        exit_action.triggered.connect(qApp.quit)
        self.toolbar.addAction(exit_action)

    def _add_group_text(self) -> QGroupBox:
        """Group box for the text watermark."""
        groupbox = QGroupBox(TR.get("TEXT"))
        vbox = QVBoxLayout()
        groupbox.setLayout(vbox)

        # The text watermark input
        self.text = QLineEdit(CONF.text)
        self.text.setPlaceholderText(TR.get("TEXT_PLACEHOLDER"))
        self.text.setClearButtonEnabled(True)
        self.text.textChanged.connect(self.button_ok_state)
        set_style(self.text)
        vbox.addWidget(self.text)

        return groupbox

    def _add_group_picture(self) -> QGroupBox:
        """Group box for the picture watermark."""
        groupbox = QGroupBox(TR.get("ICON"))
        vbox = QHBoxLayout()
        groupbox.setLayout(vbox)

        # The watermark picture input
        self.picture = QLineEdit(CONF.picture)
        self.picture.setPlaceholderText(TR.get("ICON_PLACEHOLDER"))
        self.picture.setClearButtonEnabled(True)
        self.picture.textChanged.connect(self.button_ok_state)
        set_style(self.picture)
        vbox.addWidget(self.picture)

        # The button to choose a local file
        btn_choose_file = QPushButton(
            QIcon(str(RES_DIR / "open.svg")), TR.get("CHOOSE")
        )
        btn_choose_file.setFlat(True)
        btn_choose_file.clicked.connect(self._select_one_file)
        vbox.addWidget(btn_choose_file)

        return groupbox

    def _add_group_files_list(self) -> QGroupBox:
        """Group box for the files list."""
        groupbox = QGroupBox(TR.get("FILES"))
        vbox = QHBoxLayout()
        groupbox.setLayout(vbox)

        self.paths_list = DroppableQList(self)
        vbox.addWidget(self.paths_list)

        return groupbox

    def _window(self) -> None:
        """Construct the main window."""
        layout = QVBoxLayout()

        # The central widget
        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(layout)

        layout.addWidget(self._add_group_text())
        layout.addWidget(self._add_group_picture())
        layout.addWidget(self._add_group_files_list())

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


def show_about() -> None:
    """display a simple "About" dialog."""
    icon = str(RES_DIR / "logo.svg")

    msg = QMessageBox()
    msg.setWindowTitle(TR.get("TITLE_ABOUT", [TITLE]))
    msg.setWindowIcon(QIcon(icon))
    msg.setIconPixmap(QPixmap(icon).scaledToWidth(64))

    msg.setText(f"{TITLE} v{__version__}")
    codename = TR.get("CODENAME", ["Colossos"])
    msg.setInformativeText(f"{codename}\n© 2019-2020 {COMPANY}")

    from platform import python_implementation, python_version

    msg.setDetailedText(
        f"{python_implementation()} {python_version()}\n"
        f"Pillow 7.0.0\n"
        f"PyInstaller 3.6\n"
        f"PyQt5 5.13.2\n"
        f"PyYAML 5.3\n"
        f"Tendo 0.2.15\n"
        f"Tinify 1.5.1"
    )

    msg.setStandardButtons(QMessageBox.Close)
    msg.exec_()
