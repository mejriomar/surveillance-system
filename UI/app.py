import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from PyQt6.QtGui import QIcon


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())