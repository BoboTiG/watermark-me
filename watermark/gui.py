"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from pathlib import Path

from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)

from .constants import COMPANY, PRODUCT, TITLE
from .watermark import apply_watermarks


class Application(QApplication):
    """Main window."""

    def __init__(self) -> None:
        QApplication.setOrganizationName(COMPANY)

        super().__init__([])
        self.setApplicationName(PRODUCT)

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

        self._window()

    def _window(self) -> None:
        """Construct the actual window.
        Return a tuple: watermark text, watermak icon path.
        """

        def _select_one_file(self) -> None:
            """Choose an image to use as a watermark picture."""
            image = "Image (*.png *.jpg *.bmp)"
            path, _ = QFileDialog.getOpenFileName(
                caption="Select a watermark picture", filter=image
            )

            picture.setText(path)

        dialog = QDialog()
        dialog.setWindowTitle(TITLE)
        # dialog.setWindowIcon(icon)
        layout = QVBoxLayout()

        # 1st line: label + watermark text
        layout_text = QHBoxLayout()
        lbl_text = QLabel("Texte")
        layout.addWidget(lbl_text)
        text = QLineEdit("www.arresto-momentum.com")
        layout_text.addWidget(lbl_text)
        layout_text.addWidget(text)
        layout.insertLayout(0, layout_text)

        # 2nd line: label + watermark icon
        layout_picture = QHBoxLayout()
        lbl_picture = QLabel("Icône")
        picture = QLineEdit()
        picture.setReadOnly(True)
        btn_choose_file = QPushButton("Add")
        btn_choose_file.clicked.connect(_select_one_file)
        layout_picture.addWidget(lbl_picture)
        layout_picture.addWidget(picture)
        layout_picture.addWidget(btn_choose_file)
        layout.insertLayout(1, layout_picture)

        # Buttons
        buttons = QDialogButtonBox()
        buttons.setStandardButtons(QDialogButtonBox.Ok)
        buttons.clicked.connect(dialog.close)
        layout.addWidget(buttons)

        # Files list
        paths_list = MyListWidget()
        layout.addWidget(paths_list)

        dialog.setLayout(layout)
        dialog.resize(400, 400)
        dialog.show()
        dialog.exec_()

        paths = [Path(paths_list.item(i).text()) for i in range(paths_list.count())]
        if paths:
            apply_watermarks(paths, text.text(), picture.text())


class MyListWidget(QListWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setSortingEnabled(True)

    def dropEvent(self, event: QEvent) -> None:
        for url in event.mimeData().urls():
            self.addItem(url.path())
            event.acceptProposedAction()
