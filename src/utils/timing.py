import time
import math


def round_up_to_nearest_log10(x):
    if x == 0:
        return 0
    elif x < 0:
        raise ValueError(
            "Negative numbers are not supported for this operation.")
    else:
        # Compute the nearest higher order of magnitude
        return math.ceil(math.log10(x))


_CLOCK_INFO = time.get_clock_info("perf_counter")
_PRECISION = -1*round_up_to_nearest_log10(_CLOCK_INFO.resolution)


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        print("Function " + func.__name__ + " total time: " + format(duration, f".{_PRECISION}f"))
        return result
    return wrapper
