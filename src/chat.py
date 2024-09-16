import sys
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import generate, handlebars
from src.memory import memory


def _generate_next_message(config_data, scenerio_data, bot_data, recent_messages, relevant_messages)
    messages = handlebars.get_prompt_messages(
        config_data["template"]["chat_template"], 
        {
            "recent_messages": recent_messages,
            "relevant_messages": relevant_messages,
            "bot": bot_data,
            **config_data["chat"]
        }
    )
    response = generate.get_completion(
        config_data,
        messages,
        config_data["chat"]["chat_model"],
        config_data["chat"]["chat_temperature"]
    )

    return response


def get_reply(config_data, scenerio_data, latest_event, bot_data):
    memories = memory.get_memories(
        config_data, 
        scenerio_data, 
        bot_data, 
        latest_event
    )

    return _generate_next_message(
        config_data, 
        scenerio_data, 
        bot_data, 
        memories["recent_messages"], 
        memories["filtered_relevant_messages"]
    )
