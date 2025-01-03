import json

from src.utils import generate, handlebars, parse
from src.memory import memory
from src.storage import storage


def _format_reply(config_data, _scenario_data, bot_data, reply):
    reply = {
        "user_id": bot_data["id"],
        "message": reply,
        "id": storage.hash_string(bot_data["id"] + ":" + reply),
    }
    return storage.format_message(config_data, reply)


def _generate_next_message(config_data, scenario_data, bot_data, memories, conversation_state, recent_messages):
    messages = handlebars.get_prompt_messages(
        config_data["chat"]["chat_template"],
        {
            "memories": memories,
            "conversation_state": conversation_state,
            "recent_messages": recent_messages,
            "bot": bot_data
        }
    )
    response = generate.get_completion_with_logs(
        config_data,
        scenario_data,
        messages,
        config_data["chat"]["chat_model"],
        config_data["chat"]["chat_temperature"],
        "chat"
    )

    reply = parse.parse_raw_json_response(response)["message"]

    return _format_reply(config_data, scenario_data, bot_data, reply)


def get_reply(config_data, scenario_data, bot_data, latest_event):
    memories = memory.get_chat_memories(
        config_data,
        scenario_data,
        bot_data,
        latest_event
    )
    return _generate_next_message(
        config_data,
        scenario_data,
        bot_data,
        memories["memories"],
        memories["conversation_state"],
        memories["recent_messages"]
    )


def reply(config_data, scenario_data, bot_data, latest_event):
    reply = get_reply(
        config_data,
        scenario_data,
        bot_data,
        latest_event
    )
    memory.update_stm(config_data, scenario_data, reply)
    print(json.dumps({**reply, "timestamp": reply["timestamp"].isoformat()}, indent=4, sort_keys=True))
