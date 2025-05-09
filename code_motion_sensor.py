#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Configure the GPIO pin
PIR_PIN = 4  # GPIO pin for motion sensor (BCM numbering)

# Set up GPIO
GPIO.setmode(GPIO.BCM)          # Use BCM pin numbering
GPIO.setup(PIR_PIN, GPIO.IN)    # Set pin as input

print("Simple PIR Motion Sensor - Direct GPIO Reading")
print("----------------------------------------------")
print(f"Using GPIO pin {PIR_PIN}")
print("Waiting 5 seconds for sensor to settle...")
time.sleep(5)  # Brief settling time
print("Ready!")

try:
    while True:
        # Read the sensor state directly
        motion_state = GPIO.input(PIR_PIN)
        
        # 1 = Motion detected, 0 = No motion
        if motion_state == 1:
            print("Motion detected!")
        else:
            print("No motion")
            
        time.sleep(1)  # Check every second
        
except KeyboardInterrupt:
    print("\nExiting program")
    
finally:
    # Clean up GPIO on exit
    GPIO.cleanup() 