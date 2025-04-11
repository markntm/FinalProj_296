import _thread
import time
from machine import Pin
import network
import socket
from server_client import server
from inputs import inpButton, inpPhotoresistor, inpSONARSensor, inpWaterLevelSensor


pins = {
    "button1 pin": 0,
    "photo-resistor pin": 0,
    "water-level pin": 0,
    "sonar inner-TRIG pin": 0,
    "sonar inner-ECHO pin": 0,
    "sonar outer-TRIG pin": 0,
    "sonar outer-ECHO pin": 0
}


def load_index_html():
    """Converting index.html to response format"""
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error Loading HTML</h1>"


def web_page(inside, outside):
    """Creating response"""
    html = load_index_html()
    html = html.replace("{{inside}}", str(inside))
    html = html.replace("{{outside}}", str(outside))
    return html


def core0_main():
    """Do Readings"""
    button_1 = inpButton.Button(pins['button1 pin'])
    photo_resistor = inpPhotoresistor.Photoresistor(pins['photo-resistor pin'])
    water_level = inpWaterLevelSensor.WaterLevelSensor(pins['water-level pin'])
    gate = inpSONARSensor.Gate(pins['sonar inner-TRIG pin'], pins['sonar inner-ECHO pin'],
                               pins['sonar outer-TRIG pin'], pins['sonar outer-ECHO pin'])

    gate.calibrate_sensors()

    while True:
        photo_resistor.update()
        water_level.update()
        gate.update()


def core1_server():
    """Onboard Program to Communicate with client over Wi-Fi"""
    UDPServer, BUFFER_SIZE = server.server_stuff()

    while True:
        conn, addr = UDPServer.accept()
        print("Got a connection from", addr)
        request = conn.recv(BUFFER_SIZE)
        request = str(request)



        response = web_page()
        conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n')
        conn.sendall(response)
        conn.close()

    pass


if __name__ == '__main__':
    _thread.start_new_thread(core1_server, ())
    core0_main()
