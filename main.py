"""Formula OCR Desktop App - Entry Point.

Recognize mathematical formulas from images and output LaTeX / Word formats.
"""

import sys
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.paths import app_root
from ui.main_window import MainWindow
from ui.theme import APP_NAME, LOGO_PATH, app_stylesheet


def main():
    os.chdir(app_root())

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setStyleSheet(app_stylesheet())
    app.setWindowIcon(QIcon(str(LOGO_PATH)))

    window = MainWindow(app_clipboard=app.clipboard())
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
