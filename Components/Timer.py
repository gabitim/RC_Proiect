# timer class
import time


class Timer:
    TIMER_STOP = -1

    def __init__(self, duration=0.5):
        self.start_time = self.TIMER_STOP
        self.duration = duration

    # start the timer
    def start(self):
        if self.start_time == self.TIMER_STOP:
            self.start_time = time.time()

    # stop the timer
    def stop(self):
        if self.start_time != self.TIMER_STOP:
            self.start_time = self.TIMER_STOP

    # determining whether the timer is running
    def timer_is_running(self):
        return self.start_time != self.TIMER_STOP

    def timeout(self):
        if not self.timer_is_running():
            return False
        else:
            return time.time() - self.start_time >= self.duration

    def set_timeout(self, duration):
        self.duration = duration
