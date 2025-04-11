from machine import Pin, ADC
import utime
import time


class Photoresistor:
    def __init__(self, pin):
        self.sensor = ADC(pin)
        self.threshold = 10000  # brightness value distinguishing day and night
        self.is_day = True
        self.sunrise_time = None
        self.sunset_time = None

    def read(self):
        return self.sensor.read_u16()

    def time_to_seconds(self, time):
        return time[3] * 3600 + time[4] * 60 + time[5]

    def init_threshold(self, n=10, delay_s=0.1, tolerance=100):
        readings = []

        for i in range(n):
            light_level = self.read()
            readings.append(light_level)
            time.sleep(delay_s)

        avg = sum(readings) / len(readings)
        deviations = [abs(r - avg) for r in readings]

        if all(dev < tolerance for dev in deviations):
            self.threshold = round(avg, 2)
            print("Light level threshold set to", self.threshold, ".")
            return True
        else:
            print("Light level unstable. Try again.")
            return False

    def check_alert(self, current_time):
        """Check if current time is sunrise or sunset and send alarm to user
        and make sure alarm is only set off once per sunrise and sunset."""
        if current_time == self.sunrise_time:
            """Alert Sunrise!"""

        elif current_time == self.sunset_time:
            """Alert Sunset!"""

    def update(self):
        """Run Frequently"""
        light_level = self.read()
        current_time = utime.localtime()

        self.check_alert(self.time_to_seconds(current_time))

        if light_level > self.threshold:
            if not self.is_day:
                self.sunrise_time = current_time
                print('sunrise detected, updating sunrise:', utime.strftime("%H:%M:%S", current_time))
            self.is_day = True

        else:
            if self.is_day:
                self.sunset_time = current_time
                print('sunset detected, updating sunset:', utime.strftime("%H:%M:%S", current_time))
            self.is_day = False



