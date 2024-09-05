import sys
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import generate, handlebars
from src.storage import storage


def _generate_next_message(config_data, scenerio_data, messages):
    scenerio_data["messages"] = messages

    messages = handlebars.get_prompt_messages(config_data["template"]["chat_template"], scenerio_data)
    response = generate.get_completion(
        config_data,
        messages,
        config_data["generation"]["chat_model"],
        config_data["generation"]["chat_temperature"]
    )

    return response


def get_response_to_conversation(config_data, scenerio_data):
    last_messsage = scenerio_data["messages"][-1]

    messages = storage.get_relevant_messages_from_message_table(
       config_data, scenerio_data, last_messsage, config_data["memory"]["num_messages_generate_chat"], "chat"
    )

    return _generate_next_message(config_data, scenerio_data, messages)


def get_response_to_conversation_no_memories(config_data, scenerio_data):
    messsage = scenerio_data["messages"][-1]

    messages = storage.get_recent_messages_from_message_table(
       config_data, scenerio_data, messsage, config_data["memory"]["num_messages_generate_chat"], "chat"
    )
    messages = [message for message in messages if message["message_type"] != "chat"]

    return _generate_next_message(config_data, scenerio_data, messages)
