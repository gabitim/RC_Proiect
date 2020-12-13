# timer class
import time


class Timer:
    TIMER_STOP = -1

    def __init__(self, duration=0.5):
        self.start_time = self.TIMER_STOP
        self.duration = duration

    def start(self):
        if self.start_time == self.TIMER_STOP:
            self.start_time = time.time()

    def stop(self):
        if self.start_time != self.TIMER_STOP:
            self.start_time = self.TIMER_STOP

    def restart(self):
        self.start_time = time.time()

    # determining whether the timer is running
    def running(self):
        return self.start_time != self.TIMER_STOP

    # check if we have a timeout
    def timeout(self):
        if not self.running():
            return False
        else:
            return time.time() - self.start_time >= self.duration

    def set_timeout(self, duration):
        self.duration = duration
