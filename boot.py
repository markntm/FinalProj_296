import network
import time
import machine
import ntptime
from secret import secrets

# Wi-Fi credentials
WIFI_SSID = secrets['SSID']
WIFI_PASSWORD = secrets['PASSWORD']

led = machine.Pin("LED", machine.Pin.OUT)


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            led.toggle()
            time.sleep(0.5)
            timeout -= 1
    led.on()
    print("Connected to Wi-Fi!")
    print('Network config:', wlan.ifconfig())
    return wlan.ifconfig()[0]  # Return IP address


def sync_time():
    for i in range(5):
        try:
            print("Setting system time...")
            ntptime.settime()
            print("System time set.")
            return
        except Exception as e:
            print(f"Failed to set system time: {e}")
            time.sleep(1)
    print("Giving up on setting system time.")


# Actual Boot
time.sleep(1)
ip = connect_to_wifi()
sync_time()
print("Boot complete. IP address:", ip)
