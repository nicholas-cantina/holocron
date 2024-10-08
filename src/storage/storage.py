import os
import sys
import psycopg2
import json
import hashlib

from datetime import datetime

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import timing, generate


def hash_string(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode("utf-8"))
    hashed_string = hash_object.hexdigest()

    return hashed_string


def format_summary(summary_without_metadata):
    content = summary_without_metadata["summary"]
    return {
        "id": summary_without_metadata["id"],
        "timestamp": datetime.now(),
        "user_id": summary_without_metadata["user_id"],
        "metadata": {
            "summary": content,  # TODO: add retrieval metadata
        }
    }


def format_message_with_content(config_data, message_without_metadata, content):
    return {
        "id": message_without_metadata["id"],
        "timestamp": datetime.now(),
        "user_id": message_without_metadata["user_id"],
        "metadata": {
            "message": content
        }
    }


def format_message(config_data, message_without_metadata):
    bot_data = config_data["test"]["bot_datas"][message_without_metadata["user_id"]]

    content = {
        "message": message_without_metadata["message"],
        "full_name": bot_data["full_name"],
        "first_name": bot_data["first_name"],
        "user_id": message_without_metadata["user_id"],
    }
    return format_message_with_content(config_data, message_without_metadata, content)


def get_ltm_bot_message_query_data(scenario_data, bot_data, message):
    return get_stm_bot_message_query_data(scenario_data, bot_data, message)


@timing.timing_decorator
def save_memory_to_ltm(
    config_data,
    scenario_data,
    bot_data,
    memory,
):
    query_data = get_ltm_bot_message_query_data(scenario_data, bot_data, memory)
    embedding = generate.get_embeddings(
        config_data, memory, config_data["search"]["embedding_model"])
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {config_data["database"]["ltm_schema"]}.{config_data["database"]["ltm_table"]} 
                (
                    bot_in_conversation_identity_id, 
                    conversation_id, 
                    user_id, 
                    id, 
                    timestamp, 
                    embedding, 
                    metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s::vector, %s)
                """,
                (
                    query_data["bot_in_conversation_identity_id"],
                    query_data["conversation_id"],
                    query_data["user_id"],
                    query_data["id"],
                    query_data["timestamp"],
                    embedding,
                    json.dumps(query_data["metadata"], separators=(',', ':'))
                )
            )
            connection.commit()
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


def get_conversation_mtm_query_data(scenario_data, state):
    return {
        "conversation_id": scenario_data["id"],
        "state": json.dumps(state),
    }


def get_mtm_query_data(scenario_data, bot_data, state):
    return {
        **get_conversation_mtm_query_data(scenario_data, state),
        "user_id": bot_data["id"],
    }


@timing.timing_decorator
def save_conversation_state_to_mtm(config_data, scenario_data, bot_data, state):
    query_data = get_mtm_query_data(scenario_data, bot_data, state)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {config_data["database"]["mtm_schema"]}.{config_data["database"]["mtm_table"]} 
                (
                    conversation_id,
                    user_id,
                    state
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (conversation_id, user_id) DO UPDATE
                SET 
                    conversation_id = EXCLUDED.conversation_id,
                    user_id = EXCLUDED.user_id,
                    state = EXCLUDED.state
                """,
                (
                    query_data["conversation_id"],
                    query_data["user_id"],
                    query_data["state"]
                )
            )
            connection.commit()
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


def get_stm_conversation_query_data(scenario_data):
    return {
        "conversation_id": scenario_data["id"],
    }


def get_stm_bot_query_data(scenario_data, bot_data):
    return {
        **get_stm_conversation_query_data(scenario_data),
        "bot_in_conversation_identity_id": bot_data["id"],
    }


def get_stm_bot_message_query_data(scenario_data, bot_data, message):
    return {
        **get_stm_bot_query_data(scenario_data, bot_data),
        **message,
    }


@timing.timing_decorator
def save_message_to_stm(
    config_data,
    scenario_data,
    bot_data,
    message,
):
    query_data = get_stm_bot_message_query_data(scenario_data, bot_data, message)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {config_data["database"]["stm_schema"]}.{config_data["database"]["stm_table"]} 
                (
                    bot_in_conversation_identity_id, 
                    conversation_id, 
                    user_id, 
                    id, 
                    timestamp, 
                    metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    query_data["bot_in_conversation_identity_id"],
                    query_data["conversation_id"],
                    query_data["user_id"],
                    query_data["id"],
                    query_data["timestamp"],
                    json.dumps(query_data["metadata"], separators=(',', ':'))
                )
            )
            connection.commit()
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()
