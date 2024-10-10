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


def show_bot_mtm_helper(config_data, scenario_data, bot_data):
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    state
                FROM ltm.summaries
                WHERE user_id = %s
                    AND bot_in_conversation_user_id = %s
            """, (
                scenario_data["id"],
                bot_data["id"],
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


def show_bot_ltm_helper(config_data, scenario_data, bot_data):
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    state
                    
                FROM mtm.conversation_summaries
                WHERE conversation_id = %s
                  AND user_id = %s
            """, (
                scenario_data["id"],
                bot_data["id"],
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


def show_scenerio_messages_helper(config_data, scenario_data):
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM (
                  SELECT metadata, id, timestamp, user_id 
                  FROM (
                      SELECT 
                          metadata,
                          id,
                          timestamp,
                          user_id,
                          ROW_NUMBER() OVER (PARTITION BY id ORDER BY timestamp DESC) as rn
                      FROM stm.messages
                      WHERE conversation_id = %s
                  ) subquery
                  WHERE rn = 1
                  ORDER BY timestamp DESC
                  LIMIT 10
              ) final_subquery
              ORDER BY timestamp ASC;
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
              FROM (
                  SELECT 
                      request_type,
                      request_subtype,
                      duration,
                      end_time
                  FROM {config_data["database"]["logging_schema"]}.{config_data["database"]["request_logging_table"]}
                  WHERE trace_id = %s
                  ORDER BY end_time DESC
                  LIMIT 10
              ) subquery
              ORDER BY end_time ASC;
            """, (
                str(scenario_data["test"]["trace_id"]),
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
