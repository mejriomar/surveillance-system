# websocket_handler.py
from PyQt6.QtCore import QObject, pyqtSignal
import websocket
import json
import threading
import time

class WebSocketClient(QObject):
    data_received = pyqtSignal(dict)  # Signal pour les données reçues
    status_updated = pyqtSignal(str)  # Signal pour les statuts (connexion, erreurs)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.ws = None
        self.reconnect_interval = 5
        self.is_reconnecting = False

    def start(self):
        """Démarre la connexion WebSocket dans un thread séparé."""
        threading.Thread(target=self.run_websocket, daemon=True).start()

    def run_websocket(self):
        """Boucle de connexion WebSocket avec reconnexion automatique."""
        while True:
            try:
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open
                )
                self.ws.run_forever()
            except Exception as e:
                self.status_updated.emit(f"Erreur critique : {e}")
            finally:
                if not self.is_reconnecting:
                    self.is_reconnecting = True
                    self.status_updated.emit(
                        f"Tentative de reconnexion dans {self.reconnect_interval} secondes..."
                    )
                    time.sleep(self.reconnect_interval)

    def on_message(self, ws, message):
        """Traite les messages reçus."""
        try:
            data = json.loads(message)
            self.data_received.emit(data)
        except json.JSONDecodeError as e:
            self.status_updated.emit(f"Erreur de décodage JSON : {e}")

    def on_error(self, ws, error):
        self.status_updated.emit(f"Erreur WebSocket : {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.status_updated.emit("Connexion WebSocket fermée")

    def on_open(self, ws):
        self.is_reconnecting = False
        self.status_updated.emit("Connexion WebSocket ouverte")

    def send_data(self, data):
        """Envoie des données via WebSocket."""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            try:
                self.ws.send(json.dumps(data))
                self.status_updated.emit("Données envoyées avec succès")
            except Exception as e:
                self.status_updated.emit(f"Erreur envoi : {e}")
        else:
            self.status_updated.emit("Erreur : Connexion inactive")

# Instance globale du client WebSocket
websocket_client = WebSocketClient("ws://192.168.1.15/ws")