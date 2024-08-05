import sys
import os
import random
import itertools

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
  sys.path.insert(0, parent_dir)

from src.utils import generate, handlebars, extract
from src import storage


MEMORY_USER_USER_ID = "Interviewer"  # This is a placeholder
MEMORY_USER_FIRST_NAME = "Interviewer"  # This is a placeholder
MEMORY_USER_FULL_NAME = "Interviewer"  # This is a placeholder


def _format_answer(conversation_data, question, response):
    return {
          "role": "assistant",  # Maybe switch this
          "user_id": conversation_data["bot"]["user_name"],
          "first_name": conversation_data["bot"]["first_name"],
          "full_name": conversation_data["bot"]["full_name"],
          "message": "In response to the question: " + \
              question + "I would answer: " + response  # This is a placeholder
      }


def _format_question(question):
    return {
          "role": "user",
          "user_id": MEMORY_USER_USER_ID,
          "first_name": MEMORY_USER_FIRST_NAME,
          "full_name": MEMORY_USER_FULL_NAME,
          "message": question
      }


def _generate_answer(config_data, conversation_data, question):
    formatted_question = _format_question(question)

    relevant_messages = storage.get_relevant_messages_from_search_table(
        config_data, 
        conversation_data, 
        formatted_question,
        config_data["memory"]["num_messages_generate_answers"],
        "answer"
    )

    conversation_data["messages"] = relevant_messages + [formatted_question]

    messages = handlebars.get_prompt_messages(config_data["template"]["memory_prompt_template"], conversation_data)
    response = generate.get_completion(
        config_data,
        messages, 
        config_data["generation"]["memory_model"], 
        config_data["generation"]["memory_temperature"]
    )
    
    return _format_answer(conversation_data, question, response)


def ask_questions(config_data, conversation_data):
    questions = list(itertools.chain.from_iterable(list(config_data["test"]["questions"].values())))

    for question in random.sample(questions[:1], len(questions[:1])):
      answer = _generate_answer(config_data, conversation_data, question)
      storage.save_message_to_search_table(config_data, conversation_data, answer, "answer")


def _generate_next_message(config_data, conversation_data, messages):
    conversation_data["messages"] = messages

    messages = handlebars.get_prompt_messages(config_data["template"]["chat_prompt_template"], conversation_data)
    response = generate.get_completion(
        config_data,
        messages,
        config_data["generation"]["chat_model"],
        config_data["generation"]["chat_temperature"]
    )

    return response


def get_response_to_conversation(config_data, conversation_data):
    messsage = conversation_data["messages"][-1]

    messages = storage.get_relevant_messages_from_search_table(
       config_data, conversation_data, messsage, config_data["memory"]["num_messages_generate_chat"], "chat"
    )

    return _generate_next_message(config_data, conversation_data, messages)


def get_response_to_conversation_no_answers(config_data, conversation_data):
    messsage = conversation_data["messages"][-1]

    messages = storage.get_recent_messages_from_search_table(
       config_data, conversation_data, messsage, config_data["memory"]["num_messages_generate_chat"], "chat"
    )
    chat_messages = [message for message in messages if message["message_type"] != "answer"]

    return _generate_next_message(config_data, conversation_data, chat_messages)
