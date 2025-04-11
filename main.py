import _thread
import time
from machine import Pin
import network
import socket


def web_page():
    html = """<html>
<body>
    <h2>Raspberry Pi Pico Web Server with RGB LED</h2>
    <p>
    Current RGB at the LED = """"""
    </p>
    <p>
    Set the color of the RGB LED at the server<br>
    <form>
    <label for="rgb_color">Enter RGB Color in Hex including prefix 0x (e.g., 0x4321ef)</label>
    <input type="text" id="rgb_color" name="RGB_COLOR">
    <input type="submit" value="Submit">
    </form>
    </p>
</body>
</html>"""
    return html


def core0_main():
    pass


def core1_server():
    pass


if __name__ == '__main__':
    _thread.start_new_thread(core1_server, ())
    core0_main()
