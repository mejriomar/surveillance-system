
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPainter, QFont, QPen
from PyQt6.QtCore import Qt, QRectF
import sys

class CircularLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 40, QFont.Weight.Bold))
        self.setFixedSize(150, 150)  # Taille du widget (cercle)
        self.setObjectName("circular_label")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Définir le pinceau pour la bordure rouge épaisse
        pen = QPen(Qt.GlobalColor.red, 10)
        painter.setPen(pen)

        # Calculer un carré centré de taille minimale entre la largeur et la hauteur du widget
        size = min(self.width(), self.height())
        margin = pen.width() / 2
        rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
        painter.drawEllipse(rect)

        # Dessiner le texte centré en rouge
        painter.setPen(Qt.GlobalColor.red)
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())