from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton, QTextEdit
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QFile, QTextStream
from features.backend import websocket_client
import json
class Wifi_status(QWidget):
    def __init__(self):
        super().__init__()

        # Charger le fichier CSS externe
        self._load_stylesheet("../styles.css")

        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Titre
        title = QLabel("WiFi Status")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("page_title")
        main_layout.addWidget(title)

        websocket_client.status_updated.connect(self.update_text_edit)
        websocket_client.data_received.connect(self.data_recived)

        # Zone de texte pour afficher les données reçues
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setObjectName("text_edit")

        # Zone de texte pour afficher les données reçues
        self.text_data = QTextEdit(self)
        self.text_data.setReadOnly(True)
        self.text_data.setObjectName("text_edit")

        # Bouton pour envoyer des données à l'ESP32
        self.send_button = QPushButton("Envoyer des données à l'ESP32", self)
        self.send_button.setObjectName("status_button")
        self.send_button.clicked.connect(self.send_data_to_esp32)

        # Grille principale
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)

        grid.addWidget(self.text_edit, 0, 0,1,2)
        grid.addWidget(self.text_data, 0, 2,1,2)
        grid.addWidget(self.send_button, 1, 0,1,4)

        # Ajouter la grille au layout principal avec un stretch factor
        main_layout.addLayout(grid, 1)

    def update_text_edit(self, message):
        """Ajoute un message à la zone de texte."""
        self.text_edit.append(message)

    def data_recived(self, message):
        """Ajoute un message à la zone de texte."""
        self.text_data.append(json.dumps(message))

    def send_data_to_esp32(self):
        """Envoie des données au serveur WebSocket."""
        data = {"test": "data", "value": 1}
        # Assuming websocket_client is defined elsewhere and initialized
        websocket_client.send_data(data)

    def _load_stylesheet(self, filename):
        """Charge un fichier CSS externe pour styliser l'interface."""
        file = QFile(filename)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
