import sys
import os

from src.utils import parse

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import generate, handlebars
from src.memory import memory
from src.storage import storage


def _format_reply(_scenerio_data, bot_data, reply):
    return {
        "role": "assistant",
        "user_id": bot_data["id"],
        "first_name": bot_data["first_name"],
        "full_name": bot_data["full_name"],
        "message": reply,
        "id": storage.hash_string(bot_data["id"] + ":" + reply),
    }


def _generate_next_message(config_data, scenerio_data, bot_data, memories, conversation_state, recent_messages):
    messages = handlebars.get_prompt_messages(
        config_data["chat"]["chat_template"], 
        {
            "memories": memories,
            "conversation_state": conversation_state,
            "recent_messages": recent_messages,
            "bot": bot_data
        }
    )
    response = generate.get_completion(
        config_data,
        messages,
        config_data["chat"]["chat_model"],
        config_data["chat"]["chat_temperature"]
    )

    reply = parse.parse_raw_json_response(response)["message"]

    return _format_reply(scenerio_data, bot_data, reply)


def get_reply(config_data, scenerio_data, bot_data, latest_event):
    memories = memory.get_chat_memories(
        config_data, 
        scenerio_data, 
        bot_data, 
        latest_event
    )
    return _generate_next_message(
        config_data, 
        scenerio_data, 
        bot_data, 
        memories["memories"],
        memories["conversation_state"],
        memories["recent_messages"]
    )


def reply(config_data, scenerio_data, bot_data, latest_event):
    reply = get_reply(
        config_data, 
        scenerio_data, 
        bot_data,
        latest_event
    )
    storage.save_message_to_stm(config_data, scenerio_data, bot_data, reply)
