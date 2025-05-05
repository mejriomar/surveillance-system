import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QTabWidget, QPushButton,QHeaderView
)
from PyQt6.QtCore import Qt

class EventHistoryWidget(QWidget):
    def __init__(self, *events):
        super().__init__()
        self.events = events  # Liste des événements à afficher

        # Configuration de la fenêtre
        # self.setGeometry(100, 100, 800, 600)  # Taille initiale
        # self.resize_to_fullscreen()  # Plein écran

        # Initialisation de l'interface
        self.layout = QVBoxLayout()
        # Onglets pour chaque événement
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Créer un onglet pour chaque événement
        for event in self.events:
            tab = QWidget()
            tab_layout = QVBoxLayout()

            # Titre de l'onglet
            tab_title = QLabel(f"'{event.capitalize()}' History")
            tab_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tab_title.setObjectName("tab_title")  # ID pour le CSS
            tab_layout.addWidget(tab_title)

            # Tableau pour afficher les données
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Detected Date", "Fixed Date"])
            tab_layout.addWidget(table)

            # Appliquer le layout à l'onglet
            tab.setLayout(tab_layout)

            # Ajouter l'onglet au widget d'onglets
            self.tabs.addTab(tab, event.capitalize())

            # Charger et afficher les données pour cet événement
            self.load_and_display_history(event, table)

        # Appliquer le layout principal
        self.setLayout(self.layout)

    def resize_to_fullscreen(self):
        """Ajuste la fenêtre pour qu'elle occupe tout l'écran."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)

    def load_and_display_history(self, event, table):
        """Charge les données depuis history.json et les affiche dans le tableau spécifié."""
        try:
            with open('history.json', 'r') as f:
                history_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history_data = {}

        # Récupérer les données pour l'événement spécifié
        events = history_data.get(event, [])

        # Configurer le tableau
        table.setRowCount(len(events))
        # table.horizontalHeader().setStretchLastSection(True)  # Étendre la dernière section
        # table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Colonnes de même largeur
        for row, event_data in enumerate(events):
            detected_date, fixed_date = event_data

            # Ajouter la date de détection
            detected_item = QTableWidgetItem(detected_date)
            detected_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrer le texte
            detected_item.setForeground(Qt.GlobalColor.black)  # Couleur du texte en noir
            detected_item.setFlags(detected_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Lecture seule
            table.setItem(row, 0, detected_item)

            # Ajouter la date de résolution (si elle existe)
            fixed_item = QTableWidgetItem(fixed_date if fixed_date else "Non résolu")
            fixed_item.setFlags(fixed_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Lecture seule
            fixed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrer le texte
            fixed_item.setForeground(Qt.GlobalColor.black)  # Couleur du texte en noir
            table.setItem(row, 1, fixed_item)

        # Ajuster la taille des colonnes
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)  # Étendre la dernière section
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Colonnes de même largeur

    def refresh_history(self):
        """Rafraîchit l'historique pour tous les événements."""
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            event = self.tabs.tabText(index).lower()  # Nom de l'événement en minuscules
            table = tab.findChild(QTableWidget)  # Récupérer le tableau dans l'onglet
            if table:
                self.load_and_display_history(event, table)