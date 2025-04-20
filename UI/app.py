import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from PyQt6.QtGui import QIcon
from features.backend import websocket_client
import json

def on_data_received( data):
    print("Data received:", data)

    # Données reçues de l'ESP32 (représentées par une variable Python)
    # data = {
    #     'movement': 1,
    #     'access': 1,
    #     'temperature': 1,
    #     'flame': 0,
    #     'gaz': 0,
    #     'dore': 1,
    #     'window': 0,
    #     'voice': 1,
    #     'tempreture_value': 3870
    # }

    # Chemin du fichier où enregistrer les données
    file_path = "data.json"

    # Écrire les données dans un fichier JSON
    try:
        with open(file_path, "w", encoding="utf-8") as json_file:
            # Utiliser json.dump() pour écrire le dictionnaire dans un fichier JSON
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"Les données ont été enregistrées dans {file_path}")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier : {e}")

def on_status_updated( message):
    print("Status updated:", message)

if __name__ == "__main__":
    # Démarrer le client WebSocket
    websocket_client.start()
    # Connexion aux signaux
    websocket_client.data_received.connect(on_data_received)
    websocket_client.status_updated.connect(on_status_updated)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())