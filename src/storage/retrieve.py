import os
import sys
import psycopg2

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import timing, generate
from src.storage import storage


@timing.timing_decorator
def _fetch_similar_ltms(
    config_data,
    scenerio_data,
    bot_data,
    message,
    num_messages,
):
    query_data = storage.get_ltm_bot_message_query_data(scenerio_data, bot_data, message)
    embedding = generate.get_embeddings(config_data, message, config_data["search"]["embedding_model"])
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    id,
                    timestamp,
                    user_id,
                    embedding <=> %s::vector AS distance
                FROM {config_data["database"]["ltm_schema"]}.{config_data["database"]["ltm_table"]}
                WHERE bot_in_conversation_identity_id=%s
                    AND conversation_id=%s
                ORDER BY distance, timestamp DESC
                LIMIT %s
            """, (
                embedding,
                query_data["bot_in_conversation_identity_id"],
                query_data["conversation_id"],
                num_messages
            )
            )
            results = cursor.fetchall()
            return [
                {"metadata": metadata, "id": id, "timestamp": timestamp, "user_id": user_id}
                for metadata, id, timestamp, user_id, _ in results
            ]
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


def get_ltm(config_data, scenerio_data, bot_data, message, num_messages):
    return _fetch_similar_ltms(config_data, scenerio_data, bot_data, message, num_messages)


def get_mtm_query_data(scenerio_data, bot_data):
    return {
        "user_id": bot_data["id"],
        "conversation_id": scenerio_data["id"],
    }


@timing.timing_decorator
def _fetch_mtm(config_data, scenerio_data, bot_data):
    query_data = get_mtm_query_data(scenerio_data, bot_data)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    state
                FROM {config_data["database"]["mtm_schema"]}.{config_data["database"]["mtm_table"]}
                WHERE conversation_id = %s
                    AND user_id = %s
                LIMIT 1
                """, (
                query_data["conversation_id"],
                query_data["user_id"],
            )
            )
            results = cursor.fetchall()
            if len(results) == 0:
                return None
            elif len(results) == 1:
                return results[0]
            else:
                raise ValueError("More than one conversation state found")
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


def get_mtm(config_data, scenerio_data, bot_data):
    return _fetch_mtm(config_data, scenerio_data, bot_data)


def get_stm_conversation_query_data(scenerio_data):
    return {
        "conversation_id": scenerio_data["id"],
    }


def get_stm_bot_query_data(scenerio_data, bot_data):
    return {
        **get_stm_conversation_query_data(scenerio_data),
        "bot_in_conversation_identity_id": bot_data["id"],
    }


@timing.timing_decorator
def _fetch_recent_stms(
    config_data,
    scenerio_data,
    bot_data,
    num_messages,
):
    query_data = storage.get_stm_bot_query_data(scenerio_data, bot_data)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    id,
                    timestamp, 
                    user_id
                FROM {config_data["database"]["stm_schema"]}.{config_data["database"]["stm_table"]}
                WHERE bot_in_conversation_identity_id=%s
                    AND conversation_id=%s
                ORDER BY timestamp DESC
                LIMIT %s
                """, (
                query_data["bot_in_conversation_identity_id"],
                query_data["conversation_id"],
                num_messages
            )
            )
            results = cursor.fetchall()
            return [
                {"metadata": metadata, "id": id, "timestamp": timestamp, "user_id": user_id}
                for metadata, id, timestamp, user_id in results
            ]
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


def get_stm(config_data, scenerio_data, bot_data, num_messages):
    return _fetch_recent_stms(config_data, scenerio_data, bot_data, num_messages)


@timing.timing_decorator
def _fetch_recent_messages_for_conversation(
    config_data,
    scenerio_data,
    num_messages,
):
    query_data = storage.get_stm_conversation_query_data(scenerio_data)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    id,
                    timestamp,
                    user_id
                FROM {config_data["database"]["stm_schema"]}.{config_data["database"]["stm_table"]}
                WHERE conversation_id=%s
                ORDER BY timestamp DESC
                LIMIT %s
                """, (
                query_data["conversation_id"],
                num_messages
            )
            )
            results = cursor.fetchall()
            return [
                {"metadata": metadata, "id": id, "timestamp": timestamp, "user_id": user_id}
                for metadata, id, timestamp, user_id in results
            ]
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


def get_latest_event(config_data, scenerio_data):
    return _fetch_recent_messages_for_conversation(config_data, scenerio_data, 1)[0]
