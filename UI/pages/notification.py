from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QFile, QTextStream

class Notification(QWidget):
    def __init__(self):
        super().__init__()

        # Charger le fichier CSS externe
        self._load_stylesheet("../styles.css")

        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Titre
        title = QLabel("Notification System")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("page_title")
        main_layout.addWidget(title)

        # Grille principale
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)

        # Section Gaz et Fumée
        grid.addWidget(self.create_sensor_box("Configuration", "", "gas"),0, 0,2,2)
        grid.addWidget(self.create_sensor_box("Autorisation", "", "smoke"), 2, 0,2,1)

        # Ajouter la grille au layout principal avec un stretch factor
        main_layout.addLayout(grid, 1)

        # Optionnel: si vous voulez un petit espace en bas, vous pouvez rajouter un spacer
        # main_layout.addStretch()

    def create_sensor_box(self, title, icon, object_name):
        frame = QFrame()
        frame.setObjectName(object_name)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = QLabel(f"{icon}\n{title}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        layout.addWidget(label)
        frame.setLayout(layout)
        return frame

    def _load_stylesheet(self, filename):
        file = QFile(filename)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
