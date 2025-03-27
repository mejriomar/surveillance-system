from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont,QPixmap
from PyQt6.QtCore import Qt, QFile, QTextStream
import json
from features.background_tasks import Background_tasks

class Home(QWidget):
    def __init__(self):
        super().__init__()

        # Charger le fichier CSS externe
        self._load_stylesheet("../styles.css")

        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Titre
        title = QLabel("Welcome to Gold Tech Innovation")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("page_title")
        main_layout.addWidget(title)

        # Grille principale
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(10)
        self.warn_size = 100
        self.background_tasks = Background_tasks()
        self.background_tasks.signal1.connect(self.warning_frame)  # Connecter le signal à `call_me`
        self.background_tasks.start()
        # Section Gaz et Fumée
        self.grid.addWidget(self.create_sensor_box("Gaz", "🔥", "gas"),     0, 0)
        self.grid.addWidget(self.create_sensor_box("Fumée", "🔥", "smoke"), 0, 1)

        # Température
        self.grid.addWidget(self.create_sensor_box("Température", "🌡️ 30", "temperature"), 1, 0, 1, 2)

        # Vidéo en direct
        self.grid.addWidget(self.create_sensor_box("Video", "", "video"), 0, 2, 2, 2)

        # Section Accès et Voix
        self.grid.addWidget(self.create_sensor_box("Accès", "🔒", "access"),  2, 0)


        # Section Chocs détectés
        self.grid.addWidget(self.create_sensor_box("Porte", "⚠️ Chocs détectés", "shock"),   2, 2)
        self.grid.addWidget(self.create_sensor_box("Fenêtre", "⚠️ Chocs détectés", "shock"), 2, 3)

        # Ajouter la grille au layout principal avec un stretch factor
        main_layout.addLayout(self.grid, 1)

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

    def warning_frame(self):

        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        movement = data["movement"]
        # 1) Ajouter un QLabel pour la photo
        warning_label = QLabel()
        warning_label_text = QLabel()

        if movement == 1:
            warning_pixmap = QPixmap("pages/images/warning/motion.png")
            self.warn_size = self.warn_size + 100 if self.warn_size < 200 else 100
            warning_label_text.setText("Motion detected !")
            warning_label_text.setStyleSheet("color: #FF9800;")
        else:
            self.warn_size = 200
            warning_pixmap = QPixmap("pages/images/warning/no_motion.png")
            warning_label_text.setText("No motion detected !")
            warning_label_text.setStyleSheet("color: green;")

        warning_label.setPixmap(warning_pixmap.scaled(
            self.warn_size, self.warn_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

        warning_label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label_text.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        warning_label_text.setObjectName("warning_text")
        warning_label_text.setContentsMargins(0, 0, 0, 0)

        # Centrer l'image dans le label
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setObjectName("warning")  # ID pour le CSS
        warning_label.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()
        layout.addWidget(warning_label)
        layout.addWidget(warning_label_text)
        layout.setSpacing(0)
        frame = QFrame()
        frame.setObjectName("video")
        frame.setLayout(layout)

        self.grid.addWidget(frame, 2, 1)

    def _load_stylesheet(self, filename):
        file = QFile(filename)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
