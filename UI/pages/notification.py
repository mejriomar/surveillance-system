import json
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QCheckBox, QFrame
from PyQt6.QtCore import Qt, QFile, QTextStream, QTimer
import os

class NotificationUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de Notification - Serviance")
        self.setGeometry(200, 100, 1000, 600)
        self._load_stylesheet("styles.css")
        self.init_ui()
        self.saved_email_path = "saved_email.txt"
        self.load_saved_email()
        self.previous_sensor_states = {}
        self.start_monitoring()

    def _load_stylesheet(self, path):
        file = QFile(path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()

    def init_ui(self):
        main_layout = QHBoxLayout()
        sidebar = self.create_sidebar()
        content = self.create_main_content()
        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content, 4)
        self.setLayout(main_layout)

    def create_sidebar(self):
        sidebar = QVBoxLayout()
        sidebar.setSpacing(20)
        sidebar.setContentsMargins(10, 30, 10, 10)
        menu_items = ["Home", "Atmosphérique", "Chocs", "Identité", "Caméra", "Notification"]
        for item in menu_items:
            label = QLabel(item)
            label.setFixedHeight(30)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("background-color: #1d595f; color: white; border-radius: 8px;" if item == "Notification" else "color: white;")
            sidebar.addWidget(label)
        sidebar.addStretch()
        return sidebar

    def create_main_content(self):
        layout = QVBoxLayout()
        header = QLabel("Système de Notification - Serviance")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold; background-color: #1b2f4d; padding: 15px; border-radius: 12px; color: #6ad7d7;")
        layout.addWidget(header)

        # Message de statut
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: lightgreen; font-weight: bold;")
        layout.addWidget(self.status_label)

        layout.addWidget(self.create_config_section())
        layout.addWidget(self.create_authorisation_section())
        return layout

    def create_config_section(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: #162a43; border-radius: 10px; padding: 20px;")
        layout = QGridLayout()

        email_label = QLabel("Email :")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemple@mail.com")

        phone_label = QLabel("Téléphone :")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+213 6 00 00 00 00")

        email_btn = QPushButton("Sauvegarder")
        email_btn.clicked.connect(self.save_email)

        phone_btn = QPushButton("Sauvegarder")

        for btn in (email_btn, phone_btn):
            btn.setStyleSheet("QPushButton { background-color: #2ebbbd; color: white; padding: 6px 12px; border-radius: 6px;} QPushButton:hover { background-color: #25a1a3;}")

        layout.addWidget(email_label, 0, 0)
        layout.addWidget(self.email_input, 0, 1)
        layout.addWidget(email_btn, 0, 2)
        layout.addWidget(phone_label, 1, 0)
        layout.addWidget(self.phone_input, 1, 1)
        layout.addWidget(phone_btn, 1, 2)

        frame.setLayout(layout)
        return frame

    def create_authorisation_section(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: #162a43; border-radius: 10px; padding: 20px;")
        layout = QVBoxLayout()

        title = QLabel("Autorisation des capteurs")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #61dafb;")
        layout.addWidget(title)

        self.toggle_camera = QCheckBox("Caméra")
        self.toggle_rfid = QCheckBox("RFID")
        self.toggle_choc = QCheckBox("Chocs")
        self.toggle_atmo = QCheckBox("Atmosphérique")

        for box in (self.toggle_camera, self.toggle_rfid, self.toggle_choc, self.toggle_atmo):
            box.setChecked(True)
            box.setStyleSheet("QCheckBox { padding: 5px; }")

        layout.addWidget(self.toggle_camera)
        layout.addWidget(self.toggle_rfid)
        layout.addWidget(self.toggle_choc)
        layout.addWidget(self.toggle_atmo)

        save_btn = QPushButton("Sauvegarder")
        save_btn.setStyleSheet("QPushButton { background-color: #2ebbbd; color: white; padding: 8px 15px; border-radius: 8px;} QPushButton:hover { background-color: #25a1a3;}")
        layout.addWidget(save_btn)

        frame.setLayout(layout)
        return frame

    def show_status_message(self, message, duration=3000, color="lightgreen"):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        QTimer.singleShot(duration, lambda: self.status_label.setText(""))

    def save_email(self):
        email = self.email_input.text().strip()
        if email:
            with open(self.saved_email_path, "w") as f:
                f.write(email)
            self.show_status_message("Email enregistré avec succès ✅", color="lightgreen")
        else:
            self.show_status_message("Email non valide ❌", color="red")

    def load_saved_email(self):
        if os.path.exists(self.saved_email_path):
            with open(self.saved_email_path, "r") as f:
                saved_email = f.read().strip()
                self.email_input.setText(saved_email)

    def start_monitoring(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_sensor_data)
        self.timer.start(15000)  # toutes les 15 secondes

    def check_sensor_data(self):
        try:
            with open("data.json", "r") as file:
                data = json.load(file)

            current_states = {k: v for k, v in data.items() if isinstance(v, bool)}
            changed = False

            for key, value in current_states.items():
                if self.previous_sensor_states.get(key) != value:
                    changed = True
                    break

            if changed:
                alert_sensors = [k for k, v in current_states.items() if v is True]
                if alert_sensors:
                    email = self.email_input.text().strip()
                    if email:
                        message = "Alerte : Les capteurs suivants sont activés :\n\n" + "\n".join(alert_sensors)
                        self.send_email_notification(email, "Alerte Capteur", message)
                    else:
                        self.show_status_message("Aucune adresse email pour l'alerte ❌", color="red")

            self.previous_sensor_states = current_states

        except Exception as e:
            self.show_status_message("Erreur de lecture du fichier JSON ❌", color="red")
            print(f"Erreur lors de la lecture des données : {e}")

    def send_email_notification(self, to_email, subject, message):
        sender_email = "systemserviance@gmail.com"
        sender_password = "xbzr vpxi tvgl mkmx"

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                self.show_status_message(f"Notification envoyée à {to_email} ✅", color="lightgreen")
                print(f"Notification envoyée à {to_email}")
        except Exception as e:
            self.show_status_message("Erreur lors de l'envoi de l'email ❌", color="red")
            print(f"Erreur d'envoi d'email : {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotificationUI()
    window.show()
    sys.exit(app.exec())
