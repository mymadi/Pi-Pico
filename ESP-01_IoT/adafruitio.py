'''
Smart Home - Adafruit IO
  - Tested with CircuitPython 8.0.0-beta.6

Additional libraries
  https://circuitpython.org/libraries
    - adafruit_requests.mpy
    - simpleio.mpy
    - adafruit_io
    - adafruit_minimqtt
    - adafruit_register
    - simpleio.mpy
    - adafruit_espatcontrol

References:
[1] https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-with-adafruit-io
'''

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
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("All secret keys are kept in secrets.py, please add them there!")
    raise

# Initialize an Adafruit IO HTTP API object
aiousername = secrets["aio_username"]
aiokey = secrets["aio_key"]

# Buzzer
NOTE_G4 = 392
NOTE_C5 = 523
buzzer = board.GP18

# Initialize UART connection to the ESP8266 WiFi Module.
RX = board.GP17
TX = board.GP16
uart = busio.UART(TX, RX, receiver_buffer_size=2048)  # Use large buffer as we're not using hardware flow control.
esp = adafruit_espatcontrol.ESP_ATcontrol(uart, 115200, debug=False)
requests.set_socket(socket, esp)
print("Resetting ESP module")
esp.soft_reset()
# Connect to Wi-Fi AP
esp.connect(secrets)
simpleio.tone(buzzer, NOTE_C5, duration=0.1)

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aiousername, aiokey, requests)
print("Connected to Adafruit IO...✅")

# Create feed. Please make sure same as at adafruit IO.
picowData1_feed = io.get_feed("picow.data1")
picowData2_feed = io.get_feed("picow.data2")

#  pack feed names into an array for the loop
feed_names = [picowData1_feed, picowData2_feed]
print("Feeds Created...✅")

clock = 10

while True:
    try:
        while not esp.is_connected:
            print("Connecting...")
            esp.connect(secrets)
        if clock > 10:
            # Dummy Value
            data1 = round(random.uniform(25,35),2)
            data2 = round(random.uniform(75,90),2)
            print("\nUpdating Adafruit IO...✅")
            simpleio.tone(buzzer, NOTE_G4, duration=0.1)
            simpleio.tone(buzzer, NOTE_C5, duration=0.15)
            
            #  send data to respective feeds
            data = [data1, data2]
            for z in range(len(data)):
                io.send_data(feed_names[z]["key"], data[z])
                print("sent %0.1f" % data[z])
                time.sleep(1)
            #  print sensor data to the REPL
            print("Data 1 = {:.2f}".format(data1))
            print("Data 2 = {:.2f}".format(data2))
            print()
            time.sleep(1)
            #  reset clock
            clock = 0
        else:
            clock += 1
    # pylint: disable=broad-except
    #  any errors, reset Pico W
    except Exception as e:
        print("Error:\n", str(e))
        print("Resetting microcontroller in 10 seconds")
        time.sleep(10)
        microcontroller.reset()
    #  delay
    time.sleep(1)
    print(clock)
