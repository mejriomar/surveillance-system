# -*- coding: utf-8 -*-
import asyncio
import websockets
import json
import RPi.GPIO as GPIO

# Configuration of GPIO pins (BCM numbering)
PIN_CONFIG = {
    "movement": 12,
    "access": 14,
    "temperature": 27,
    "flame": 26,
    "gaz": 25,
    "dore": 33,
    "window": 24,
    "voice": 15,
    "temp_reset": 5  # Safe pin for reset
}

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
for name, pin in PIN_CONFIG.items():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Temporary counter
i = 0

def generate_json():
    global i
    
    # Reset counter if button is pressed
    if GPIO.input(PIN_CONFIG["temp_reset"]) == GPIO.LOW:
        i = 0
        print("Temperature counter reset")
    
    # Read sensor states
    data = {
        "movement": GPIO.input(PIN_CONFIG["movement"]) == GPIO.LOW,
        "access": GPIO.input(PIN_CONFIG["access"]) == GPIO.LOW,
        "temperature": GPIO.input(PIN_CONFIG["temperature"]) == GPIO.LOW,
        "flame": GPIO.input(PIN_CONFIG["flame"]) == GPIO.LOW,
        "gaz": GPIO.input(PIN_CONFIG["gaz"]) == GPIO.LOW,
        "dore": GPIO.input(PIN_CONFIG["dore"]) == GPIO.LOW,
        "window": GPIO.input(PIN_CONFIG["window"]) == GPIO.LOW,
        "voice": GPIO.input(PIN_CONFIG["voice"]) == GPIO.LOW,
        "tempreture_value": i
    }
    
    i += 1
    return json.dumps(data)

# Global counter
counter = 0

async def send_counter(websocket):
    """Send incrementing counter to client every second."""
    global counter
    while True:
        await asyncio.sleep(1)
        counter += 1
        try:
            await websocket.send(generate_json())
        except websockets.exceptions.ConnectionClosed:
            break

async def receive_messages(websocket):
    """Receive and print messages from client."""
    try:
        async for message in websocket:
            print(f"Received from client: {message}")
    except websockets.exceptions.ConnectionClosed:
        pass

async def handler(websocket):
    """Handle a single client connection."""
    print("Client connected.")
    
    # Start sending and receiving tasks
    send_task = asyncio.create_task(send_counter(websocket))
    receive_task = asyncio.create_task(receive_messages(websocket))

    done, pending = await asyncio.wait(
        [send_task, receive_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel remaining tasks upon disconnection
    for task in pending:
        task.cancel()

    print("Client disconnected.")

async def main():
    """Start the WebSocket server."""
    async with websockets.serve(handler, "0.0.0.0", 8765, ping_interval=20):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if _name_ == "_main_":
    asyncio.run(main())