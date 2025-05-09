#!/usr/bin/env python3

# Import the GPIO library FIRST - very important
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import json
import os

BUZZER_PIN = 16  # GPIO 18

# Set the GPIO mode explicitly
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

# Set up buzzer pin as output
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)  # Initialize to off

# Initialize the reader with explicit pin assignments
reader = SimpleMFRC522()

# Define buzzer pin (change to match your wiring)



# File to store registered badge IDs
BADGE_FILE = "registered_badges.json"

def beep():
    """Sound the buzzer for the specified duration"""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    
def denied_sound():
    """Play a denied access pattern (three short beeps)"""
    for _ in range(3):
        beep()
        time.sleep(0.1)

def granted_sound():
    """Play an access granted pattern (one longer beep)"""
    beep()

def load_badges():
    """Load registered badges from file"""
    if os.path.exists(BADGE_FILE):
        try:
            with open(BADGE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error reading badge file")
            return {"badges": []}
    else:
        print(f"Badge file {BADGE_FILE} not found!")
        return {"badges": []}

# Load the badges at startup
badges_data = load_badges()
if badges_data["badges"]:
    print(f"Loaded {len(badges_data['badges'])} registered badges")
else:
    print("No registered badges found!")

print("\n===== RFID ACCESS CONTROL SYSTEM =====")
print("System is running - scan a badge to check access")
print("Press CTRL+C to exit")
print("---------------------------------------")

try:
    
    while True:
        # Wait for a badge
        print("\nWaiting for badge...")
        id, text = reader.read()
        print(f"Badge scanned! ID: {id}")
        
        # Check if badge is registered
        badge_found = False
        for badge in badges_data["badges"]:
            if badge["id"] == id:
                print("? ACCESS GRANTED")
                print(f"Welcome, {badge['name']}!")
                granted_sound()  # Play access granted sound
                badge_found = True
                break
        
        if not badge_found:
            print("? ACCESS DENIED")
            print("Unregistered badge detected!")
            #denied_sound()  # Play access denied sound
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
        # Brief delay to avoid multiple reads of the same card
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\nSystem shutdown by user")
finally:
    # Clean up GPIO
    GPIO.output(BUZZER_PIN, GPIO.LOW)  # Ensure buzzer is off
    GPIO.cleanup() 