import machine
import time
import ntptime


def sync_time():
    try:
        ntptime.settime()
        print("Time synced")
    except:
        print("Failed to sync time")


def get_current_time():
    try:
        return time.localtime()
    except:
        return None


def time_str(tm):
    return f"{tm[3]:02d}:{tm[4]:02d}"


class TimedMotorDoor:
    def __init__(self, pin1, pin2, gate=None, total_chickens=7,
                 open_time1="06:30", open_time2="17:00",
                 motor_run_time_s=5, close_delay_s=60, grace_period_s=90):
        self.motor1 = machine.Pin(pin1, machine.Pin.OUT)
        self.motor2 = machine.Pin(pin2, machine.Pin.OUT)

        self.gate = gate
        self.total_chickens = total_chickens

        self.open_time1 = open_time1
        self.open_time2 = open_time2
        self.open_times = [open_time1, open_time2]

        self.motor_run_time_s = motor_run_time_s
        self.close_delay_s = close_delay_s
        self.grace_period_s = grace_period_s

        self.state = "idle"
        self.last_triggered = set()
        self.action_start_time = None

        self.stop_motor()

    def clockwise(self):
        self.motor1.high()
        self.motor2.low()

    def anticlockwise(self):
        self.motor1.low()
        self.motor2.high()

    def stop_motor(self):
        self.motor1.low()
        self.motor2.low()

    def update(self):
        now = get_current_time()
        if now is None:
            print("Time not available.")
            return

        now_str = time_str(now)
        now_seconds = now[3] * 3600 + now[4] * 60 + now[5]

        # Reset daily triggers at midnight
        if now_str == "00:00":
            self.last_triggered.clear()

        # Check for scheduled opening
        for sched in self.open_times:
            h, m = map(int, sched.split(":"))
            sched_seconds = h * 3600 + m * 60

            if sched not in self.last_triggered:
                if 0 <= now_seconds - sched_seconds <= self.grace_period_s:
                    self.clockwise()
                    self.state = "opening"
                    self.action_start_time = time.ticks_ms()
                    self.last_triggered.add(sched)
                    print(f"Door opening at {now_str}")
                    return

        # Motor state transitions
        if self.state == "opening":
            if time.ticks_diff(time.ticks_ms(), self.action_start_time) >= self.motor_run_time_s * 1000:
                self.stop_motor()
                self.state = "waiting_to_close"
                self.action_start_time = time.ticks_ms()
                print("Door fully open")

        elif self.state == "waiting_to_close":
            # Wait until all chickens are in before closing
            if self.gate and self.gate.inside_count < self.total_chickens:
                print(f"Waiting for chickens... ({self.gate.inside_count}/{self.total_chickens} inside)")
                return

            if time.ticks_diff(time.ticks_ms(), self.action_start_time) >= self.close_delay_s * 1000:
                self.anticlockwise()
                self.state = "closing"
                self.action_start_time = time.ticks_ms()
                print("Door closing...")

        elif self.state == "closing":
            if time.ticks_diff(time.ticks_ms(), self.action_start_time) >= self.motor_run_time_s * 1000:
                self.stop_motor()
                self.state = "idle"
                print("Door fully closed")

    def set_open_time1(self, time_str):
        self.open_time1 = time_str
        self._refresh_open_times()

    def set_open_time2(self, time_str):
        self.open_time2 = time_str
        self._refresh_open_times()

    def _refresh_open_times(self):
        self.open_times = [self.open_time1, self.open_time2]
        self.last_triggered.clear()
