from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame, QSpacerItem, QSizePolicy,QPushButton,QToolButton,QHBoxLayout
from PyQt6.QtGui import QFont,QIcon,QPixmap
from PyQt6.QtCore import Qt, QFile, QTextStream,QSize,QThread, pyqtSignal,QTimer
from features.background_tasks import Background_tasks, Background_tasks_nn
import json
import time
from features.functions import dynamic_resize_image, dynamic_resize_text, resize_button_icon,send_http_get,send_http_get_asnych
from features.backend import websocket_client
from features.backend import websocket_client
from features.history_ui import EventHistoryWidget
from features.browserWindow import camera
from features.webDialog import WebDialog
from datetime import datetime

class ToastNotification(QLabel):
    def __init__(self, message: str, parent=None):
        super().__init__(message, parent)
        self.setStyleSheet("""
            background-color: rgba(255, 165, 0, 220);
            color: black;
            border: 2px solid black;
            border-radius: 8px;
            padding: 8px;
            font-weight: bold;
        """)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.adjustSize()
        self.timer = QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.hide)

    def show_notification(self, x, y):
        self.move(x, y)
        self.show()
        self.timer.start()


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
        # Titre
        title = QLabel("Surveillance camera")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("page_title")

        self.record_button = self.create_button("pages/images/cam_controler/no_rec.png")
        self.record_button.setCheckable(True)
        self.enble_auto_rec_button = self.create_button("pages/images/cam_controler/no_auto_rec.png")
        self.enble_auto_rec_button.setCheckable(True)
        self.enble_auto_rec_button.clicked.connect(self.auto_record)

        self.ip_addaress = "http://goldtech_camera.local"

        self.config_button = self.create_button("pages/images/cam_controler/conf.png")
        self.config_button.clicked.connect(self.open_web_dialog)
        camera.grabber.motion_detected.connect(self.show_motion_alert)
        self.is_reccording = False
        self.is_auto_reccording = False
        self.timer_reccording = QTimer(self)
        self.timer_reccording.setInterval(10000)


        self.record_button.clicked.connect(self.start_record)
        camera.stop_recording()


        title_layout = QHBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(self.record_button)
        title_layout.addWidget(self.config_button)
        title_layout.addWidget(self.enble_auto_rec_button)
        main_layout.addLayout(title_layout)

        # Grille principale
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(10)
        # history
        events_to_display = ("movement","m")  # Événements à afficher
        self.history = EventHistoryWidget(*events_to_display)
        self.grid.addWidget(self.history, 0, 2,2,1)  # Correction ici
        websocket_client.data_received.connect(self.on_data_received)

        # start_camera after 3 seconds
        self.start_camera = QTimer(self)
        self.start_camera.setInterval(3000)
        self.start_camera.timeout.connect(self.start_camera_delay)
        self.start_camera.start()

        self.button_layout = QGridLayout()
        self.grid.addLayout(self.get_h_views(),0, 0,1,2)
        self.cam_controler()

        # Initialisation d'attributs pour le caching et la réutilisation
        self.pixmap_cache = {}
        self.data = self._load_json("data_movemnt.json")
        self.warn_size = 100  # Taille initiale
        self.warning_frames = {}  # Dictionnaire pour stocker plusieurs widgets d'avertissement
        self.warn_size = {}  # Taille initiale

        # Démarrer les tâches en arrière-plan
        self.background_tasks = Background_tasks()
        self.background_tasks.signal1.connect(self.repetitive)
        self.background_tasks.start()
        # Ajouter la grille au layout principal avec un stretch factor
        main_layout.addLayout(self.grid, 1)

        send_http_get_asnych(self.ip_addaress + "/ip", None, self.get_ip)

    def start_camera_delay(self):
        camera.start_camera()
        self.start_camera.stop()  # Arrêter le timer après le démarrage de la caméra

    def show_motion_alert(self):
        toast = ToastNotification("⚠️ Mouvement détecté !", self)
        x = self.width() - toast.width() - 20
        y = self.height() - toast.height() - 20

        toast.show_notification(x, y)
        if self.is_reccording == False:
            # print(f"is_auto_reccording = {self.is_auto_reccording}")
            if self.is_auto_reccording == True:
                self.is_reccording = True
                # modify_json("movement", True)
                camera.start_recording()
                self.timer_reccording.timeout.connect(self.movement_stope_reccording)
                self.timer_reccording.start()
                data =self._load_json("data_movemnt.json")
                data["movement"] = True
                self.history_save(data)
                self.history.refresh_history()
                # print("Recording started")

    def movement_stope_reccording(self):
        self.is_reccording = False
        # modify_json("movement", False)
        data =self._load_json("data_movemnt.json")
        data["movement"] = False
        self.history_save(data)
        self.history.refresh_history()
        camera.stop_recording()
        self.timer_reccording.stop()



    def open_web_dialog(self):
        dialog = WebDialog("http://goldtech_camera.local")
        dialog.exec()

    def on_data_received(self, data):
        self.history.refresh_history()

    def create_button(self,icon_path):
        button = QToolButton()
        button.setIcon(QIcon(icon_path))
        resize_button_icon(button, self.width(), self.height(), scale_factor=0.12)  # Redimensionner l'icône
        button.setAutoRaise(True)  # Effet de surbrillance au survol
        button.setObjectName("control_button")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def cam_controler(self):
        up_button = self.create_button("pages/images/cam_controler/up.png")
        up_button.clicked.connect(self.up)
        down_button = self.create_button("pages/images/cam_controler/down.png")
        down_button.clicked.connect(self.down)
        left_button = self.create_button("pages/images/cam_controler/left.png")
        left_button.clicked.connect(self.left)
        right_button = self.create_button("pages/images/cam_controler/right.png")
        right_button.clicked.connect(self.right)
        self.reset_button = self.create_button("pages/images/cam_controler/reset.png")
        self.reset_button.setCheckable(True)
        self.reset_button.clicked.connect(self.reset)
        self.reset_button.setIconSize(QSize(30, 30))  # Taille de l'icône
        # Configuration du layout en grille
        self.button_layout.setContentsMargins(10, 10, 10, 10)
        self.button_layout.setHorizontalSpacing(0)
        self.button_layout.setVerticalSpacing(0)

        self.button_layout.addWidget(up_button, 0, 1,Qt.AlignmentFlag.AlignBottom)
        self.button_layout.addWidget(left_button, 1, 0,Qt.AlignmentFlag.AlignRight)
        self.button_layout.addWidget(self.reset_button, 1, 1,Qt.AlignmentFlag.AlignCenter)
        self.button_layout.addWidget(right_button, 1, 2,Qt.AlignmentFlag.AlignLeft)
        self.button_layout.addWidget(down_button, 2, 1,Qt.AlignmentFlag.AlignTop)

        self.button_layout.up_button = up_button
        self.button_layout.down_button = down_button
        self.button_layout.left_button = left_button
        self.button_layout.right_button = right_button
        self.button_layout.reset_button = self.reset_button

        self.grid.addLayout(self.button_layout,1, 1,1,1)

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
        warning_text_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
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
        warn_max_size = 100
        warn_size_variable = 50  # Valeur de taille variable pour l'animation
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
        self.data = self._load_json("data_movemnt.json")
        # Récupérer la valeur pour ce type d'avertissement
        warn_status = self.data.get(warn_conf["warning_type"], 0)

        if warn_status == 1:
            # self.warn_size[key] = self.warn_size[key] + warn_max_size - warn_size_variable if self.warn_size[key] < warn_max_size else warn_max_size - warn_size_variable

            pixmap = self.get_pixmap(warn_conf["warning_icon"])
            frame.warning_text_label.setText(warn_conf["warning_text"])
            frame.warning_text_label.setStyleSheet(warn_conf["warning_color"])
        else:
            # self.warn_size[key] = warn_max_size
            pixmap = self.get_pixmap(warn_conf["no_warning_icon"])
            frame.warning_text_label.setText(warn_conf["no_warning_text"])
            frame.warning_text_label.setStyleSheet(warn_conf["no_warning_color"])

        frame.warning_label.setPixmap(pixmap.scaled(self.warn_size[key], self.warn_size[key], Qt.AspectRatioMode.KeepAspectRatio))
        # Mettre à jour l'image en redimensionnant le pixmap
        # dynamic_resize_image(frame, frame.warning_label, pixmap, percentage=0.3, max_size=self.warn_size[key])
        dynamic_resize_text(frame, frame.warning_text_label, percentage=0.05, min_font_size=5, max_font_size=10)

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
                "row": 1,
                "column": 0,
                "row_n": 1,
                "column_n": 1
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
        send_http_get_asnych(self.ip_addaress + "/servo", {"dir": "up"})
    def down(self):
        send_http_get_asnych(self.ip_addaress + "/servo", {"dir": "down"})
    def left(self):
        send_http_get_asnych(self.ip_addaress + "/servo", {"dir": "left"})
    def right(self):
        send_http_get_asnych(self.ip_addaress + "/servo", {"dir": "right"})
    def reset(self):
        # ip = send_http_get(self.ip_addaress + "/ip")
        # self.ip_addaress = "http://"+ip
        if self.reset_button.isChecked():
            send_http_get_asnych(self.ip_addaress + "/servo", {"dir": "led_on"})
        else:
            send_http_get_asnych(self.ip_addaress + "/servo", {"dir": "led_off"})



    def get_ip(self,result):
        self.ip_addaress = "http://"+result
        print(self.ip_addaress)


    def get_h_views(self):
        self.h_views = QHBoxLayout()
        views = camera.get_views()
        self.h_views.addWidget(views[0])
        return self.h_views

    def start_record(self):
        if  self.record_button.isChecked():
             self.record_button.setIcon(QIcon("pages/images/cam_controler/rec.png"))
             camera.start_recording()
        else:
            self.record_button.setIcon(QIcon("pages/images/cam_controler/no_rec.png"))
            camera.stop_recording()

    def auto_record(self):
        # ip = send_http_get(self.ip_addaress + "/ip")
        # self.ip_addaress = "http://"+ip
        if self.enble_auto_rec_button.isChecked():
            self.is_auto_reccording = True
            self.enble_auto_rec_button.setIcon(QIcon("pages/images/cam_controler/auto_rec.png"))
        else:
            self.is_auto_reccording = False
            self.enble_auto_rec_button.setIcon(QIcon("pages/images/cam_controler/no_auto_rec.png"))

    def history_save(self,current_data):
        """
        Fonction pour gérer l'historique des événements avec des couples [detected, fixed].

        :param current_data: Dictionnaire contenant les données actuelles des capteurs.
        """
        # Charger les données précédentes
        try:
            with open('data_movemnt.json', 'r') as f:
                previous_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            previous_data = {
                "movement": False,
                "access": False,
                "temperature": False,
                "flame": False,
                "gaz": False,
                "dore": False,
                "window": False,
                "voice": False,
                "tempreture_value": 0
            }

        # Charger l'historique existant
        try:
            with open('history.json', 'r') as f:
                history_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history_data = {}

        sensor = 'movement'
        if sensor not in history_data:
            history_data[sensor] = []

        # Changement de False → True (détecté)
        if not previous_data[sensor] and current_data[sensor]:
            event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            history_data[sensor].append([event_time, None])  # Ajouter un couple avec detected et fixed=None

        # Changement de True → False (réparé)
        elif previous_data[sensor] and not current_data[sensor]:
            event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Trouver le dernier événement détecté sans date de résolution
            for event in reversed(history_data[sensor]):
                if event[1] is None:  # Si fixed est encore None
                    event[1] = event_time  # Ajouter la date de résolution
                    break

        # Sauvegarder l'historique mis à jour
        with open('history.json', 'w') as f:
            json.dump(history_data, f, indent=2)

        # Sauvegarder les données actuelles comme précédentes pour la prochaine exécution
        with open('data_movemnt.json', 'w') as f:
            json.dump(current_data, f, indent=2)
