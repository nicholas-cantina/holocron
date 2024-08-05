import os
import sys

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import timing


@timing.timing_decorator
def get_embeddings(config_data, input, model):
    response = config_data["generation"]["openai_client"].embeddings.create(
        input=input,
        model=model
    )
    return response.data[0].embedding


@timing.timing_decorator
def get_completion(config_data, messages, model, temperature):
    response = config_data["generation"]["openai_client"].chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature
    )
    return response.choices[0].message.content
