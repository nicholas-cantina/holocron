import sys
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.storage import storage, retrieve


def get_memories(config_data, scenerio_data, bot_data, message):
    recent_messages = retrieve.get_relevant_messages_from_message_table(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["question"]["num_recent_messages_generate_answers"],
    ) + [message]

    relevant_messages = retrieve.get_recent_messages_from_message_table(
        config_data,
        scenerio_data,
        bot_data,
        message,
        config_data["question"]["num_relevant_messages_generate_answers"],
    )
    return {
        "recent_messages": recent_messages,
        "relevant_messages": [
            message for message in relevant_messages if 
            message["message_id"] not in 
                [message["message_id"] for message in recent_messages]
        ]
    }


def _generate_conversation_stm(config_data, scenerio_data):
    # fetch current stm
    # fetch ltm
    # generate new stm
    # save new stm
    pass  # TODO: add this


def _generate_bot_stm(config_data, scenerio_data, bot_data):
    # fetch current stm
    # fetch ltm
    # generate new stm
    # save new stm
    pass  # TODO: add this


def update_bot_stm(config_data, scenerio_data, bot_data):
    new_bot_state = _generate_bot_stm(config_data, scenerio_data, bot_data)
    storage.save_bot_state(config_data, scenerio_data, bot_data, new_bot_state)


def update_stm(config_data, scenerio_data):
    new_conversation_state = _generate_conversation_stm(config_data, scenerio_data)
    storage.save_conversation_state(config_data, scenerio_data, new_conversation_state)

    for bot_data in scenerio_data["users"]["bots"]:
        update_bot_stm(config_data, scenerio_data, bot_data)


def update_bot_ltm(config_data, scenerio_data, bot_data, event):
    storage.save_message(config_data, scenerio_data, bot_data, event)


def update_ltm(config_data, scenerio_data, message):
    for bot_data in scenerio_data["users"]["bots"]:
        update_bot_ltm(config_data, scenerio_data, bot_data, message)
