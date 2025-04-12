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


def core0_main(button, photo_resistor, water_level, gate):
    """Do Readings"""
    gate.calibrate_sensors()

    while True:
        photo_resistor.update()
        water_level.update()
        gate.update()


def core1_server():
    """Onboard Program to Communicate with client over Wi-Fi"""
    server.run_server(photo_resistor, water_level, )
    pass


if __name__ == '__main__':
    button_1 = inpButton.Button(pins['button1 pin'])
    photo_resistor = inpPhotoresistor.Photoresistor(pins['photo-resistor pin'])
    water_level = inpWaterLevelSensor.WaterLevelSensor(pins['water-level pin'])
    gate = inpSONARSensor.Gate(pins['sonar inner-TRIG pin'], pins['sonar inner-ECHO pin'],
                               pins['sonar outer-TRIG pin'], pins['sonar outer-ECHO pin'])

    _thread.start_new_thread(core1_server, (photo_resistor, water_level, gate))
    core0_main(button_1, photo_resistor, water_level, gate)
