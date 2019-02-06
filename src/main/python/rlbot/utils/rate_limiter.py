import time
from timeit import timeit


# A rate limiter that will deduct from inputted datetime difference
class RateLimiter:
    def __init__(self, permits_per_second):
        self.time_per_tick = 1.0 / float(permits_per_second)
        self.then = time.perf_counter()
        self.accumulator = 0.0

    # Assumes acquring 1 permit
    def acquire(self):
        while True:
            now = time.perf_counter()
            self.accumulator += now - self.then
            self.then = now
            if self.accumulator > self.time_per_tick:
                self.accumulator -= self.time_per_tick
                break
            else:
                time.sleep(0.002)


if __name__ == '__main__':

    # Run a rate limiter test
    for fps in (30, 60, 120, 240):

        print("fps :", fps)

        rate_limiter = RateLimiter(fps)

        def test_function():
            time.sleep(0.003)  # simulated bot get_output time
            rate_limiter.acquire()

        n_times = fps
        time_taken = timeit(test_function, number=n_times)

        average_time = time_taken / n_times

        print("Average time :", average_time * 1000, "ms.")
        print("Frequency :", 1 / average_time, "hz.")
        print("Target is", round(1000 / fps, 5), "ms and", fps, "hz.")
        print()
