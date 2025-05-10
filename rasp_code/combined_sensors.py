#!/usr/bin/env python3

# --- Standard Imports ---
import time
import json
import os
import datetime # For DHT11 script (implicitly, not directly used in snippet but good for full script)

# --- GPIO and Sensor Libraries ---
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522 # For RFID

# For DHT11 (CircuitPython approach)
import board
import adafruit_dht

# --- Pin Definitions ---
# RFID
RFID_BUZZER_PIN = 16  # As per your rfid.py
# Note: MFRC522 library handles its own SPI pin definitions (SDA, SCK, MOSI, MISO, RST)

# DHT11
# The pin for DHT11 is defined using the 'board' module notation
DHT11_GPIO_PIN_BOARD = board.D17 # GPIO17, as per your dht11.py (board.D17)

# Button
BUTTON_PIN = 2 # GPIO2, derived from your input_button.py (Button(2))

# Motion Sensor
MOTION_PIR_PIN = 4 # GPIO4, as per your motion.py

# --- Global Variables & Constants ---
BADGE_FILE = "registered_badges.json" # For RFID
rfid_reader = None
dht11_device = None
badges_data = {"badges": []} # Initialize for RFID

# --- GPIO General Setup ---
def initialize_gpio():
    print("Attempting to initialize GPIO...")
    try:
        GPIO.setmode(GPIO.BCM)      # Use Broadcom pin numbering
        GPIO.setwarnings(False)     # Disable GPIO warnings
        print("GPIO initialized successfully.")
    except Exception as e:
        print(f"ERROR during GPIO initialization: {e}")
        raise # Re-raise the exception to stop the script if GPIO setup fails

# --- RFID Functions ---
def setup_rfid():
    global rfid_reader, badges_data
    print("Attempting to set up RFID...")
    try:
        GPIO.setup(RFID_BUZZER_PIN, GPIO.OUT)
        GPIO.output(RFID_BUZZER_PIN, GPIO.LOW) # Buzzer off
        rfid_reader = SimpleMFRC522()
        print("RFID reader hardware initialized.")
        badges_data = load_rfid_badges()
        if badges_data.get("badges"):
            print(f"Loaded {len(badges_data['badges'])} registered RFID badges.")
        else:
            print("No registered RFID badges found or file error.")
        print("RFID setup complete.")
    except Exception as e:
        print(f"ERROR during RFID setup: {e}")
        rfid_reader = None # Ensure reader is None if setup fails

