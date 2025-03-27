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
        self.warn_size = 200
        # Créer et démarrer le thread
        self.background_tasks = Background_tasks()
        self.background_tasks.signal1.connect(self.warning_frame)  # Connecter le signal à `call_me`
        self.background_tasks.start()
        #self.grid.addWidget(self.create_sensor_box("history", "", "smoke"), 2, 0,2,2)



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

    def _load_stylesheet(self, filename):
        file = QFile(filename)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
    def up(self):
        print("up")

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

        self.grid.addWidget(frame, 2, 2,2,2)
