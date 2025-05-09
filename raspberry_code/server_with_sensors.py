# -*- coding: utf-8 -*-
import asyncio
import websockets
import json
import RPi.GPIO as GPIO
import time
import os
from mfrc522 import SimpleMFRC522
import board
import adafruit_dht

# === Pin Definitions ===
RFID_BUZZER_PIN = 16        # GPIO16
DHT11_GPIO_PIN = board.D17  # GPIO17
BUTTON_PIN = 2              # GPIO2 (used to reset counter)
MOTION_PIR_PIN = 4          # GPIO4

# Additional sensors
PIN_CONFIG = {
    "movement": 12,
    "access": None,       # will set access from badge_found
    "temperature_switch": 27,
    "flame": 26,
    "gaz": 25,
    "dore": 33,
    "window": 24,
    "voice": 15,
    "temp_reset": 5,
}

# === Globals ===
badge_found = False
temperature_c = None
rfid_reader = None
badges_data = {"badges": []}
dht11_device = None
counter = 0
BADGE_FILE = "registered_badges.json"
DEFAULT_PORT = 8765

# === Initialization ===
def initialize_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    # Buzzer output
    GPIO.setup(RFID_BUZZER_PIN, GPIO.OUT)
    # PIR input
    GPIO.setup(MOTION_PIR_PIN, GPIO.IN)
    # Button reset
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Other inputs
    for pin in [PIN_CONFIG["movement"], PIN_CONFIG["temperature_switch"],
                PIN_CONFIG["flame"], PIN_CONFIG["gaz"], PIN_CONFIG["dore"],
                PIN_CONFIG["window"], PIN_CONFIG["voice"], PIN_CONFIG["temp_reset"]]:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("GPIO initialized.")

# === RFID ===

def setup_rfid():
    global rfid_reader, badges_data
    rfid_reader = SimpleMFRC522()
    badges_data = load_rfid_badges()
    print("RFID reader initialized.")


def load_rfid_badges():
    if os.path.exists(BADGE_FILE):
        with open(BADGE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("JSON decode error in badge file.")
    else:
        print("Badge file not found!")
    return {"badges": []}


def rfid_beep(duration=0.2):
    GPIO.output(RFID_BUZZER_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(RFID_BUZZER_PIN, GPIO.LOW)


def run_rfid_check():
    global badge_found
    badge_found = False
    if not rfid_reader:
        return
    id, _ = rfid_reader.read_no_block()
    if id:
        print(f"RFID scanned: {id}")
        for badge in badges_data.get("badges", []):
            if badge.get("id") == id:
                badge_found = True
                print("ACCESS GRANTED")
                print(f"Welcome {badge.get('name', '')}")
                rfid_beep(0.5)
                break
        if not badge_found:
            print("ACCESS DENIED")
            GPIO.output(RFID_BUZZER_PIN, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(RFID_BUZZER_PIN, GPIO.LOW)

# === DHT11 ===

def setup_dht11():
    global dht11_device
    try:
        dht11_device = adafruit_dht.DHT11(DHT11_GPIO_PIN)
        print("DHT11 initialized.")
    except Exception as e:
        dht11_device = None
        print(f"DHT11 setup error: {e}")


def run_dht11_reading():
    global temperature_c
    if not dht11_device:
        return
    try:
        temperature_c = dht11_device.temperature
        humidity = dht11_device.humidity
        if temperature_c is not None and humidity is not None:
            # Use plain 'C' instead of degree symbol to avoid encoding issues
            print(f"Temp: {temperature_c:.1f}C, Humidity: {humidity:.1f}%")
    except RuntimeError as e:
        print(f"DHT11 read retry: {e}")
    except Exception as e:
        print(f"DHT11 error: {e}")

# === JSON Generation ===

def generate_json():
    global counter
    # Reset if button pressed
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:
        counter = 0
        print("Counter reset")

    data = {
        "movement": GPIO.input(PIN_CONFIG["movement"]) == GPIO.LOW,
        "access": badge_found,
        "temperature_switch": GPIO.input(PIN_CONFIG["temperature_switch"]) == GPIO.LOW,
        "flame": GPIO.input(PIN_CONFIG["flame"]) == GPIO.LOW,
        "gaz": GPIO.input(PIN_CONFIG["gaz"]) == GPIO.LOW,
        "dore": GPIO.input(PIN_CONFIG["dore"]) == GPIO.LOW,
        "window": GPIO.input(PIN_CONFIG["window"]) == GPIO.LOW,
        "voice": GPIO.input(PIN_CONFIG["voice"]) == GPIO.LOW,
        "temperature_value": temperature_c,
        "counter": counter
    }
    counter += 1
    return json.dumps(data)

# === Async Server ===

async def send_data(ws):
    while True:
        run_rfid_check()
        run_dht11_reading()
        await ws.send(generate_json())
        await asyncio.sleep(1)

async def handle(ws):
    print("Client connected.")
    sender = asyncio.create_task(send_data(ws))
    try:
        async for msg in ws:
            print(f"Received: {msg}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        sender.cancel()
        print("Client disconnected.")

async def main(port=DEFAULT_PORT):
    initialize_gpio()
    setup_rfid()
    setup_dht11()
    print(f"Starting WebSocket on ws://0.0.0.0:{port}")
    try:
        async with websockets.serve(handle, "0.0.0.0", port):
            await asyncio.Future()  # run forever
    except OSError as e:
        print(f"Failed to bind on port {port}: {e}")
        print("Please make sure the port is free or specify a different port.")

if __name__ == "__main__":
    try:
        port_env = os.getenv('WS_PORT')
        port = int(port_env) if port_env and port_env.isdigit() else DEFAULT_PORT
        asyncio.run(main(port))
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        if dht11_device:
            try:
                dht11_device.exit()
            except Exception:
                pass
        GPIO.cleanup()
        print("Cleaned up GPIO.")
