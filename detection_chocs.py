import time
import random

# Simulation des broches GPIO
class GPIO:
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    PUD_UP = "PUD_UP"
    HIGH = 1
    LOW = 0

    pins = {}

    @staticmethod
    def setmode(mode):
        print(f"Mode GPIO configuré sur {mode}")

    @staticmethod
    def setup(pin, mode, pull_up_down=None):
        GPIO.pins[pin] = GPIO.LOW
        print(f"Broche {pin} configurée en mode {mode}")

    @staticmethod
    def input(pin):
        # Simuler une détection aléatoire de choc
        return random.choice([GPIO.HIGH, GPIO.LOW])

    @staticmethod
    def output(pin, state):
        GPIO.pins[pin] = state
        print(f"Buzzer {'activé' if state == GPIO.HIGH else 'désactivé'}")

    @staticmethod
    def cleanup():
        print("Nettoyage des GPIO simulés")

# Configuration des broches pour les capteurs et le buzzer
DOOR1_SENSOR_PIN = 17  # Capteur pour la porte 1
DOOR2_SENSOR_PIN = 18  # Capteur pour la porte 2
WINDOW1_SENSOR_PIN = 22  # Capteur pour la fenêtre 1
WINDOW2_SENSOR_PIN = 23  # Capteur pour la fenêtre 2
BUZZER_PIN = 27  # Broche GPIO simulée pour le buzzer

# Dictionnaire pour mapper les capteurs à leurs emplacements
SENSOR_LOCATIONS = {
    DOOR1_SENSOR_PIN: "Porte 1",
    DOOR2_SENSOR_PIN: "Porte 2",
    WINDOW1_SENSOR_PIN: "Fenêtre 1",
    WINDOW2_SENSOR_PIN: "Fenêtre 2",
}

# Simulation des GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR1_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DOOR2_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WINDOW1_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WINDOW2_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

try:
    print("Détection de chocs simulée en cours...")
    while True:
        for sensor_pin, location in SENSOR_LOCATIONS.items():
            if GPIO.input(sensor_pin) == GPIO.LOW:  # Simuler une détection de choc
                print(f"!!! *** Alerte *** Choc détecté à {location} *** !!!")
                GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Activer le buzzer simulé
                time.sleep(1)  # Maintenir le buzzer actif pendant 0.5 seconde
                GPIO.output(BUZZER_PIN, GPIO.LOW)  # Désactiver le buzzer simulé
        time.sleep(3)  # Petite pause pour éviter une détection continue
except KeyboardInterrupt:
    print("Arrêt de la simulation.")
finally:
    GPIO.cleanup()  # Réinitialiser les GPIO simulés