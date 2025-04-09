from machine import ADC


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

    def update(self):
        """Run Frequently"""
        self.level = self.read()

        if self.level < self.empty_threshold:
            self.status = "empty"
        elif self.level < self.low_threshold:
            self.status = "low"
        else:
            self.status = "safe"
