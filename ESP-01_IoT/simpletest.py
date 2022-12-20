'''
Pi Pico: Scan for available WiFi AP, connect to the speicifed AP and ping 8.8.8.8.

Hardware:
- Maker Pi Pico
- ESP8266 WiFi module with Espressif AT Firmware v2.2.0 and above.

Where to Buy?
https://my.cytron.io/p-maker-pi-pico-simplifying-raspberry-pi-pico-for-beginners-and-kits

Additional Library:
- adafruit_requests.mpy
- adafruit_espatcontrol

References:
[1] https://github.com/CytronTechnologies/MAKER-PI-PICO
'''

import time
import board
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

print("Resetting ESP module")
esp.soft_reset()

first_pass = True
while True:
    try:
        if first_pass:
            print("\nScanning for WiFi AP...")
            for ap in esp.scan_APs():
                print(ap)
                
            print("\nConnecting...")
            esp.connect(secrets)
            print("IP address:", esp.local_ip)
            print("ESP Firmware Version:", esp.version)
            print()
            first_pass = False
            
        print("Pinging 8.8.8.8...", end="")
        print(esp.ping("8.8.8.8"))
        time.sleep(10)
        
    except (ValueError, RuntimeError, adafruit_espatcontrol.OKError) as e:
        print("Failed, retrying\n", e)
