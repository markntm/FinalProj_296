from machine import ADC
import time


class WaterLevelSensor:
    def __init__(self, pin, empty_threshold=1000, low_threshold=5000):
        self.sensor = ADC(pin)
        self.empty_threshold = empty_threshold
        self.low_threshold = low_threshold
        self.level = 0
        self.status = "unknown"

    def read(self):
        return self.sensor.read_u16()

    def get_status(self):
        return self.status

    def get_level(self):
        return self.level

    def init_low_threshold(self, n=10, delay_s=0.1, tolerance=100):
        readings = []

        for i in range(n):
            water_level = self.read()
            readings.append(water_level)
            time.sleep(delay_s)

        avg = sum(readings) / len(readings)
        deviations = [abs(r - avg) for r in readings]

        if all(dev < tolerance for dev in deviations):
            self.low_threshold = round(avg, 2)
            print("Low water level threshold set to", self.low_threshold, ".")
            return True
        else:
            print("Water level unstable. Try again.")
            return False

    def init_empty_threshold(self, n=10, delay_s=0.1, tolerance=100):
        readings = []

        for i in range(n):
            water_level = self.read()
            readings.append(water_level)
            time.sleep(delay_s)

        avg = sum(readings) / len(readings)
        deviations = [abs(r - avg) for r in readings]

        if all(dev < tolerance for dev in deviations):
            self.empty_threshold = round(avg, 2)
            print("Empty water level threshold set to", self.empty_threshold, ".")
            return True
        else:
            print("Water level unstable. Try again.")
            return False

    def update(self):
        """Run Frequently"""
        self.level = self.read()

        if self.level < self.empty_threshold:
            self.status = "empty"
        elif self.level < self.low_threshold:
            self.status = "low"
        else:
            self.status = "safe"
