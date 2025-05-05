from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QUrl
from PyQt6.QtWebSockets import QWebSocket
from PyQt6.QtNetwork import QAbstractSocket

import json

class WebSocketClient(QObject):
    data_received = pyqtSignal(dict)  # Signal pour les données reçues
    status_updated = pyqtSignal(str)  # Signal pour les statuts (connexion, erreurs)

    def __init__(self, url):
        super().__init__()
        self.url = QUrl(url)
        self.socket = QWebSocket()
        self.reconnect_interval = 1  # seconds
        self.is_reconnecting = False
        self._setup_connections()

    def _setup_connections(self):
        """Connect Qt signals to slots"""
        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.textMessageReceived.connect(self.on_message)
        self.socket.errorOccurred.connect(self.on_error)

    def start(self):
        """Démarre la connexion WebSocket"""
        self.status_updated.emit(f"Tentative de connexion à {self.url.toString()}")
        self.socket.open(self.url)

    def on_connected(self):
        """Gère l'événement de connexion réussie"""
        self.is_reconnecting = False
        self.status_updated.emit("Connexion WebSocket établie")

    def on_disconnected(self):
        """Gère la déconnexion"""
        self.status_updated.emit("Connexion WebSocket perdue")
        self._schedule_reconnect()

    def on_message(self, message):
        """Traite les messages reçus"""
        try:
            data = json.loads(message)
            self.data_received.emit(data)
        except json.JSONDecodeError as e:
            self.status_updated.emit(f"Erreur de décodage JSON : {e}")

    def on_error(self, error):
        """Gère les erreurs"""
        error_str = self.socket.errorString()
        self.status_updated.emit(f"Erreur WebSocket : {error_str}")
        self.socket.close()

    def _schedule_reconnect(self):
        """Planifie une reconnexion après un délai"""
        if not self.is_reconnecting:
            self.is_reconnecting = True
            QTimer.singleShot(self.reconnect_interval * 1000, self.start)

    def send_data(self, data):
        """Envoie des données via WebSocket"""
        if self.socket.state() == QAbstractSocket.SocketState.ConnectedState:
            try:
                self.socket.sendTextMessage(json.dumps(data))
                self.status_updated.emit("Données envoyées avec succès")
            except Exception as e:
                self.status_updated.emit(f"Erreur lors de l'envoi : {e}")
        else:
            self.status_updated.emit("Erreur : Connexion inactive")

# Instance globale du client WebSocket
# websocket_client = WebSocketClient("ws://192.168.43.237/ws")
websocket_client = WebSocketClient("ws://192.168.43.66:8765")
# websocket_client = WebSocketClient("ws://esp32.local/ws")