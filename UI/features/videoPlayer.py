from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider, QLabel
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        # Création du lecteur multimédia et de la sortie audio
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # Création du widget vidéo
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # Création du layout principal qui sera retourné
        self.layout = QVBoxLayout()

        # Initialisation des contrôles
        self._setup_controls()

        # Connexion des signaux pour mettre à jour la position et la durée
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)

        # Variables pour stocker la durée
        self.duration = 0

    def _setup_controls(self):
        # Bouton pour ouvrir un fichier vidéo
        self.open_button = QPushButton("Ouvrir Vidéo")
        self.open_button.clicked.connect(self.open_file)

        # Bouton pour lire / mettre en pause
        self.play_button = QPushButton("▶️ Lire")
        self.play_button.clicked.connect(self.toggle_play_pause)

        # Bouton Stop
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_video)

        # Curseur de position (progression)
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.setObjectName("video_slider")
        self.position_slider.sliderMoved.connect(self.set_position)

        # Label pour afficher le temps écoulé et la durée totale
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Curseur de volume
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setObjectName("volume_slider")
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.audio_output.setVolume(0.5)  # Volume initial à 50%

        # Layout pour les boutons et le volume
        self.controls_layout = QHBoxLayout()
        self.controls_layout.addWidget(self.open_button)
        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.stop_button)
        self.controls_layout.addWidget(QLabel("Volume"))
        self.controls_layout.addWidget(self.volume_slider)

    def play_video(self):
        """
        Construit et retourne un QVBoxLayout contenant le widget vidéo,
        le curseur de progression avec le label de temps à droite, et les contrôles.
        Ce layout sera intégré dans la fenêtre principale.
        """
        # Ajout du widget vidéo
        self.layout.addWidget(self.video_widget,1)

        # Création d'un layout horizontal pour le slider et le label de temps
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.position_slider)
        time_layout.addWidget(self.time_label)

        # Ajout du layout horizontal dans le layout principal
        self.layout.addLayout(time_layout)

        # Ajout des contrôles
        self.layout.addLayout(self.controls_layout)
        return self.layout

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une vidéo", "", "Vidéos (*.mp4 *.avi *.mov *.mkv)"
        )
        if file_path:
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.play()
            self.play_button.setText("⏸️ Pause")

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_button.setText("▶️ Lire")
        else:
            self.media_player.play()
            self.play_button.setText("⏸️ Pause")

    def stop_video(self):
        self.media_player.stop()
        self.play_button.setText("▶️ Lire")

    def update_position(self, position):
        self.position_slider.setValue(position)
        self.update_time_label(position, self.duration)

    def update_duration(self, duration):
        self.duration = duration
        self.position_slider.setRange(0, duration)
        self.update_time_label(self.media_player.position(), duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100.0)

    def update_time_label(self, position, duration):
        """Met à jour le label de temps au format mm:ss / mm:ss."""
        self.time_label.setText(f"{self.format_time(position)} / {self.format_time(duration)}")

    def format_time(self, ms):
        """Formate le temps en millisecondes en mm:ss."""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"
