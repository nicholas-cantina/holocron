import os
import configparser

from openai import OpenAI

# Load the configuration from a file
CONFIG = configparser.ConfigParser()
CONFIG.read('../config.ini')  # Relative path to the configuration file

# Initialize the OpenAI client with an API key from the configuration
CLIENT = OpenAI(
    api_key=CONFIG['OPENAI']['OPENAI_API_KEY']
)

# Default temperature for AI completions to control randomness
DEFAULT_TEMPERATURE = 0.25


def get_completion(messages, model, temperature=DEFAULT_TEMPERATURE):
    """
    Retrieves a completion for a given set of messages using the specified model and temperature.

    Parameters:
    - messages (list of dict): List of message dictionaries to be processed.
    - model (str): Model identifier to use for generating completions.
    - temperature (float): Controls the randomness of the completion, default is 0.25.

    Returns:
    - str: The content of the first message from the completion response.
    """
    response = CLIENT.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature
    )
    return response.choices[0].message.content