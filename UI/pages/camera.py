from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame, QSpacerItem, QSizePolicy,QPushButton,QToolButton
from PyQt6.QtGui import QFont,QIcon,QPixmap
from PyQt6.QtCore import Qt, QFile, QTextStream,QSize,QThread, pyqtSignal
from features.videoPlayer import VideoPlayer
from features.background_tasks import Background_tasks
import json
import time



class Camera(QWidget):
    def __init__(self):
        super().__init__()

        # Charger le fichier CSS externe
        self._load_stylesheet("../styles.css")

        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Titre
        title = QLabel("Surveillance camera")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("page_title")
        main_layout.addWidget(title)

        # Grille principale
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(10)
        self.video_frame()
        self.cam_controler()

        # Initialisation d'attributs pour le caching et la réutilisation
        self.pixmap_cache = {}
        self.data = self._load_json("data.json")
        self.warn_size = 100  # Taille initiale
        self.warning_frames = {}  # Dictionnaire pour stocker plusieurs widgets d'avertissement

        # Démarrer les tâches en arrière-plan
        self.background_tasks = Background_tasks()
        self.background_tasks.signal1.connect(self.repetitive)
        self.background_tasks.start()




        # Ajouter la grille au layout principal avec un stretch factor
        main_layout.addLayout(self.grid, 1)


    def create_button(self,icon_path):
        button = QToolButton()
        button.setIcon(QIcon(icon_path))
        button.setMinimumSize(80, 80)  # Taille minimale du bouton
        button.setIconSize(QSize(80, 80))  # Taille de l'icône
        button.setAutoRaise(True)  # Effet de surbrillance au survol
        button.setObjectName("control_button")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def cam_controler(self):
        up_button = self.create_button("pages/images/cam_controler/up.png")
        up_button.clicked.connect(self.up)
        down_button = self.create_button("pages/images/cam_controler/down.png")
        left_button = self.create_button("pages/images/cam_controler/left.png")
        right_button = self.create_button("pages/images/cam_controler/right.png")
        reset_button = self.create_button("pages/images/cam_controler/reset.png")
        reset_button.setIconSize(QSize(50, 50))  # Taille de l'icône
        # Configuration du layout en grille
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)

        layout.addWidget(up_button, 0, 1,Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(left_button, 1, 0,Qt.AlignmentFlag.AlignRight)
        layout.addWidget(reset_button, 1, 1,Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(right_button, 1, 2,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(down_button, 2, 1,Qt.AlignmentFlag.AlignTop)

        # Encapsulation dans un QFrame
        frame = QFrame()
        frame.setObjectName("video")
        frame.setLayout(layout)

        self.grid.addWidget(frame,0, 2,2,2)


    def video_frame(self):
        self.video_player = VideoPlayer()
        frame = QFrame()
        frame.setObjectName("video")
        frame.setLayout(self.video_player.play_video())
        self.grid.addWidget(frame,0, 0,4,2)
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
        else:
            frame = self.warning_frames[key]

        # Recharger les données JSON
        self.data = self._load_json("data.json")
        # Récupérer la valeur pour ce type d'avertissement
        warn_status = self.data.get(warn_conf["warning_type"], 0)

        if warn_status == 1:
            # Augmentation progressive de la taille
            self.warn_size = self.warn_size + 100 if self.warn_size < 200 else 100
            pixmap = self.get_pixmap(warn_conf["warning_icon"])
            frame.warning_text_label.setText(warn_conf["warning_text"])
            frame.warning_text_label.setStyleSheet(warn_conf["warning_color"])
        else:
            self.warn_size = 200
            pixmap = self.get_pixmap(warn_conf["no_warning_icon"])
            frame.warning_text_label.setText(warn_conf["no_warning_text"])
            frame.warning_text_label.setStyleSheet(warn_conf["no_warning_color"])

        # Mettre à jour l'image en redimensionnant le pixmap
        frame.warning_label.setPixmap(pixmap.scaled(
            self.warn_size, self.warn_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    def repetitive(self):
        """Méthode appelée périodiquement par Background_tasks pour mettre à jour les avertissements."""
        # Exemple de configuration pour un avertissement de mouvement
        motion_warning_conf = {
            "warning_type": "movement",
            "warning_text": "Motion detected!",
            "no_warning_text": "No motion detected",
            "no_warning_icon": "pages/images/warning/no_motion.png",
            "warning_icon": "pages/images/warning/motion.png",
            "warning_color": "color: #FF9800;",
            "no_warning_color": "color: green;",
            "grid_position": {
                "row": 2,
                "column": 2,
                "row_n": 2,
                "column_n": 2
            }
        }
        self.warning_frame(motion_warning_conf)
    def _load_stylesheet(self, filename):
        file = QFile(filename)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
    def up(self):
        print("up")


