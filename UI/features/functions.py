from PyQt6.QtWidgets import  QToolButton
from PyQt6.QtCore import Qt, QSize
import requests
import json
from datetime import datetime
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



def send_http_get(url, params=None):
    """
    Envoie une requête HTTP GET vers l'URL donnée avec paramètres optionnels.

    :param url: URL de destination (ex: "http://192.168.4.1/servo")
    :param params: Dictionnaire de paramètres GET (ex: {"dir": "up"})
    :return: Contenu de la réponse ou message d’erreur
    """
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()  # Soulève une exception pour les erreurs HTTP
        try:
            return response.json()  # Essaie de décoder en JSON
        except ValueError:
            return response.text  # Sinon retourne le texte brut
    except requests.exceptions.RequestException as e:
        return f"Erreur : {e}"



def modify_json(element, value, filename='data.json'):
    try:
        # Lecture du fichier JSON
        with open(filename, 'r') as f:
            data = json.load(f)

        # Vérification que la clé existe
        if element not in data:
            print(f"⚠️ L'élément '{element}' n'existe pas dans le fichier JSON.")
            return False

        # Modification de la valeur
        data[element] = value

        # Écriture du fichier mis à jour
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"✅ '{element}' a été mis à jour avec succès à la valeur : {value}")
        return True

    except FileNotFoundError:
        print(f"❌ Le fichier '{filename}' est introuvable.")
    except json.JSONDecodeError:
        print(f"❌ Le fichier '{filename}' n'est pas un JSON valide.")
    except Exception as e:
        print(f"❌ Une erreur s'est produite : {e}")

    return False

def history(current_data):
    """
    Fonction pour gérer l'historique des événements avec des couples [detected, fixed].

    :param current_data: Dictionnaire contenant les données actuelles des capteurs.
    """
    # Charger les données précédentes
    try:
        with open('data.json', 'r') as f:
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

    # Vérifier les changements d'état des capteurs
    sensors = ['movement', 'access', 'temperature', 'flame', 'gaz', 'dore', 'window', 'voice']
    for sensor in sensors:
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

    # Vérifier la température
    prev_temp = previous_data['tempreture_value']
    curr_temp = current_data['tempreture_value']
    if 'temperature' not in history_data:
        history_data['temperature'] = []

    # Dépassement du seuil de température (détecté)
    if curr_temp > 50 and prev_temp <= 50:
        event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history_data['temperature'].append([event_time, None])  # Ajouter un couple avec detected et fixed=None

    # Retour sous le seuil de température (réparé)
    elif curr_temp <= 50 and prev_temp > 50:
        event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Trouver le dernier événement détecté sans date de résolution
        for event in reversed(history_data['temperature']):
            if event[1] is None:  # Si fixed est encore None
                event[1] = event_time  # Ajouter la date de résolution
                break

    # Sauvegarder l'historique mis à jour
    with open('history.json', 'w') as f:
        json.dump(history_data, f, indent=2)

    # Sauvegarder les données actuelles comme précédentes pour la prochaine exécution
    with open('data.json', 'w') as f:
        json.dump(current_data, f, indent=2)