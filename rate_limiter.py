from datetime import datetime
import math
import time

ONE_SECOND_TO_MICROSECONDS = 1000000


# A rate limiter that will deduct from inputted datetime difference
class RateLimiter:
    def __init__(self, permits_per_second):
        self.permits_per_second = (1.0 / float(permits_per_second))

    @staticmethod
    def get_time_microseconds(elapsed_time):
        return (
               elapsed_time.days * 24 * 60 * 60 + elapsed_time.seconds) * ONE_SECOND_TO_MICROSECONDS + elapsed_time.microseconds

    # Assumes acquring 1 permit
    def acquire(self, microseconds_waited):
        seconds_to_wait = max(self.permits_per_second - RateLimiter.get_time_microseconds(
            microseconds_waited) / ONE_SECOND_TO_MICROSECONDS, 0)
        time.sleep(seconds_to_wait)
        return seconds_to_wait


if __name__ == '__main__':
    # Run a rate limiter test
    r = RateLimiter(60)
    while (True):
        before = datetime.now()
        time.sleep(0.01)  # Sleep ten milliseconds
        after = datetime.now()

        print(RateLimiter.get_time_microseconds(after - before))
        print(r.acquire(after - before))
