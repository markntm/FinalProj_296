import network
import time
import urequests


def connect_to_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("SSID", "PASSWORD")
    while not wlan.isconnected:
        print("connecting to network...")

    if wlan.isconnected():
        print("Connection Successful.")
        status = wlan.ifconfig()
        print("status of ifconfig:", status)
        return status[0]  # Returns ip

