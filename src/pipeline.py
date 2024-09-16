import sys
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.memory import memory, create, consolidate
from src.storage import retrieve
from src import intent, chat


def initialize_stm_pipeline(config_data, scenerio_data):
    conversation_data = scenerio_data["conversation"]
    memory.update_conversation_stm(config_data, scenerio_data, conversation_data)

    for bot in scenerio_data["bots"]:
        bot_state = bot["state"]
        memory.update_bot_stm(config_data, scenerio_data, bot_state)


def initialize_ltm_pipeline(config_data, scenerio_data):
    messages = scenerio_data["conversation"]["events"]["messages"]
    for message in messages:
        memory.update_ltm(config_data, scenerio_data, message)


def _run_bot_memory_creation_pipeline(config_data, scenerio_data, bot_data):
    event = create.create_events(config_data, scenerio_data, bot_data)
    memory.update_bot_ltm(config_data, scenerio_data, bot_data, event)


def run_memory_creation_pipeline(config_data, scenerio_data):
    bots_data = scenerio_data["users"]["bots"]
    for bot_data in bots_data:
        _run_bot_memory_creation_pipeline(config_data, scenerio_data, bot_data)


def _run_bot_memory_consolidation_pipeline(config_data, scenerio_data, bot_data):
    takeaway = consolidate.consolidate_takeaways(config_data, scenerio_data, bot_data)
    memory.update_bot_ltm(config_data, scenerio_data, bot_data, takeaway)


def run_memory_consolidation_pipeline(config_data, scenerio_data):
    bots_data = scenerio_data["users"]["bots"]
    for bot_data in bots_data:
        _run_bot_memory_consolidation_pipeline(config_data, scenerio_data, bot_data)


def run_chat_pipeline(config_data, scenerio_data):
    latest_event = retrieve.get_latest_event(config_data)
    user_intent = intent.get_intent(config_data, scenerio_data, latest_event)
    reply = chat.get_reply(config_data, scenerio_data, latest_event, user_intent["bot_data"])

    memory.update_bot_ltm(config_data, scenerio_data, user_intent["bot_data"], reply)
    # memory.update_bot_stm(config_data, scenerio_data, user_intent["bot_data"], reply)

    return reply
