from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QFile, QTextStream
import json
from features.background_tasks import Background_tasks
from features.functions import dynamic_resize_image, dynamic_resize_text

class Identify(QWidget):
    def __init__(self):
        super().__init__()

        # Charger le fichier CSS externe
        self._load_stylesheet("../styles.css")

        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Titre
        title = QLabel("Access verification and voice detection")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("page_title")
        main_layout.addWidget(title)

        # Grille principale
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(10)
        main_layout.addLayout(self.grid, 1)

        # Initialisation d'attributs pour le caching et la réutilisation
        self.pixmap_cache = {}
        self.data = self._load_json("data.json")
        self.warn_size = {}  # Taille initiale
        self.warning_frames = {}  # Dictionnaire pour stocker plusieurs widgets d'avertissement

        # Démarrer les tâches en arrière-plan
        self.background_tasks = Background_tasks()
        self.background_tasks.signal1.connect(self.repetitive)
        self.background_tasks.start()

    def _load_json(self, filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_pixmap(self, path):
        """Retourne un QPixmap mis en cache pour éviter de recharger l'image à chaque fois."""
        if path not in self.pixmap_cache:
            self.pixmap_cache[path] = QPixmap(path)
        return self.pixmap_cache[path]

    def create_warning_frame(self):
        """Crée un widget d'avertissement qui sera mis à jour ultérieurement."""
        frame = QFrame()
        frame.setObjectName("video")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Label pour l'image
        warning_label = QLabel()
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setObjectName("warning")
        warning_label.setContentsMargins(0, 0, 0, 0)

        # Label pour le texte d'avertissement
        warning_text_label = QLabel()
        warning_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_text_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        warning_text_label.setObjectName("warning_text")
        warning_text_label.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(warning_label)
        layout.addWidget(warning_text_label)

        # Conserver les références pour une mise à jour facile
        frame.warning_label = warning_label
        frame.warning_text_label = warning_text_label
        return frame

    def warning_frame(self, warn_conf):

        """
        Met à jour ou crée un widget d'avertissement avec les informations fournies dans warn_conf.
        Chaque widget est indexé par sa position (row, column) pour garantir l'unicité.
        """
        warn_max_size = 80
        warn_size_variable = 25  # Valeur de taille variable pour l'animation
        grid_pos = warn_conf["grid_position"]
        # Utiliser la position comme clé unique (row, column)
        key = (grid_pos["row"], grid_pos["column"])
        if key not in self.warning_frames:
            frame = self.create_warning_frame()
            self.warning_frames[key] = frame
            self.grid.addWidget(frame,
                                grid_pos["row"],
                                grid_pos["column"],
                                grid_pos["row_n"],
                                grid_pos["column_n"])
            self.warn_size[key] = warn_max_size  # Taille initiale pour chaque avertissement
        else:
            frame = self.warning_frames[key]

        # Recharger les données JSON
        self.data = self._load_json("data.json")
        # Récupérer la valeur pour ce type d'avertissement
        warn_status = self.data.get(warn_conf["warning_type"], 0)

        if warn_status == 1:
            self.warn_size[key] = self.warn_size[key] + warn_max_size - warn_size_variable if self.warn_size[key] < warn_max_size else warn_max_size - warn_size_variable

            pixmap = self.get_pixmap(warn_conf["warning_icon"])
            frame.warning_text_label.setText(warn_conf["warning_text"])
            frame.warning_text_label.setStyleSheet(warn_conf["warning_color"])
        else:
            self.warn_size[key] = warn_max_size
            pixmap = self.get_pixmap(warn_conf["no_warning_icon"])
            frame.warning_text_label.setText(warn_conf["no_warning_text"])
            frame.warning_text_label.setStyleSheet(warn_conf["no_warning_color"])

        # Mettre à jour l'image en redimensionnant le pixmap
        dynamic_resize_image(frame, frame.warning_label, pixmap, percentage=0.3, max_size=self.warn_size[key])
        dynamic_resize_text(frame, frame.warning_text_label, percentage=0.05, min_font_size=10, max_font_size=20)

    def repetitive(self):
        """Méthode appelée périodiquement par Background_tasks pour mettre à jour les avertissements."""

        # Exemple de configuration pour un avertissement de gaz
        flame_warning_conf = {
            "warning_type": "access",
            "warning_text": "Access detected!",
            "no_warning_text": "No detected",
            "no_warning_icon": "pages/images/warning/no_access.png",
            "warning_icon": "pages/images/warning/access.png",
            "warning_color": "color: orange;",
            "no_warning_color": "color: green;",
            "grid_position": {
                "row": 0,
                "column": 0,
                "row_n": 1,
                "column_n": 2
            }
        }
        self.warning_frame(flame_warning_conf)

        temperature_warning_conf = {
            "warning_type": "voice",
            "warning_text": "Voice detected!",
            "no_warning_text": "No voice detected!",
            "no_warning_icon": "pages/images/warning/no_voice.png",
            "warning_icon": "pages/images/warning/voice.png",
            "warning_color": "color: orange;",
            "no_warning_color": "color: green;",
            "grid_position": {
                "row": 0,
                "column": 2,  # Position différente pour éviter le chevauchement
                "row_n": 1,
                "column_n": 2
            }
        }
        self.warning_frame(temperature_warning_conf)

        temperature_warning_conf = {
            "warning_type": "window",
            "warning_text": "Broken windo detected!",
            "no_warning_text": "Closed",
            "no_warning_icon": "pages/images/warning/no_window.png",
            "warning_icon": "pages/images/warning/window.png",
            "warning_color": "color: orange;",
            "no_warning_color": "color: green;",
            "grid_position": {
                "row": 1,
                "column": 0,  # Position différente pour éviter le chevauchement
                "row_n": 2,
                "column_n": 4
            }
        }
        self.warning_frame(temperature_warning_conf)

    def _load_stylesheet(self, filename):
        file = QFile(filename)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
