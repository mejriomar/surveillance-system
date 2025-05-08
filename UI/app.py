import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
import signal
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
