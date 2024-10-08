
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.memory import memory, summarize
from src.storage import storage
from src.utils import generate, handlebars, parse


QUESTION_USER_USER_ID = "C1F71C6648F9FE5D20FBF21B"  # placeholder
QUESTION_USER_FIRST_NAME = "Terry"  # placeholder
QUESTION_USER_FULL_NAME = "Terry Gross"  # placeholder


def _format_question(config_data, question):
    question = {
        "user_id": QUESTION_USER_USER_ID,
        "message": question,
        "id": storage.hash_string(QUESTION_USER_USER_ID + ":" + question),
    }
    content = {
        "message": question,
        "first_name": QUESTION_USER_FIRST_NAME,
        "full_name": QUESTION_USER_FULL_NAME,
        "user_id": QUESTION_USER_USER_ID,
    }
    return storage.format_message_with_content(config_data, question, content)


def _format_answer(config_data, _scenario_data, bot_data, answer):
    answer = {
        "user_id": bot_data["id"],
        "message": answer,
        "id": storage.hash_string(bot_data["id"] + ":" + answer),
    }
    return storage.format_message(config_data, answer)


def _get_reframe_question_template_data(config_data, _scenario_data, bot_data, question):
    return {
        "question": question,
        "bot": bot_data,
        "question_reframed_question_few_shot_examples": config_data["create"]["question_reframed_question_few_shot_examples"],
    }


def _generate_reframed_question(config_data, _scenario_data, bot_data, question):
    prompt_messages = handlebars.get_prompt_messages(
        config_data["create"]["question_reframe_template"],
        _get_reframe_question_template_data(config_data, _scenario_data, bot_data, question)
    )
    reframed_question_response = generate.get_completion(
        config_data,
        prompt_messages,
        config_data["create"]["question_reframe_model"],
        config_data["create"]["question_reframe_temperature"]
    )
    reframed_question = parse.parse_raw_json_response(
        reframed_question_response)["new_question"]

    return _format_question(config_data, reframed_question)


def _get_answer_template_data(_config_data, _scenario_data, bot_data, memories, question):
    return {
        "question": question,
        "memories": memories["memories"],
        "conversation_state": memories["conversation_state"],
        "recent_messages": memories["recent_messages"],
        "bot": bot_data,
    }


def _generate_answer(config_data, scenario_data, bot_data, question):
    memories = memory.get_answer_memories(
        config_data, scenario_data, bot_data, question)

    prompt_messages = handlebars.get_prompt_messages(
        config_data["create"]['answer_template'],
        _get_answer_template_data(config_data, scenario_data, bot_data, memories, question)
    )
    answer_response = generate.get_completion(
        config_data,
        prompt_messages,
        config_data["create"]["answer_model"],
        config_data["create"]["answer_temperature"]
    )
    answer = parse.parse_raw_json_response(answer_response)["message"]

    return _format_answer(config_data, scenario_data, bot_data, answer)


def get_answer_question(config_data, scenario_data, bot_data, question):
    question = _generate_reframed_question(
        config_data, scenario_data, bot_data, question)
    answer = _generate_answer(config_data, scenario_data, bot_data, question)

    return summarize.get_summarize_ltm_events(config_data, scenario_data, bot_data, answer)


def answer_question(config_data, scenario_data, bot_data, question):
    memory = get_answer_question(config_data, scenario_data, bot_data, question)
    storage.save_memory_to_ltm(config_data, scenario_data, bot_data, memory)
