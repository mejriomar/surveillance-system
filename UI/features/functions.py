from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QToolButton, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtGui import QPixmap

def dynamic_resize_image(widget, image_label, original_pixmap, percentage=0.3, max_size=200):
    """
    Redimensionne l'image dans image_label en fonction de la largeur de widget.

    :param widget: Le widget parent qui permet de récupérer la taille (ex: self)
    :param image_label: Le QLabel affichant l'image
    :param original_pixmap: Le QPixmap original de l'image (non redimensionné)
    :param percentage: Pourcentage de la largeur du widget à utiliser pour calculer la taille de l'image (ex: 0.3 pour 30%)
    :param max_size: Taille maximale (en pixels) que l'image peut atteindre
    """
    new_width = widget.width()
    calculated_size = int(new_width * percentage)
    image_size = min(calculated_size, max_size)

    if not original_pixmap.isNull():
        scaled_pixmap = original_pixmap.scaled(
            image_size, image_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        image_label.setPixmap(scaled_pixmap)

def dynamic_resize_text(widget, text_label, percentage=0.05, min_font_size=10, max_font_size=20):
    """
    Ajuste dynamiquement la taille de la police du text_label en fonction de la largeur du widget.

    :param widget: Le widget parent servant de référence pour la taille (par exemple, self)
    :param text_label: Le QLabel dont la police doit être redimensionnée
    :param percentage: Pourcentage de la largeur du widget pour calculer la taille de police
    :param min_font_size: Taille minimale de la police en points
    :param max_font_size: Taille maximale de la police en points
    """
    new_width = widget.width()
    # Calculer une taille de police basée sur un pourcentage de la largeur du widget
    calculated_font_size = int(new_width * percentage)

    # Contraindre la taille calculée entre la taille minimale et maximale
    final_font_size = min(max(calculated_font_size, min_font_size), max_font_size)

    font = text_label.font()
    font.setPointSize(final_font_size)
    text_label.setFont(font)

def resize_button_icon(button: QToolButton, window_width: int, window_height: int, scale_factor: float = 0.15):
    """
    Redimensionne dynamiquement le bouton et son icône en fonction de la taille de la fenêtre.

    :param button: Le bouton QToolButton à redimensionner
    :param window_width: Largeur actuelle de la fenêtre
    :param window_height: Hauteur actuelle de la fenêtre
    :param scale_factor: Facteur de mise à l'échelle (ex: 0.15 = 15% de la fenêtre)
    """
    size = int(min(window_width * scale_factor, window_height * scale_factor))  # Taille proportionnelle à la fenêtre
    button.setMinimumSize(size, size)
    button.setIconSize(QSize(size - 10, size - 10))  # L'icône est légèrement plus petite que le bouton