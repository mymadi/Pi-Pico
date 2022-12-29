"""
Thingspaek IoT using CircuitPython on Raspberry Pi Pico
  - Tested with CircuitPython 8.0.0-beta.6

Additional libraries
  https://circuitpython.org/libraries
  - adafruit_requests.mpy
  - simpleio.mpy
  - adafruit_espatcontrol

Reference:
[1] https://github.com/CytronTechnologies/MAKER-PI-PICO/blob/main/Example%20Code/CircuitPython/IoT/thingspeak.py
"""

import os
import time
import microcontroller
import board
import digitalio
import simpleio
import random

import busio
import adafruit_requests as requests
import adafruit_espatcontrol.adafruit_espatcontrol_socket as socket
from adafruit_espatcontrol import adafruit_espatcontrol

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("All secret keys are kept in secrets.py, please add them there!")
    raise

# Initialize UART connection to the ESP8266 WiFi Module.
RX = board.GP17
TX = board.GP16
uart = busio.UART(TX, RX, receiver_buffer_size=2048)  # Use large buffer as we're not using hardware flow control.

esp = adafruit_espatcontrol.ESP_ATcontrol(uart, 115200, debug=False)
requests.set_socket(socket, esp)

print("Resetting ESP module✅")
esp.soft_reset()
# Connect to Wi-Fi AP
esp.connect(secrets)

# Buzzer
NOTE_G4 = 392
NOTE_C5 = 523
buzzer = board.GP18
simpleio.tone(buzzer, NOTE_C5, duration=0.1)

# Thingspeak API url.
tswriteAPI = secrets["thingspeak_write_api_key"]
API_URL = "http://api.thingspeak.com"


while True:
    try:
        while not esp.is_connected:
            print("Connecting...")
            esp.connect(secrets)
        
        # Dummy Value
        value1 = round(random.uniform(25,35),2)
        value2 = round(random.uniform(75,90),2)
        value3 = round(random.uniform(8,300),2)
        
        # Updating Thingspeak
        print("\nUpdating Thingspeak...✅")
        get_url = API_URL + "/update?api_key=" + tswriteAPI + "&field1=" + str(value1) + "&field2=" + str(value2) + "&field3=" + str(value3)
        r = requests.get(get_url)
        print("Value 1:", value1)
        print("Value 2:", value2)
        print("Value 3:", value3)
        print("Data Count:", r.text)
        print("OK✅")
    
        time.sleep(20)  # Free version of Thingspeak only allows one update every 20 seconds.
        simpleio.tone(buzzer, NOTE_G4, duration=0.1)
        simpleio.tone(buzzer, NOTE_C5, duration=0.15)
        
    except OSError as e:
        print("Failed!\n", e)
        microcontroller.reset()
