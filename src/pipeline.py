import sys
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.memory import memory, create, summarize
from src.storage import storage
from src.chat import chat as _chat


def _format_backfill(backfill):
    backfill = {
        "role": backfill["role"],
        "user_id": backfill["user_id"],
        "first_name": backfill["first_name"],
        "full_name": backfill["full_name"],
        "message": backfill["message"],
        "id": storage.hash_string(backfill["user_id"] + ":" + backfill["message"]),
    }
    return storage.format_message(backfill)


def backfill_stm(config_data, scenerio_data):
    backfills = scenerio_data["conversation"]["events"]["messages"]
    for backfill in backfills:
        message = _format_backfill(backfill)
        memory.update_stm(config_data, scenerio_data, message)


def update_stm(config_data, scenerio_data, bot_data, message):
    message = storage.format_message(message)
    memory.update_bot_stm(config_data, scenerio_data, bot_data, message)


def update_mtm(config_data, scenerio_data, message):
    memory.update_mtm(config_data, scenerio_data, message)


def update_ltm(config_data, scenerio_data, message):
    memory.update_ltm(config_data, scenerio_data, message)


def answer_question(config_data, scenerio_data, bot_data, questions):
    create.answer_question(config_data, scenerio_data, bot_data, questions)


def chat(config_data, scenerio_data, bot_data, message):
    return _chat.get_reply(config_data, scenerio_data, bot_data, message)
