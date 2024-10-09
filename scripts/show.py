import os
import sys
import psycopg2
import json
import hashlib

from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def show_scenerio_messages_helper(config_data, scenario_data):
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    id,
                    timestamp,
                    user_id
                FROM (
                    SELECT 
                        metadata,
                        id,
                        timestamp,
                        user_id,
                        ROW_NUMBER() OVER (PARTITION BY id ORDER BY timestamp DESC) as rn
                    FROM {config_data["database"]["stm_schema"]}.{config_data["database"]["stm_table"]}
                    WHERE conversation_id = %s
                ) subquery
                WHERE rn = 1
                ORDER BY timestamp ASC
                LIMIT 10
            """, (
                scenario_data["id"],
            )
            )
            results = cursor.fetchall()
            print(json.dumps([
                {"metadata": metadata, "id": id, "timestamp": timestamp.isoformat(), "user_id": user_id}
                for metadata, id, timestamp, user_id in results
            ], indent=4))
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


def show_trace_requests_helper(config_data, scenario_data):
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    request_type,
                    request_subtype,
                    duration
                FROM {config_data["database"]["logging_schema"]}.{config_data["database"]["request_logging_table"]}
                WHERE trace_id=%s
                ORDER BY end_time ASC
                LIMIT 10
            """, (
                scenario_data["test"]["trace_id"],
            )
            )
            results = cursor.fetchall()
            print(json.dumps([
                {"request_type": request_type, "request_subtype": request_subtype, "duration": duration.total_seconds()}
                for request_type, request_subtype, duration in results
            ], indent=4))
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()
