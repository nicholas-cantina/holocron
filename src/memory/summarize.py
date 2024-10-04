import os
import sys
import time
import json

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.storage import retrieve, storage
from src.utils import generate, handlebars, parse
from src.memory import memory


def _get_summarize_template_data(config_data, scenerio_data, bot_data, memories):
    return {
        "memories": memories["memories"],
        "conversation_state": memories["conversation_state"],
        "recent_messages": memories["recent_messages"],
        "bot": bot_data,
        "bot_names": ", ".join([bot["full_name"] for bot in scenerio_data["users"]["bots"]]),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def _format_mtm_summary(scenerio_data, bot_data, summary):
    return summary


def _generate_mtm_events_summary(config_data, scenerio_data, bot_data, memories):
    prompt_messages = handlebars.get_prompt_messages(
        config_data["create"]["mtm_template"],
        _get_summarize_template_data(
            config_data,
            scenerio_data,
            bot_data,
            memories
        )
    )

    summary_response = generate.get_completion(
        config_data,
        prompt_messages,
        config_data["summarize"]["mtm_model"],
        config_data["summarize"]["mtm_temperature"]
    )

    summary = parse.parse_raw_json_response(
        summary_response)["new_working_memory"]

    return _format_mtm_summary(scenerio_data, bot_data, summary)


def _summarize_mtm_events(config_data, scenerio_data, bot_data, message):
    memories = memory.get_mtm_summary_memories(
        config_data,
        scenerio_data,
        bot_data,
        message
    )

    summary = _generate_mtm_events_summary(
        config_data, scenerio_data, bot_data, memories)
    storage.save_conversation_state_to_mtm(config_data, scenerio_data, bot_data, summary)


def summarize_mtm_events(config_data, scenerio_data, bot_data, message):
    _summarize_mtm_events(config_data, scenerio_data, bot_data, message)


def _format_ltm_summary(_scenerio_data, bot_data, summary):
    summary = {
        "summary": summary,
        "id": storage.hash_string(bot_data["id"] + ":" + json.dumps(summary)),
        "user_id": bot_data["id"],
    }
    return storage.format_summary(summary)


def _generate_ltm_summary(config_data, scenerio_data, bot_data, memories):
    prompt_messages = handlebars.get_prompt_messages(
        config_data["summarize"]["ltm_template"],
        _get_summarize_template_data(
            config_data,
            scenerio_data,
            bot_data,
            memories
        )
    )

    summary_response = generate.get_completion(
        config_data,
        prompt_messages,
        config_data["summarize"]["ltm_model"],
        config_data["summarize"]["ltm_temperature"]
    )

    summary = parse.parse_raw_json_response(
        summary_response)["new_long_term_memory"]

    return _format_ltm_summary(scenerio_data, bot_data, summary)


def generate_ltm_summary(config_data, scenerio_data, bot_data, message):
    memories = memory.get_ltm_summary_memories(
        config_data,
        scenerio_data,
        bot_data,
        message
    )

    return _generate_ltm_summary(config_data, scenerio_data, bot_data, memories)


def get_summarize_ltm_events(config_data, scenerio_data, bot_data, message):
    return generate_ltm_summary(config_data, scenerio_data, bot_data, message)


def summarize_ltm_events(config_data, scenerio_data, bot_data, message):
    # TODO: make this work for multiple messages
    summary = get_summarize_ltm_events(config_data, scenerio_data, bot_data, message)
    storage.save_memory_to_ltm(config_data, scenerio_data, bot_data, summary)
