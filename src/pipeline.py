import sys
import os
import json

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.memory import memory, create, summarize
from src.storage import storage
from src.chat import chat as _chat


def format_text_message(config_data, backfill):
    bot_data = config_data["test"]["bot_datas"][backfill["user_id"]]
    backfill = {
        "user_id": backfill["user_id"],
        "first_name": bot_data["first_name"],
        "full_name": bot_data["full_name"],
        "message": backfill["message"],
        "id": storage.hash_string(backfill["user_id"] + ":" + backfill["message"]),
    }
    return storage.format_message(config_data, backfill)


def update_stm(config_data, scenario_data, message):
    memory.update_stm(config_data, scenario_data, message)


def update_mtm(config_data, scenario_data, message):
    memory.update_mtm(config_data, scenario_data, message)


def update_ltm(config_data, scenario_data, message):
    memory.update_ltm(config_data, scenario_data, message)


def answer_question(config_data, scenario_data, bot_data, questions):
    create.answer_question(config_data, scenario_data, bot_data, questions)


def reply(config_data, scenario_data, bot_data, message):
    _chat.reply(config_data, scenario_data, bot_data, message)
