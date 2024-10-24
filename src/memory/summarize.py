import time
import json

from src.storage import storage
from src.utils import generate, handlebars, parse
from src.memory import memory


def _get_summarize_template_data(config_data, scenario_data, bot_data, memories):
    return {
        "memories": memories["memories"],
        "conversation_state": memories["conversation_state"],
        "recent_messages": memories["recent_messages"],
        "bot": bot_data,
        "bot_names": ", ".join([config_data["test"]["bot_datas"][bot]["full_name"] for bot in scenario_data["users"]["bots"]]),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def _format_mtm_summary(_scenario_data, _bot_data, summary):
    return summary


def _generate_mtm_events_summary(config_data, scenario_data, bot_data, memories):
    prompt_messages = handlebars.get_prompt_messages(
        config_data["summarize"]["mtm_template"],
        _get_summarize_template_data(
            config_data,
            scenario_data,
            bot_data,
            memories
        )
    )

    summary_response = generate.get_completion_with_logs(
        config_data,
        scenario_data,
        prompt_messages,
        config_data["summarize"]["mtm_model"],
        config_data["summarize"]["mtm_temperature"],
        "summarize_mtm"
    )

    summary = parse.parse_raw_json_response(
        summary_response)["new_working_memory"]

    return _format_mtm_summary(scenario_data, bot_data, summary)


def _summarize_mtm_events(config_data, scenario_data, bot_data, message):
    memories = memory.get_mtm_summary_memories(
        config_data,
        scenario_data,
        bot_data,
        message
    )

    return _generate_mtm_events_summary(
        config_data, scenario_data, bot_data, memories)


def summarize_mtm_events(config_data, scenario_data, bot_data, message):
    return _summarize_mtm_events(config_data, scenario_data, bot_data, message)


def _format_ltm_summary(_scenario_data, bot_data, summary):
    summary = {
        "summary": summary,
        "id": storage.hash_string(bot_data["id"] + ":" + json.dumps(summary, sort_keys=True)),
        "user_id": bot_data["id"],
    }
    return storage.format_summary(summary)


def _generate_ltm_summary(config_data, scenario_data, bot_data, memories):
    prompt_messages = handlebars.get_prompt_messages(
        config_data["summarize"]["ltm_template"],
        _get_summarize_template_data(
            config_data,
            scenario_data,
            bot_data,
            memories
        )
    )

    summary_response = generate.get_completion_with_logs(
        config_data,
        scenario_data,
        prompt_messages,
        config_data["summarize"]["ltm_model"],
        config_data["summarize"]["ltm_temperature"],
        "sumarize_ltm"
    )

    summary = parse.parse_raw_json_response(
        summary_response)["new_long_term_memory"]

    return _format_ltm_summary(scenario_data, bot_data, summary)


def _summarize_ltm_events(config_data, scenario_data, bot_data, message):
    memories = memory.get_ltm_summary_memories(
        config_data,
        scenario_data,
        bot_data,
        message
    )

    return _generate_ltm_summary(config_data, scenario_data, bot_data, memories)


def get_summarize_ltm_events(config_data, scenario_data, bot_data, message):
    return _summarize_ltm_events(config_data, scenario_data, bot_data, message)


def summarize_ltm_events(config_data, scenario_data, bot_data, message):
    # TODO: make this work for multiple messages
    summary = get_summarize_ltm_events(config_data, scenario_data, bot_data, message)
    storage.save_memory_to_ltm(config_data, scenario_data, bot_data, summary)
