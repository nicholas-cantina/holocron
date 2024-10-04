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
            message["metadata"]["summary"]["content"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"]["content"] for message in recent_messages],
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
            message["metadata"]["summary"]["content"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"]["content"] for message in recent_messages],
    }


def get_stm_summary_memories(config_data, scenerio_data, bot_data, message):
    memories = retrieve.get_ltm(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["summary"]["num_ltm_memories_generate_mtm_summary"],
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
        config_data["summary"]["num_recent_messages_generate_mtm_summary"],
    )
    recent_messages = _dedup_messages(recent_messages + [message])

    return {
        "memories": [
            message["metadata"]["summary"]["content"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"]["content"] for message in recent_messages],
    }


def get_mtm_summary_memories(config_data, scenerio_data, bot_data, message):
    memories = retrieve.get_ltm(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["summary"]["num_ltm_memories_generate_mtm_summary"],
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
        config_data["summary"]["num_recent_messages_generate_mtm_summary"],
    )
    recent_messages = _dedup_messages(recent_messages + [message])

    return {
        "memories": [
            message["metadata"]["summary"]["content"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"]["content"] for message in recent_messages],
    }


def get_ltm_summary_memories(config_data, scenerio_data, bot_data, message):
    memories = retrieve.get_ltm(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["summary"]["num_ltm_memories_generate_ltm_summary"],
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
        config_data["summary"]["num_recent_messages_generate_ltm_summary"],
    )
    recent_messages = _dedup_messages(recent_messages + [message])

    return {
        "memories": [
            message["metadata"]["summary"]["content"] for message in memories if
            message["id"] not in
            [message["id"] for message in recent_messages]
        ],
        "conversation_state": conversation_state,
        "recent_messages": [message["metadata"]["message"]["content"] for message in recent_messages],
    }


def update_bot_stm(config_data, scenerio_data, bot_data, event):
    storage.save_message_to_stm(config_data, scenerio_data, bot_data, event)


def update_stm(config_data, scenerio_data, message):
    for bot_data in scenerio_data["users"]["bots"]:
        update_bot_stm(config_data, scenerio_data, bot_data, message)


def update_bot_mtm(config_data, scenerio_data, bot_data, message):
    new_mtm = summarize.summarize_mtm_events(config_data, scenerio_data, bot_data, message)
    storage.save_conversation_state_to_mtm(config_data, scenerio_data, bot_data, new_mtm)


def update_mtm(config_data, scenerio_data, message):
    for bot_data in scenerio_data["users"]["bots"]:
        update_bot_mtm(config_data, scenerio_data, bot_data, message)


def update_bot_ltm(config_data, scenerio_data, bot_data, message):
    new_ltm = summarize.summarize_ltm_events(config_data, scenerio_data, bot_data, message)
    storage.save_memory_to_ltm(config_data, scenerio_data, bot_data, message)


def update_ltm(config_data, scenerio_data, message):
    for bot_data in scenerio_data["users"]["bots"]:
        update_bot_ltm(config_data, scenerio_data, bot_data, message)
