import _thread
import time
from server_client import server
from inputs import inpPhotoresistor, inpSONARSensor, inpWaterLevelSensor
from outputs import outRGBLED, outServo, outMotor


pins = {
    "servo pin": 0,
    "R-LED pin": 0,
    "G-LED pin": 0,
    "B-LED pin": 0,
    "motor1 pin": 0,
    "motor2 pin": 0,
    "photo-resistor pin": 0,
    "water-level pin": 0,
    "sonar inner-TRIG pin": 0,
    "sonar inner-ECHO pin": 0,
    "sonar outer-TRIG pin": 0,
    "sonar outer-ECHO pin": 0
}


def core0_main(photo_resistor, water_level, gate, rgb_led, servo, motor_door):
    """Do Readings"""
    print("Core 0 Reading: On")
    gate.calibrate_sensors()

    while True:
        photo_resistor.update()
        water_level.update()
        gate.update()
        rgb_led.update()
        servo.update()
        motor_door.update()

        if motor_door:
            motor_door.update()
            server.sensor_cache["motor_door_state"] = motor_door.state
            server.sensor_cache["motor_open_times"] = ", ".join(motor_door.open_times)
            server.sensor_cache["motor_close_times"] = ", ".join(motor_door.close_times)

        if servo:
            servo.update()
            server.sensor_cache["servo_door_state"] = servo.state
            server.sensor_cache["servo_open_times"] = ", ".join(servo.open_times)
            server.sensor_cache["servo_close_times"] = ", ".join(servo.close_times)

        time.sleep(3)  # change for more frequent reading after testing server
    # make a safe way to exit program
    # print("Core 0 Reading: Off")


def core1_server():
    """Onboard Program to Communicate with client over Wi-Fi"""
    server.setup_devices(photo_resistor, water_level, gate, motor_door, servo)
    server.run_server()


if __name__ == '__main__':
    rgb_led = outRGBLED.RGBLED(
        red_pin=pins["R-LED pin"],
        green_pin=pins["G-LED pin"],
        blue_pin=pins["B-LED pin"]
    )
    servo = outServo.TimedServo(
        pin=pins["servo pin"]
    )
    photo_resistor = inpPhotoresistor.Photoresistor(
        pin=pins['photo-resistor pin']
    )
    water_level = inpWaterLevelSensor.WaterLevelSensor(
        pin=pins['water-level pin']
    )
    gate = inpSONARSensor.Gate(
        inner_trig_pin=pins['sonar inner-TRIG pin'],
        inner_echo_pin=pins['sonar inner-ECHO pin'],
        outer_trig_pin=pins['sonar outer-TRIG pin'],
        outer_echo_pin=pins['sonar outer-ECHO pin']
    )
    motor_door = outMotor.TimedMotorDoor(
        pin1=pins['motor1 pin'],
        pin2=pins['motor2 pin'],
        gate=gate
    )

    _thread.start_new_thread(core1_server, ())
    core0_main(photo_resistor, water_level, gate, rgb_led, servo, motor_door)
