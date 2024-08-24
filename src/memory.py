import sys
import os
import random
import itertools
import json

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import generate, handlebars
from src import storage


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


def _format_answer_response(conversation_data, question, answer):
    return {
          "role": "assistant",
          "user_id": conversation_data["bot"]["user_name"],
          "first_name": conversation_data["bot"]["first_name"],
          "full_name": conversation_data["bot"]["full_name"],
          "message": "In response to the question: \"" + question + "\" I answered: \"" + answer + "\"" # This is a placeholder
      }


def _generate_reframed_question(config_data, conversation_data, question):
    formatted_question = _format_question(question)
    relevant_messages = storage.get_relevant_messages_from_search_table(
        config_data,
        conversation_data,
        formatted_question,
        config_data["memory"]["num_messages_generate_answers"],
        "answer"
    )

    conversation_data["messages"] = relevant_messages + [formatted_question]
    question_reframe_messages = handlebars.get_prompt_messages(
        config_data["template"]["question_reframe_template"],
        {
            "question": question,
            **config_data["template"],
            **conversation_data
        }
    )
    reframed_question = generate.get_completion(
        config_data,
        question_reframe_messages,
        config_data["generation"]["answer_model"],
        config_data["generation"]["answer_temperature"]
    )
    return _format_question(reframed_question)


def _generate_answer(config_data, conversation_data, question):
    reframed_question = _generate_reframed_question(config_data, conversation_data, question)
    relevant_messages = storage.get_relevant_messages_from_search_table(
        config_data,
        conversation_data,
        reframed_question,
        config_data["memory"]["num_messages_generate_answers"],
        "answer"
    )
    conversation_data["messages"] = relevant_messages + [reframed_question]
    answer_messages = handlebars.get_prompt_messages(
        config_data["template"]['answer_template'], 
        {
            **config_data["template"],
            **conversation_data
        }
    )
    answer = generate.get_completion(
        config_data,
        answer_messages,
        config_data["generation"]["answer_model"], 
        config_data["generation"]["answer_temperature"]
    )

    return _format_answer_response(conversation_data, question, answer)


def ask_questions(config_data, conversation_data):
    questions = list(itertools.chain.from_iterable(list(config_data["test"]["questions"].values())))[:1] # TODO: remove [:1]

    for question in random.sample(questions, len(questions)):
      answer = _generate_answer(config_data, conversation_data, question)
      storage.save_message_to_search_table(config_data, conversation_data, answer, "answer")


def _generate_next_message(config_data, conversation_data, messages):
    conversation_data["messages"] = messages

    messages = handlebars.get_prompt_messages(config_data["template"]["chat_template"], conversation_data)
    response = generate.get_completion(
        config_data,
        messages,
        config_data["generation"]["chat_model"],
        config_data["generation"]["chat_temperature"]
    )

    return response


def get_response_to_conversation(config_data, conversation_data):
    last_messsage = conversation_data["messages"][-1]

    messages = storage.get_relevant_messages_from_search_table(
       config_data, conversation_data, last_messsage, config_data["memory"]["num_messages_generate_chat"], "chat"
    )

    return _generate_next_message(config_data, conversation_data, messages)

# Used for testing vs. with answers
def get_response_to_conversation_no_answers(config_data, conversation_data):
    messsage = conversation_data["messages"][-1]

    messages = storage.get_recent_messages_from_search_table(
       config_data, conversation_data, messsage, config_data["memory"]["num_messages_generate_chat"], "chat"
    )
    chat_messages = [message for message in messages if message["message_type"] != "answer"]

    return _generate_next_message(config_data, conversation_data, chat_messages)
