from machine import Pin
import enum
import time


class Job(enum.Enum):
    up = 1
    down = 2
    left = 3
    right = 4


class Button:
    def __init__(self, pin, job=1, debounce_ms=100):
        self.sensor = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.job = job
        self.debounce_ms = debounce_ms
        self.last_state = 1
        self.last_debounce_time = time.ticks_ms()
        self.button_state = 1
        self.last_press_time = 0

    def update(self):
        reading = self.sensor.value()

        if reading != self.last_state:
            self.last_debounce_time = time.ticks_ms()

        if time.ticks_diff(time.ticks_ms(), self.last_debounce_time) > self.debounce_ms:
            if reading != self.button_state:
                self.button_state = reading
                if self.button_state == 0:
                    self.last_press_time = time.ticks_ms()
                    return True  # New valid press
        self.last_state = reading
        return False

