import sys
import os
import json
import random

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import generate, handlebars, parse
from src.storage import storage
from src.memory import memory


QUESTION_USER_USER_ID = "C1F71C6648F9FE5D20FBF21B"  # This is a placeholder
QUESTION_USER_FIRST_NAME = "Terry"  # This is a placeholder
QUESTION_USER_FULL_NAME = "Terry Gross"  # This is a placeholder


def _format_question(question):
    return {
          "role": "user",
          "user_id": QUESTION_USER_USER_ID,
          "first_name": QUESTION_USER_FIRST_NAME,
          "full_name": QUESTION_USER_FULL_NAME,
          "message": question,
          "message_id": storage.hash_string(QUESTION_USER_USER_ID + ":" + question),
      }


def _format_answer(scenerio_data, bot_data, answer):
    return {
          "role": "assistant",
          "user_id": bot_data["id"],
          "first_name": bot_data["first_name"],
          "full_name": bot_data["full_name"],
          "message": answer,
          "message_id": storage.hash_string(bot_data["id"] + ":" + answer),
      }


def _generate_reframed_question(config_data, scenerio_data, bot_data, question):
    question_reframe_messages = handlebars.get_prompt_messages(
        config_data["question"]["question_reframe_template"],
        {
            "question": question,
            "bot": bot_data,
            **config_data["question"],
        }
    )
    reframed_question_response = generate.get_completion(
        config_data,
        question_reframe_messages,
        config_data["question"]["question_reframe_model"],
        config_data["question"]["question_reframe_temperature"]
    )
    reframed_question = parse.parse_raw_json_response(reframed_question_response)["new_question"]
    
    return _format_question(reframed_question)


def _generate_answer(config_data, scenerio_data, bot_data, question):
    memories = memory.get_memories(config_data, scenerio_data, bot_data, question)

    answer_messages = handlebars.get_prompt_messages(
        config_data["question"]['answer_template'], 
        {
            "question": question,
            "recent_messages": memories["recent_messages"],
            "relevant_messages": memories["relevant_messages"],
            "bot": bot_data,
            **config_data["question"],
        }
    )
    answer_response = generate.get_completion(
        config_data,
        answer_messages,
        config_data["question"]["answer_model"], 
        config_data["question"]["answer_temperature"]
    )
    answer = parse.parse_raw_json_response(answer_response)["message"]

    return _format_answer(scenerio_data, bot_data, answer)


def _create_event(config_data, scenerio_data, bot_data, question):
    question = _generate_reframed_question(config_data, scenerio_data, bot_data, question)
    storage.save_created_event(config_data, scenerio_data, bot_data, question)
    answer = _generate_answer(config_data, scenerio_data, bot_data, question)
    storage.save_created_event(config_data, scenerio_data, bot_data, answer)


def create_events(config_data, scenerio_data, bot_data):
    questions = config_data["question"]["questions"]
    for question in random.sample(questions, len(questions)):
        _create_event(config_data, scenerio_data, bot_data, question)
