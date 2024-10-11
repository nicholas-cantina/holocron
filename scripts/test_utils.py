import sys
import os
import uuid
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, parent_dir)

from scripts import test_config, setup
from src import pipeline
from src.storage import retrieve, storage


def initialize():
    config_data = test_config.get_config_data()
    scenario_data = config_data["test"]["scenario"]
    scenario_data["test"]["trace_id"] = uuid.uuid4()
    setup.initialize_data_stores(config_data)
    return config_data, scenario_data


def format_text_message(config_data, backfill):
    user_data = {}
    if backfill["user_id"] in config_data["test"]["user_datas"]:
        user_data = config_data["test"]["user_datas"][backfill["user_id"]]
    else:
        user_data = config_data["test"]["bot_datas"][backfill["user_id"]]
    backfill = {
        "user_id": backfill["user_id"],
        "first_name": user_data["first_name"],
        "full_name": user_data["full_name"],
        "message": backfill["message"],
        "id": storage.hash_string(backfill["user_id"] + ":" + backfill["message"]),
    }
    return storage.format_message_for_bot_data(config_data, backfill, user_data)


def backfill_scenario(config_data, scenario_data):
    backfills = scenario_data["events"]["messages"]
    for backfill in backfills:
        
        message = format_text_message(config_data, backfill)
        pipeline.update_stm(config_data, scenario_data, message)
        print(json.dumps({**message, "timestamp": message["timestamp"].isoformat()}, indent=4, sort_keys=True))


def make_bot_reply(config_data, scenario_data, bot_data):
    message = retrieve.get_latest_event(config_data, scenario_data)
    pipeline.reply(config_data, scenario_data, bot_data, message)


def update_bots_memory(config_data, scenario_data):
    message = retrieve.get_latest_event(config_data, scenario_data)
    pipeline.update_mtm(config_data, scenario_data, message)
    pipeline.update_ltm(config_data, scenario_data, message)


def ask_bot_questions(config_data, scenario_data, bot_data, questions):
    for question in questions:
        pipeline.answer_question(config_data, scenario_data, bot_data, question)


def chat_as_self(config_data, scenario_data, user_data, text):
    message = format_text_message(config_data, {"user_id": "nicholas", "message": text})
    pipeline.update_stm(config_data, scenario_data, message)
    print(json.dumps({**message, "timestamp": message["timestamp"].isoformat()}, indent=4, sort_keys=True))
