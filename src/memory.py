import sys
import os
import random
import itertools

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
  sys.path.insert(0, parent_dir)

from utils import handlebars
from utils import openai


memory_model = "gpt-4o"

memory_user_user_id = "Interviewer"
memory_user_first_name = "Interviewer"
memory_user_full_name = "Interviewer"

how_many_questions = 1


def generate_memories(prompt_data, questions, prompt_template):
  memories = []
  questions = list(itertools.chain.from_iterable(list(questions.values())))[:how_many_questions]
  for question in random.sample(questions, len(questions)):
    question_message = {
      "role": "user",
      "user_id": memory_user_user_id,
      "first_name": memory_user_first_name,
      "full_name": memory_user_full_name,
      "message": question
    }
    prompt_data_for_memories = prompt_data.copy()
    prompt_data_for_memories["messages"] = prompt_data_for_memories["messages"][:2] + memories + [question_message]

    messages = handlebars.make_messages(prompt_template, prompt_data_for_memories)
    memory = openai.get_completion(messages, memory_model)

    memory_message = {
      "role": "assistant",
      "user_id": prompt_data["bot"]["user_name"],
      "first_name": prompt_data["bot"]["first_name"],
      "full_name": prompt_data["bot"]["full_name"],
      "message": memory,
    }
    memories += [question_message]
    memories += [memory_message]
  
  return memories
