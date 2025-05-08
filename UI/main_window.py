from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel
from PyQt6.QtCore import Qt, QFile, QTextStream
from PyQt6.QtGui import QPixmap,QIcon
from pages.home import Home
from pages.notification import Notification
from pages.camera import Camera
from pages.identify import Identify
from pages.fire_detection import Fire_detection
from pages.shocks import Shock
from pages.wifi_status import Wifi_status
from features.backend import websocket_client
import json
from datetime import datetime
from features.functions import history

from features.browserWindow import camera

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gold Tech")
        self.setMinimumSize(1366 , 768 )

        # Démarrer le client WebSocket
        websocket_client.start()
        # Connexion aux signaux
        websocket_client.data_received.connect(self.on_data_received)
        websocket_client.status_updated.connect(self.on_status_updated)
        camera.init("http://goldtech_camera.local:81/stream", n_views=2)
        # Layouts


        # Configuration de l'interface
        self.central_widget = QWidget()
        self.setWindowIcon(QIcon("logo.png"))
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self._create_nav_bar()
        self._create_page_container()

        # Charger le style
        self._load_stylesheet("styles.css")

    def on_data_received( self,data):
        # print("Data received:", data)
        # print("Data received:", data['tempreture_value'])
        history(data)  # Appeler la fonction d'historique avec les données reçues
        file_path = "data.json"

        # Écrire les données dans un fichier JSON
        try:
            with open(file_path, "w", encoding="utf-8") as json_file:
                # Utiliser json.dump() pour écrire le dictionnaire dans un fichier JSON
                json.dump(data, json_file, indent=4, ensure_ascii=False)
            # print(f"Les données ont été enregistrées dans {file_path}")
        except Exception as e:
            print(f"Erreur lors de l'écriture dans le fichier : {e}")



    def on_status_updated( self,message):
        print("Status updated:", message)

    def _create_nav_bar(self):
        # Créer un widget container pour le layout
        nav_container = QWidget()
        nav_container.setObjectName("nav_container")  # ID pour le CSS

        nav_bar = QVBoxLayout(nav_container)
        nav_bar.setContentsMargins(0, 50, 0, 100)  # Marges intérieures
        nav_bar.setSpacing(20)  # Espace entre les boutons

        # 1) Ajouter un QLabel pour la photo
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png")
        # Redimensionner si nécessaire
        logo_label.setPixmap(logo_pixmap.scaled(
            60, 60,  # par exemple 60x60
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        # Centrer l'image dans le label
        logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        logo_label.setObjectName("logo")  # ID pour le CSS
        # Ajouter le label au layout
        nav_bar.addWidget(logo_label)

        # 2) Ajouter les boutons de navigation
        self.nav_buttons = []
        page_names = ["Home", "Fire", "Shocks","identify","Camera","Notification","Wifi status"]  # Noms personnalisés

        for i in range(7):
            btn = QPushButton(page_names[i])
            btn.setObjectName("nav_button")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=i: self._switch_page(i))
            nav_bar.addWidget(btn)
            self.nav_buttons.append(btn)

        self.nav_buttons[0].setChecked(True)
        self.main_layout.addWidget(nav_container)  # Ajouter le container

    def _create_page_container(self):
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("page_container")

        # Créer les pages
        self.pages = [
            Home(),
            Fire_detection(),
            Shock(),
            Identify(),
            Camera(),
            Notification(),
            Wifi_status()
        ]

        for page in self.pages:
            self.stacked_widget.addWidget(page)

        self.main_layout.addWidget(self.stacked_widget)

    def _switch_page(self, index):
        for btn in self.nav_buttons:
            btn.setChecked(False)
        self.nav_buttons[index].setChecked(True)
        self.stacked_widget.setCurrentIndex(index)

    def _load_stylesheet(self, filename):
        file = QFile(filename)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()