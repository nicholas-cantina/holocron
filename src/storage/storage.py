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


def get_conversation_bot_message_query_data(scenerio_data, bot_data, message):
    return {
        "bot_in_channel_identity_id": bot_data["id"],
        "external_channel_id": scenerio_data["conversation"]["id"],
        "external_identity_id": message["user_id"],
        "message_id": hash_string(message["user_id"] + ":" + message["message"]),
        "message_timestamp": datetime.now(),
        "metadata": {
            **message
        }
    }


def get_conversation_bot_query_data(scenerio_data, bot_data):
    return {
        "bot_in_channel_identity_id": bot_data["id"],
        "external_channel_id": scenerio_data["conversation"]["id"],
    }

def get_conversation_query_data(scenerio_data, bot_data):
    return {
        "external_channel_id": scenerio_data["conversation"]["id"],
    }


@timing.timing_decorator
def save_message(
    config_data,
    scenerio_data,
    bot_data,
    message,
):
    query_data = get_conversation_bot_message_query_data(scenerio_data, bot_data, message)
    message_embedding = generate.get_embeddings(config_data, message, config_data["search"]["embedding_model"])
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {config_data["database"]["schema"]}.{config_data["database"]["message_table"]} 
                (
                    bot_in_channel_identity_id, 
                    external_channel_id, 
                    external_identity_id, 
                    message_id, 
                    message_timestamp, 
                    message_embedding, 
                    metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s::vector, %s)
                """,
                (   
                    query_data["bot_in_channel_identity_id"],
                    query_data["external_channel_id"],
                    query_data["external_identity_id"],
                    query_data["message_id"],
                    query_data["message_timestamp"],
                    message_embedding,
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


@timing.timing_decorator
def save_created_event(
    config_data,
    scenerio_data,
    bot_data,
    message,
):
    query_data = get_conversation_bot_message_query_data(scenerio_data, bot_data, message)
    message_embedding = generate.get_embeddings(config_data, message, config_data["search"]["embedding_model"])
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {config_data["database"]["schema"]}.{config_data["database"]["message_table"]} 
                (
                    bot_in_channel_identity_id, 
                    external_channel_id, 
                    external_identity_id, 
                    message_id, 
                    message_timestamp, 
                    message_embedding, 
                    metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s::vector, %s)
                """,
                (   
                    query_data["bot_in_channel_identity_id"],
                    query_data["external_channel_id"],
                    query_data["external_identity_id"],
                    query_data["message_id"],
                    query_data["message_timestamp"],
                    message_embedding,
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


def save_bot_state(
    config_data,
    scenerio_data,
    bot_data,
    state,
):
    pass  # TODO: add this]


def save_conversation_state(
    config_data,
    scenerio_data,
    state,
):
    pass  # TODO: add this