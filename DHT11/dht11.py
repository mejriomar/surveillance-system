#!/usr/bin/env python3

import time
import board
import adafruit_dht

# Initialize the DHT11 sensor
# You need to specify the GPIO pin using the 'board' module.
# For example, if your DHT11 data pin is connected to GPIO 4:
DHT_PIN = board.D17  # D4 corresponds to GPIO 4. Change if your pin is different.
                    # Common alternatives: board.D17 (GPIO17), board.D22 (GPIO22), etc.

# Initialize the DHT device.
# Note: The DHT11 is less precise and slower than DHT22.
try:
    dhtDevice = adafruit_dht.DHT11(DHT_PIN)
    print("DHT11 sensor initialized successfully.")
except Exception as e:
    print(f"Failed to initialize DHT11 sensor: {e}")
    print("Please check your wiring and that libgpiod2 is installed ('sudo apt install libgpiod2').")
    exit()

print("Starting DHT11 readings (Press CTRL+C to exit)")

try:
    while True:
        try:
            # Attempt to get a sensor reading.
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            print('Humidity',humidity,'temperature',temperature_c)
            if humidity is not None and temperature_c is not None:
                print(f"Temperature: {temperature_c:.1f}ï¿½C, Humidity: {humidity:.1f}%")
                if temperature_c > 25:
                    print('Temperature is over 25ï¿½C')
                else:
                    print('Temperature is under or at 25ï¿½C')
            else:
                print("Failed to retrieve data from DHT11 sensor (got None)")

        except RuntimeError as error:
            # Errors happen fairly often with DHT sensors, just print it and continue.
            print(f"Reading error: {error.args[0]}")
        except Exception as error:
            dhtDevice.exit() # Clean up the sensor
            raise error # Re-raise other errors

        # Wait 2 seconds before the next reading
        time.sleep(2.0)

except KeyboardInterrupt:
    print("\nExiting program")