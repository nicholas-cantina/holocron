import sys
import os
import argparse
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from scripts import test_config, setup as setup_
from src import pipeline
from src.storage import retrieve


def setup():
    config_data = test_config.get_config_data()
    scenerio_data = config_data["test"]["scenerio"]

    setup_.initialize_data_stores(config_data)

    return config_data, scenerio_data


def parse_args(user_input):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    help_parser = subparsers.add_parser("help")
    help_subparsers = help_parser.add_subparsers(dest="help_command")
    _ = help_subparsers.add_parser("bots")

    _ = subparsers.add_parser("backfill")

    add_parser_ = subparsers.add_parser("add")
    add_parser_.add_argument("user_id", type=str, help="The user_id for the bot you'd like to test")

    _ = subparsers.add_parser("update")

    chat_parser = subparsers.add_parser("chat")
    chat_parser.add_argument("user_id", type=str, help="The user_id for the bot you'd like to test")

    interview_parser = subparsers.add_parser("interview")
    interview_parser.add_argument("user_id", type=str, help="The user_id for the bot you'd like to test")

    args = parser.parse_args(user_input.split())
    return args


def backfill_scenerio(config_data, scenerio_data):
    pipeline.backfill_stm(config_data, scenerio_data)


def get_bot_response(config_data, scenerio_data, bot_data):
    message = retrieve.get_latest_event(config_data, scenerio_data)
    response = pipeline.chat(config_data, scenerio_data, bot_data, message)
    pipeline.update_stm(config_data, scenerio_data, bot_data, response)
    return response


def update_bots_memory(config_data, scenerio_data):
    message = retrieve.get_latest_event(config_data, scenerio_data)
    pipeline.update_mtm(config_data, scenerio_data, message)
    pipeline.update_ltm(config_data, scenerio_data, message)


def ask_bot_questions(config_data, scenerio_data, bot_data, questions):
    for question in questions:
        pipeline.answer_question(config_data, scenerio_data, bot_data, question)


def get_bot_data_for_user_id(bot_datas, user_id):
    if user_id is None and len(bot_datas) == 1:
        return next(iter(bot_datas))
    elif user_id in bot_datas:
        return bot_datas[user_id]
    else:
        return None


def test():
    config_data, scenerio_data = setup()

    while True:
        user_input = input("> ")

        args = parse_args(user_input)

        if args.command == "help":
            if args.help_command == "bots":
                print(scenerio_data["users"]["bots"])
            else:
                print("Invalid help command. Available help commands are: \"bots\".")

        elif args.command == "add":
            if args.user_id in config_data["test"]["bot_datas"] and args.user_id not in scenerio_data["users"]["bots"]:
                scenerio_data["users"]["bots"].append(args.user_id)

        elif args.command == "backfill":
            backfill_scenerio(config_data, scenerio_data)  # TODO: return something

        elif args.command == "chat":
            bot_data = get_bot_data_for_user_id(config_data["test"]["bot_datas"], args.user_id)
            if bot_data is not None:
                response = get_bot_response(config_data, scenerio_data, bot_data)
                print(json.dumps(response))
            else:
                print(f"User {args.user_id} not found.")

        elif args.command == "interview":
            bot_data = get_bot_data_for_user_id(config_data["test"]["bot_datas"], args.user_id)
            if bot_data is not None:
                ask_bot_questions(config_data, scenerio_data, bot_data, config_data["test"]["questions"])
                # TODO: fetch the history (need start building those helper functions)
            else:
                print(f"User {args.user_id} not found.")

        elif args.command == "remember":
            update_bots_memory(config_data)  # TODO: return something

        else:
            print("Invalid command. Available commands are: \"help\", \"add\", \"backfill\", \"chat\", \"interview\", \"remember\".")


if __name__ == "__main__":
    test()
