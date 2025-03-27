from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame, QSpacerItem, QSizePolicy,QPushButton,QToolButton
from PyQt6.QtGui import QFont,QIcon
from PyQt6.QtCore import Qt, QFile, QTextStream,QSize
from features.videoPlayer import VideoPlayer

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
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)

        # Section Gaz et Fumée
        grid.addWidget(self.video_frame(),0, 0,2,2)
        grid.addWidget(self.create_sensor_box("history", "", "smoke"), 2, 0,2,2)
        grid.addWidget(self.cam_controler(),0, 2,2,2)
        grid.addWidget(self.create_sensor_box("warning", "", "smoke"), 2, 2,2,2)

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
        up_button = self.create_button("pages/images/up.png")
        up_button.clicked.connect(self.up)
        down_button = self.create_button("pages/images/down.png")
        left_button = self.create_button("pages/images/left.png")
        right_button = self.create_button("pages/images/right.png")
        reset_button = self.create_button("pages/images/reset.png")
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

        return frame


    def video_frame(self):
        self.video_player = VideoPlayer()
        frame = QFrame()
        frame.setObjectName("video")
        frame.setLayout(self.video_player.play_video())
        return frame

    def _load_stylesheet(self, filename):
        file = QFile(filename)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
    def up(self):
        print("up")
