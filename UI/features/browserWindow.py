# camera_module.py

import cv2
from datetime import datetime
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel
import os

class CameraGrabber(QThread):
    frame_ready = pyqtSignal(QImage)
    motion_detected = pyqtSignal()

    def __init__(self, url: str, fps: float = 20.0):
        super().__init__()
        self.url = url
        self.running = False
        self.recording = False
        self.writer = None
        self.filename = None
        self.fps = fps
        self.prev_gray = None
        self.motion_threshold = 50000

    def run(self):
        while True:
            cap = cv2.VideoCapture(self.url)
            real_fps = cap.get(cv2.CAP_PROP_FPS)
            if real_fps > 0:
                self.fps = real_fps

            self.running = True

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    print("⚠️ Perte de connexion au flux. Nouvelle tentative dans 2 secondes...")
                    cap.release()
                    self._release_writer()
                    self.msleep(2000)
                    break

                # Détection de mouvement
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if self.prev_gray is not None:
                    try:
                        diff = cv2.absdiff(self.prev_gray, gray)
                        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                        motion_score = cv2.countNonZero(thresh)
                    except Exception as e:
                        print(f"⚠️ Erreur de traitement d'image : {e}")
                        motion_score = 0

                    if motion_score > self.motion_threshold:
                        # print("📸 Mouvement détecté !")
                        self.motion_detected.emit()

                self.prev_gray = gray

                if self.recording and self.writer is None:
                    h, w = frame.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    self.writer = cv2.VideoWriter(self.filename, fourcc, self.fps, (w, h))

                if self.recording and self.writer:
                    try:
                        self.writer.write(frame)
                    except Exception as e:
                        print(f"⚠️ Erreur d'écriture dans le fichier : {e}")


                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, _ = rgb.shape
                img = QImage(rgb.data, w, h, w*3, QImage.Format.Format_RGB888)
                self.frame_ready.emit(img)

            cap.release()
            self._release_writer()
            if not self.running:
                break

    def _release_writer(self):
        if self.writer:
            self.writer.release()
            self.writer = None

    def stop(self):
        self.running = False
        self.wait()

    def start_recording(self, filename: str):
        self.filename = filename
        self.recording = True

    def stop_recording(self):
        self.recording = False
        if self.writer:
            self.writer.release()
            self.writer = None


class CameraView(QLabel):
    def __init__(self, min_size=(320, 240)):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(*min_size)

    def update_image(self, img: QImage):
        self.setPixmap(
            QPixmap.fromImage(img)
                   .scaled(self.size(),
                           Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
        )

    def set_recording_border(self, is_recording: bool):
        color = "red" if is_recording else "black"
        self.setStyleSheet(f"border: 2px solid {color};")


class CameraEngine:
    def __init__(self):
        pass

    def init(self, stream_url: str, n_views: int = 1, view_size=(320,240)):
        self.grabber = CameraGrabber(stream_url)
        self.views = [CameraView(view_size) for _ in range(n_views)]
        for v in self.views:
            self.grabber.frame_ready.connect(v.update_image)

    def get_views(self):
        return self.views

    def start_camera(self):
        if not self.grabber.isRunning():
            self.grabber.start()

    def stop_camera(self):
        if self.grabber.isRunning():
            self.grabber.stop()

    def start_recording(self, filename: str = None):
        if filename is None:
            filename = datetime.now().strftime("record_%Y%m%d_%H%M%S.avi")

        save_dir = "videos"
        os.makedirs(save_dir, exist_ok=True)
        full_path = os.path.join(save_dir, filename)

        self.grabber.start_recording(full_path)
        for v in self.views:
            v.set_recording_border(True)

    def stop_recording(self):
        self.grabber.stop_recording()
        for v in self.views:
            v.set_recording_border(False)

camera = CameraEngine()
