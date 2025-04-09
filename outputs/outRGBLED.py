from machine import Pin, PWM
import utime

rgb_values = {
    'red': (65535, 0, 0),
    'yellow': (65535, 65535, 0),
    'green': (0, 65535, 0),
    'off': (0, 0, 0)
}


class RGBLED:
    def __init__(self, red_pin, green_pin, blue_pin):
        self.red = PWM(Pin(red_pin))
        self.green = PWM(Pin(green_pin))
        self.blue = PWM(Pin(blue_pin))
        self.red.freq(1000)
        self.green.freq(1000)
        self.blue.freq(1000)

        self.blinking = False
        self.period = 1000  # ms
        self.last_toggle = utime.ticks_ms()
        self.blink_state = False
        self.blink_color = 'off'

    def color(self, r=0, g=0, b=0):
        self.red.duty_u16(r)
        self.green.duty_u16(g)
        self.blue.duty_u16(b)

    def set_color(self, name):
        r = rgb_values[name][0]
        g = rgb_values[name][1]
        b = rgb_values[name][2]
        self.color(r, g, b)

    def start_blinking(self, period_ms=1000, color='off'):
        self.blinking = True
        self.period = period_ms
        self.blink_color = color
        self.last_toggle = utime.ticks_ms()
        self.blink_state = False
        print('blinking start')

    def stop_blinking(self):
        self.blink_state = False
        self.set_color('off')
        print('blinking stopped')

    def update_LED(self):
        """Run Frequently"""
        if not self.blinking:
            return
        now = utime.ticks_ms()
        if now - self.last_toggle > self.period:
            self.last_toggle = now
            self.blink_state = not self.blink_state
            if self.blink_state:
                self.set_color(self.blink_color)
            else:
                self.set_color('off')
