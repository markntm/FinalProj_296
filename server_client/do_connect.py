import network
import time
from secret import secrets


def connect_to_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets["SSID"], secrets["PASSWORD"])

    while not wlan.isconnected:
        print("connecting to network...")
        time.sleep(0.5)

    if wlan.isconnected():
        print("Connection Successful.")
        status = wlan.ifconfig()
        print("status of ifconfig:", status)
        return status[0]  # Returns ip

