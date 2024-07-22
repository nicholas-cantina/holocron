from utils import common
from utils import handlebars
from utils import openai

CHAT_MODEL = "gpt-4o"

HOW_MANY_MESSAGES_TO_SEND = 20


def generate_test_outputs(prompt_data, memories, prompt_template):
    """
    Generate test outputs for conversations with and without memories.

    Parameters:
    - prompt_data (dict): The data for the prompt, including messages.
    - memories (list): List of memory messages to include.
    - prompt_template (str): The template for formatting the messages.

    Returns:
    - list: A list containing a dictionary with the results of conversations
            with and without memories.
    """
    # Extract messages from the prompt data
    messages = prompt_data["messages"]
    
    # Generate messages without memories
    no_memories_messages = handlebars.make_messages(prompt_template, {
        **prompt_data,
        "messages": messages[:HOW_MANY_MESSAGES_TO_SEND]
    })
    
    # Generate messages with memories
    with_memories_messages = handlebars.make_messages(prompt_template, {
        **prompt_data,
        "messages": (memories + messages)[:HOW_MANY_MESSAGES_TO_SEND]
    })
    
    # Get the results of the conversations from the OpenAI model
    no_memories_result = openai.get_completion(no_memories_messages, CHAT_MODEL)
    with_memories_result = openai.get_completion(with_memories_messages, CHAT_MODEL)
    
    # Return the results in a dictionary
    return [{
        "no_memory_conversation": no_memories_messages,
        "with_memory_conversation": with_memories_messages,
        "no_memory": no_memories_result,
        "with_memory": with_memories_result
    }]