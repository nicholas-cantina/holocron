import sys
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.memory import summarize
from src.storage import storage, retrieve


def _dedup_messages(messages):
    return list({message['id']: message for message in messages}.values())


def get_chat_memories(config_data, scenerio_data, bot_data, message):
    memories = retrieve.get_ltm(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["chat"]["num_ltm_memories_generate_chat"],
    )

    conversation_state = retrieve.get_mtm(
        config_data,
        scenerio_data,
        bot_data,
    )

    recent_messages = retrieve.get_stm(
        config_data,
        scenerio_data,
        bot_data,
        config_data["chat"]["num_recent_messages_generate_chat"],
    )
    recent_messages = _dedup_messages(recent_messages + [message])

    return {
        "memories": [
            message["metadata"]["summary"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"] for message in recent_messages],
    }


def get_answer_memories(config_data, scenerio_data, bot_data, message):
    memories = retrieve.get_ltm(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["create"]["num_ltm_memories_generate_answer"],
    )

    conversation_state = retrieve.get_mtm(
        config_data,
        scenerio_data,
        bot_data,
    )

    recent_messages = retrieve.get_stm(
        config_data,
        scenerio_data,
        bot_data,
        config_data["create"]["num_recent_messages_generate_answer"],
    )
    recent_messages = _dedup_messages(recent_messages + [message])

    return {
        "memories": [
            message["metadata"]["summary"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"] for message in recent_messages],
    }


def get_stm_summary_memories(config_data, scenerio_data, bot_data, message):
    memories = retrieve.get_ltm(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["summarize"]["num_ltm_memories_generate_mtm"],
    )

    conversation_state = retrieve.get_mtm(
        config_data,
        scenerio_data,
        bot_data,
    )

    recent_messages = retrieve.get_stm(
        config_data,
        scenerio_data,
        bot_data,
        config_data["summarize"]["num_recent_messages_generate_mtm"],
    )
    recent_messages = _dedup_messages(recent_messages + [message])

    return {
        "memories": [
            message["metadata"]["summary"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"] for message in recent_messages],
    }


def get_mtm_summary_memories(config_data, scenerio_data, bot_data, message):
    memories = retrieve.get_ltm(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["summarize"]["num_ltm_memories_generate_mtm"],
    )

    conversation_state = retrieve.get_mtm(
        config_data,
        scenerio_data,
        bot_data,
    )

    recent_messages = retrieve.get_stm(
        config_data,
        scenerio_data,
        bot_data,
        config_data["summarize"]["num_recent_messages_generate_mtm"],
    )
    recent_messages = _dedup_messages(recent_messages + [message])

    return {
        "memories": [
            message["metadata"]["summary"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"] for message in recent_messages],
    }


def get_ltm_summary_memories(config_data, scenerio_data, bot_data, message):
    memories = retrieve.get_ltm(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["summarize"]["num_ltm_memories_generate_ltm"],
    )

    conversation_state = retrieve.get_mtm(
        config_data,
        scenerio_data,
        bot_data,
    )

    recent_messages = retrieve.get_stm(
        config_data,
        scenerio_data,
        bot_data,
        config_data["summarize"]["num_recent_messages_generate_ltm"],
    )
    recent_messages = _dedup_messages(recent_messages + [message])

    return {
        "memories": [
            message["metadata"]["summary"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"] for message in recent_messages],
    }


def update_bot_stm(config_data, scenerio_data, bot_data, message):
    storage.save_message_to_stm(config_data, scenerio_data, bot_data, message)


def update_stm(config_data, scenerio_data, message):
    for bot_user_id in scenerio_data["users"]["bots"]:
        bot_data = config_data["test"]["bot_datas"][bot_user_id]
        update_bot_stm(config_data, scenerio_data, bot_data, message)


def update_bot_mtm(config_data, scenerio_data, bot_data, message):
    new_mtm = summarize.summarize_mtm_events(config_data, scenerio_data, bot_data, message)
    storage.save_conversation_state_to_mtm(config_data, scenerio_data, bot_data, new_mtm)


def update_mtm(config_data, scenerio_data, message):
    for bot_user_id in scenerio_data["users"]["bots"]:
        bot_data = config_data["test"]["bot_datas"][bot_user_id]
        update_bot_mtm(config_data, scenerio_data, bot_data, message)


def update_bot_ltm(config_data, scenerio_data, bot_data, message):
    new_ltm = summarize.get_summarize_ltm_events(config_data, scenerio_data, bot_data, message)
    storage.save_memory_to_ltm(config_data, scenerio_data, bot_data, new_ltm)


def update_ltm(config_data, scenerio_data, message):
    for bot_user_id in scenerio_data["users"]["bots"]:
        bot_data = config_data["test"]["bot_datas"][bot_user_id]
        update_bot_ltm(config_data, scenerio_data, bot_data, message)
