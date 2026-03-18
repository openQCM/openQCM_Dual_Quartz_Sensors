"""Entry point — run with: python -m openqcm"""

import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from .gui.style import STYLESHEET
from .gui.main_window import MainWindow

_ICON_DIR = os.path.join(os.path.dirname(__file__), "gui", "assets")
if hasattr(sys, "_MEIPASS"):
    _ICON_DIR = os.path.join(sys._MEIPASS, "openqcm", "gui", "assets")
_ICON_PATH = os.path.join(_ICON_DIR, "openqcm.ico")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    if os.path.exists(_ICON_PATH):
        app.setWindowIcon(QIcon(_ICON_PATH))

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
