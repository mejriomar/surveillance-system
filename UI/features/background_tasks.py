import sys
import time
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

class Background_tasks(QThread):
    signal1 = pyqtSignal()  # Signal pour appeler

    def run(self):
        while True:
            self.signal1.emit()
            time.sleep(0.5)

class Background_tasks_nn(QThread):
    signal1 = pyqtSignal()  # Signal pour appeler

    def run(self):
        self.signal1.emit()