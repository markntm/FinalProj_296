from machine import Pin, ADC
import utime


class Photoresistor:
    def __init__(self, pin):
        self.sensor = ADC(pin)
        self.threshold = 10000  # brightness value distinguishing day and night
        self.is_day = True
        self.sunrise_time = None
        self.sunset_time = None

    def read_light(self):
        return self.sensor.read_u16()

    def time_to_seconds(self, time):
        return time[3] * 3600 + time[4] * 60 + time[5]

    def check_alert(self, current_time):
        """Check if current time is sunrise or sunset and send alarm to user
        and make sure alarm is only set off once per sunrise and sunset."""
        if current_time == self.sunrise_time:
            """Alert Sunrise!"""

        elif current_time == self.sunset_time:
            """Alert Sunset!"""

    def update(self):
        """Run Frequently"""
        light_level = self.read_light()
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



