import os
import sys

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import logging


@logging.request_decorator
def get_embeddings(config_data, _scenario_data, input, model, _request_type):
    response = config_data["test"]["openai_client"].embeddings.create(
        input=input,
        model=model
    )
    return response.data[0].embedding


@logging.request_decorator
def get_completion(config_data, _scenario_data, messages, model, temperature, _request_type):
    response = config_data["test"]["openai_client"].chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
    )
    return response.choices[0].message.content


def get_simple_completion(config_data, messages, model, temperature):
    response = config_data["test"]["openai_client"].chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
    )
    return response.choices[0].message.content
