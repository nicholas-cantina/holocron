import sys
import os
import random

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import generate, handlebars
from src.storage import storage


QUESTION_USER_USER_ID = "Interviewer"  # This is a placeholder
QUESTION_USER_FIRST_NAME = "Interviewer"  # This is a placeholder
QUESTION_USER_FULL_NAME = "Interviewer"  # This is a placeholder


def _format_question(question):
    return {
          "role": "user",
          "user_id": QUESTION_USER_USER_ID,
          "first_name": QUESTION_USER_FIRST_NAME,
          "full_name": QUESTION_USER_FULL_NAME,
          "message": question
      }


def _format_answer(scenerio_data, question, answer):
    return {
          "role": "assistant",
          "user_id": scenerio_data["bot"]["user_name"],
          "first_name": scenerio_data["bot"]["first_name"],
          "full_name": scenerio_data["bot"]["full_name"],
          "message": "In response to the question: \"" + question + "\" I answered: \"" + answer + "\""
      }


def _generate_reframed_question(config_data, scenerio_data, question):
    scenerio_data["messages"] = [_format_question(question)]
    question_reframe_messages = handlebars.get_prompt_messages(
        config_data["template"]["question_reframe_template"],
        {
            "question": question,
            **config_data["template"],
            **scenerio_data
        }
    )
    reframed_question = generate.get_completion(
        config_data,
        question_reframe_messages,
        config_data["generation"]["answer_model"],
        config_data["generation"]["answer_temperature"]
    )
    return _format_question(reframed_question)


def _generate_answer(config_data, scenerio_data, question):
    reframed_question = _generate_reframed_question(config_data, scenerio_data, question)
    relevant_messages = storage.get_relevant_messages_from_message_table(
        config_data,
        scenerio_data,
        reframed_question,
        config_data["memory"]["num_messages_generate_answers"],
        "answer"
    )
    scenerio_data["messages"] = relevant_messages + [reframed_question]
    answer_messages = handlebars.get_prompt_messages(
        config_data["template"]['answer_template'], 
        {
            **config_data["template"],
            **scenerio_data
        }
    )
    answer = generate.get_completion(
        config_data,
        answer_messages,
        config_data["generation"]["answer_model"], 
        config_data["generation"]["answer_temperature"]
    )

    return _format_answer(scenerio_data, question, answer)


def _create_event(config_data, scenerio_data, bot_data, question):
    answer = _generate_answer(config_data, scenerio_data, question)
    storage.save_created_event(config_data, scenerio_data, answer)


def create_events(config_data, scenerio_data, bot_data):
    # TODO: (LT) add more ways to create events
    questions = config_data["test"]["questions"]
    for question in random.sample(questions, len(questions)):
        _create_event(config_data, scenerio_data, bot_data, question)
