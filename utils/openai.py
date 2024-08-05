import os
import configparser
import sys

from openai import OpenAI

# Set parent directory and add to sys.path
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils import timing


# Load the configuration from a file
_CONFIG = configparser.ConfigParser()
_CONFIG.read('../config.ini')  # Relative path to the configuration file

# Initialize the OpenAI client with an API key from the configuration
CLIENT = OpenAI(
    api_key=_CONFIG['OPENAI']['OPENAI_API_KEY']
)


@timing.timing_decorator
def get_embeddings(input, model):
    response = CLIENT.embeddings.create(
        input=input,
        model=model
    )
    return response.data[0].embedding


@timing.timing_decorator
def get_completion(messages, model, temperature):
    response = CLIENT.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature
    )
    return response.choices[0].message.content
