import os
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QDialog,QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# 🔧 Force software rendering to avoid GPU issues
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
os.environ["QT_QUICK_BACKEND"] = "software"

class WebDialog(QDialog):
    def __init__(self, url: str):
        super().__init__()
        self.setWindowTitle("Web Viewer")
        self.resize(800, 600)

        # Créer la vue Web
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl(url))

        # Créer les boutons de navigation
        self.back_button = QPushButton("←")
        self.forward_button = QPushButton("→")

        self.back_button.clicked.connect(self.web_view.back)
        self.forward_button.clicked.connect(self.web_view.forward)

        # Organiser les boutons horizontalement
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)

        # Disposer les éléments verticalement
        layout = QVBoxLayout()
        layout.addLayout(nav_layout)
        layout.addWidget(self.web_view)
        self.setLayout(layout)