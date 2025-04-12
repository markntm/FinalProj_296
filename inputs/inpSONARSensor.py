from machine import Pin
import time


class SONARSensor:
    def __init__(self, trig_pin, echo_pin):
        self.TRIG = Pin(trig_pin, Pin.OUT)
        self.ECHO = Pin(echo_pin, Pin.IN)
        self.TRIG.low()

        self.idle_distance = None

    def distance(self, timeout_us=100000):
        self.TRIG.low()
        time.sleep_us(2)
        self.TRIG.high()
        time.sleep_us(10)
        self.TRIG.low()

        timeout_start = time.ticks_us()

        while self.ECHO.value() == 0:
            if time.ticks_diff(time.ticks_us(), timeout_start) > timeout_us:
                return -1
        time1 = time.ticks_us()

        timeout_start = time.ticks_us()

        while self.ECHO.value() == 1:
            if time.ticks_diff(time.ticks_us(), timeout_start) > timeout_us:
                return -1
        time2 = time.ticks_us()

        duration = time.ticks_diff(time2, time1)
        distance_cm = (duration * 0.0342) / 2
        return round(distance_cm, 2)

    def init_idle_distance(self, n=10, delay_s=0.1, tolerance_cm=2.0):
        readings = []

        for i in range(n):
            distance = self.distance()
            if distance != -1:
                readings.append(distance)
            time.sleep(delay_s)

        avg = sum(readings) / len(readings)
        deviations = [abs(r - avg) for r in readings]

        if all(dev < tolerance_cm for dev in deviations):
            self.idle_distance = round(avg, 2)
            print("Idle distance set to", self.idle_distance, "cm.")
            return True
        else:
            print("Idle distance unstable. Try again.")
            return False


class Gate:
    def __init__(self, inner_trig_pin, inner_echo_pin, outer_trig_pin, outer_echo_pin):
        self.innerSensor = SONARSensor(inner_trig_pin, inner_echo_pin)
        self.outerSensor = SONARSensor(outer_trig_pin, outer_echo_pin)
        self.chickenHeightLower_cm = 20
        self.chickenHeightUpper_cm = 40

        self.last_event_time = 0
        self.last_state = None
        self.inside_count = 0
        self.outside_count = 0

    def update(self, delay_ms=500):
        if time.ticks_diff(time.ticks_ms(), self.last_event_time) < delay_ms:
            return

        inner_distance = self.innerSensor.distance()
        outer_distance = self.outerSensor.distance()

        if inner_distance == -1 or outer_distance == -1:
            print("Inner distance unstable. Try again.")
            return

        inner_triggered = inner_distance < (self.innerSensor.idle_distance - self.chickenHeightLower_cm)
        outer_triggered = outer_distance < (self.outerSensor.idle_distance - self.chickenHeightLower_cm)

        if inner_triggered and not outer_triggered:
            self.last_state = 'A'
        elif outer_triggered and not inner_triggered:
            self.last_state = 'B'
        elif inner_triggered and outer_triggered:
            if self.last_state == 'A':
                self.inside_count += 1
                self.outside_count -= 1
                print("Chicken ENTERED.")
            elif self.last_state == 'B':
                self.outside_count += 1
                self.inside_count -= 1
                print("Chicken EXITED.")
            self.last_state = None

        self.last_event_time = time.ticks_ms()

    def calibrate_sensors(self):
        while True:
            if self.innerSensor.init_idle_distance() and self.outerSensor.init_idle_distance():
                return
            print("Retrying Gate Calibration...")

    def get_chicken_count(self):
        print("Inside:", self.inside_count, "| Outside:", self.outside_count)
        return self.inside_count, self.outside_count

    def reset_chicken_count(self, amt_chickens=7):
        self.inside_count = amt_chickens
        self.outside_count = 0