def rfid_beep(duration=0.2): # Shorter default beep
    # Ensure RFID_BUZZER_PIN is set up before trying to use it
    try:
        GPIO.output(RFID_BUZZER_PIN, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(RFID_BUZZER_PIN, GPIO.LOW)
    except Exception as e:
        print(f"Error in rfid_beep (is pin {RFID_BUZZER_PIN} set up?): {e}")

def load_rfid_badges():
    # This function is now called within setup_rfid after GPIO pin is ready
    if os.path.exists(BADGE_FILE):
        try:
            with open(BADGE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading RFID badge file (JSON Decode): {BADGE_FILE}")
            return {"badges": []}
        except Exception as e:
            print(f"Error opening/reading RFID badge file: {e}")
            return {"badges": []}
    else:
        print(f"RFID Badge file {BADGE_FILE} not found!")
        return {"badges": []}

def run_rfid_check():
    if not rfid_reader:
        return
    try:
        id, text = rfid_reader.read_no_block()
        if id:
            print(f"RFID Badge scanned! ID: {id}")
            badge_found = False
            for badge in badges_data.get("badges", []):
                if badge.get("id") == id:
                    print("✅ ACCESS GRANTED")
                    print(f"Welcome, {badge.get('name', 'N/A')}!")
                    rfid_beep(0.5)
                    badge_found = True
                    break
            if not badge_found:
                print("❌ ACCESS DENIED")
                print("Unregistered RFID badge detected!")
                GPIO.output(RFID_BUZZER_PIN, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(RFID_BUZZER_PIN, GPIO.LOW)
            time.sleep(1)
    except Exception as e:
        print(f"Error during RFID check: {e}")

# --- DHT11 Functions ---
def setup_dht11():
    global dht11_device
    print("Attempting to set up DHT11...")
    try:
        dht11_device = adafruit_dht.DHT11(DHT11_GPIO_PIN_BOARD)
        print("DHT11 sensor initialized successfully.")
    except RuntimeError as error:
        print(f"ERROR initializing DHT11 (RuntimeError): {error.args[0]}")
        dht11_device = None
    except Exception as e:
        print(f"ERROR failed to initialize DHT11 sensor (General Error): {e}")
        dht11_device = None
    print("DHT11 setup attempt complete.")

def run_dht11_reading():
    if not dht11_device:
        return
    try:
        temperature_c = dht11_device.temperature
        humidity = dht11_device.humidity
        if humidity is not None and temperature_c is not None:
            print(f"DHT11 - Temperature: {temperature_c:.1f}°C, Humidity: {humidity:.1f}%")
        else:
            print("DHT11: Failed to retrieve data (got None).")
    except RuntimeError as error:
        print(f"DHT11 reading error: {error.args[0]}. Retrying next cycle.")
    except Exception as e:
        print(f"Unexpected DHT11 error: {e}")

# --- Motion Sensor Functions ---
def setup_motion_sensor():
    print("Attempting to set up Motion (PIR) sensor...")
    try:
        GPIO.setup(MOTION_PIR_PIN, GPIO.IN)
        print(f"Motion sensor on GPIO {MOTION_PIR_PIN} configured.")
        print("Waiting 5 seconds for PIR sensor to settle...")
        time.sleep(5)
        print("PIR Sensor Ready!")
    except Exception as e:
        print(f"ERROR during Motion sensor setup: {e}")
    print("Motion sensor setup complete.")

def run_motion_detection():
    try:
        motion_state = GPIO.input(MOTION_PIR_PIN)
        if motion_state == 1:
            print("PIR: Motion detected!")
    except Exception as e:
        print(f"Error reading motion sensor: {e}")

# --- Button Functions (Converted to RPi.GPIO polling) ---
def setup_button():
    print("Attempting to set up Button...")
    try:
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"Button on GPIO {BUTTON_PIN} configured with pull-up.")
    except Exception as e:
        print(f"ERROR during Button setup: {e}")
    print("Button setup complete.")

def run_button_check():
    try:
        button_state = GPIO.input(BUTTON_PIN)
        if button_state == GPIO.LOW:
            print(f"BUTTON (GPIO {BUTTON_PIN}): PRESSED")
    except Exception as e:
        print(f"Error reading button state: {e}")

# --- Main Program Loop ---
def main():
    print("Starting main program...")
    try:
        initialize_gpio()
        setup_rfid()
        setup_dht11()
        setup_motion_sensor()
        setup_button()

        print("\n--- Starting Combined Sensor Monitoring Loop ---")
        print("Press CTRL+C to exit.")

        while True:
            run_rfid_check()
            run_dht11_reading()
            run_motion_detection()
            run_button_check()
            time.sleep(1)
            print("--- Loop iteration complete ---")

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An unhandled error occurred in main: {e}")
    finally:
        print("Cleaning up GPIO resources...")
        if dht11_device:
            try:
                dht11_device.exit()
                print("DHT11 device exited.")
            except Exception as e:
                print(f"Error on dht11_device.exit(): {e}")
        
        # Ensure buzzer pin is configured before trying to set low
        try:
            # Check if pin was set up (could fail if RFID setup failed)
            # A more robust way would be to track setup state for each pin
            if GPIO.gpio_function(RFID_BUZZER_PIN) == GPIO.OUT:
                 GPIO.output(RFID_BUZZER_PIN, GPIO.LOW)
        except Exception as e:
            print(f"Error ensuring buzzer is off (pin {RFID_BUZZER_PIN}): {e}")
            
        GPIO.cleanup()
        print("GPIO cleanup complete. Exiting.")

if __name__ == "__main__":
    main() 