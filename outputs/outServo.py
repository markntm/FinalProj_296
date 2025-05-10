from machine import Pin, PWM
import time
import ntptime


def interval_mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def servo_write(pwm_pin, angle):
    pulse_width = interval_mapping(angle, 0, 180, 0.5, 2.5)  # ms
    duty_u16 = int(interval_mapping(pulse_width, 0, 20, 0, 65535))
    pwm_pin.duty_u16(duty_u16)


def get_current_time():
    try:
        return time.localtime()
    except:
        return None


class TimedServo:
    def __init__(self, pin, open_times=["06:00", "17:00"], open_duration_s=10, grace_period_s=90):
        self.servo = PWM(Pin(pin))
        self.servo.freq(50)

        self.open_times = open_times  # List of "HH:MM" strings
        self.open_duration_s = open_duration_s
        self.grace_period_s = grace_period_s

        self.is_open = False
        self.open_timestamp = None
        self.last_triggered_times = set()  # Tracks "HH:MM" already triggered

        servo_write(self.servo, 0)  # Ensure it's closed at start

    def update(self):
        now = get_current_time()  # checks for current time
        if now is None:
            print("Time not available.")
            return

        now_seconds = now[3] * 3600 + now[4] * 60 + now[5]

        # Check if we're within the grace window for any un-triggered time
        for sched_time in self.open_times:
            h, m = map(int, sched_time.split(":"))
            sched_seconds = h * 3600 + m * 60

            if sched_time not in self.last_triggered_times:
                if 0 <= now_seconds - sched_seconds <= self.grace_period_s:
                    servo_write(self.servo, 180)
                    self.is_open = True
                    self.open_timestamp = time.ticks_ms()
                    self.last_triggered_times.add(sched_time)
                    break

        # Close after duration
        if self.is_open and self.open_timestamp is not None:
            elapsed = time.ticks_diff(time.ticks_ms(), self.open_timestamp) / 1000
            if elapsed >= self.open_duration_s:
                servo_write(self.servo, 0)
                self.is_open = False
                self.open_timestamp = None
                print("Servo CLOSED after", self.open_duration_s, "seconds.")

    def set_open_times(self, time_list):
        self.open_times = time_list
        self.last_triggered_times.clear()

    def set_open_duration(self, duration_s):
        self.open_duration_s = duration_s

    def sync_time(self):
        try:
            ntptime.settime()
            print("Time synced with NTP.")
        except:
            print("Failed to sync time.")
