import time
import math
import psycopg2
import json

from datetime import datetime


def round_up_to_nearest_log10(x):
    if x == 0:
        return 0
    elif x < 0:
        raise ValueError(
            "Negative numbers are not supported for this operation.")
    else:
        return math.ceil(math.log10(x))


_CLOCK_INFO = time.get_clock_info("perf_counter")
_PRECISION = -1*round_up_to_nearest_log10(_CLOCK_INFO.resolution)


def fetch_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        # log_fetch(args[0]["test"]["trace_id"], args[0], start_time, end_time, duration, args[1], result, json.dumps(args[2:], sort_keys=True))
        # print("Function " + func.__name__ + " total time: " + format(duration, f".{_PRECISION}f") + " seconds")
        return result
    return wrapper


def log_request(
        config_data,
        trace_id, 
        request_type, 
        request_subtype, 
        start_time, 
        end_time, 
        duration, 
        request, 
        response, 
        context
):
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {config_data["database"]["logging_schema"]}.{config_data["database"]["request_logging_table"]} 
                (
                    trace_id,
                    request_type,
                    request_subtype,
                    start_time, 
                    end_time, 
                    duration, 
                    request, 
                    response, 
                    context
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    trace_id,
                    request_type,
                    request_subtype,
                    start_time,
                    end_time,
                    duration,
                    json.dumps(request, separators=(',', ':'), sort_keys=True),
                    json.dumps(response, separators=(',', ':'), sort_keys=True),
                    json.dumps(context, separators=(',', ':'), sort_keys=True)
                )
            )
            connection.commit()
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


def request_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        duration = end_time - start_time  # duration as a timedelta

        log_request(
            args[0],
            args[1]["test"]["trace_id"], 
            func.__name__,
            args[-1],
            start_time, 
            end_time, 
            duration, 
            args[2], 
            result, 
            args[3:-1]
        )
        # print("Function " + func.__name__ + " total time: " + format(duration, f".{_PRECISION}f") + " seconds")
        return result
    return wrapper
