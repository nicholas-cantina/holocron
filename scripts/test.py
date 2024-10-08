import sys
import os
import argparse
import json
import readline

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, parent_dir)

from scripts import test_config, setup
from src import pipeline
from src.storage import retrieve


def initialize():
    config_data = test_config.get_config_data()
    scenario_data = config_data["test"]["scenario"]
    setup.initialize_data_stores(config_data)
    return config_data, scenario_data


def backfill_scenario(config_data, scenario_data):
    pipeline.backfill_stm(config_data, scenario_data)


def get_bot_response(config_data, scenario_data, bot_data):
    message = retrieve.get_latest_event(config_data, scenario_data)
    response = pipeline.chat(config_data, scenario_data, bot_data, message)
    pipeline.update_stm(config_data, scenario_data, bot_data, response)
    return response


def update_bots_memory(config_data, scenario_data):
    message = retrieve.get_latest_event(config_data, scenario_data)
    pipeline.update_mtm(config_data, scenario_data, message)
    pipeline.update_ltm(config_data, scenario_data, message)


def ask_bot_questions(config_data, scenario_data, bot_data, questions):
    for question in questions:
        pipeline.answer_question(config_data, scenario_data, bot_data, question)


def get_bot_data(bot_datas, user_id):
    if user_id is None and len(bot_datas) == 1:
        return next(iter(bot_datas.values()))
    return bot_datas.get(user_id)


def setup_readline():
    import atexit
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    histfile = os.path.join(script_dir, ".test_history")
    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    atexit.register(readline.write_history_file, histfile)


class SilentArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(None, message)


def parse_args(user_input):
    parser = SilentArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    help_parser = subparsers.add_parser("help")
    help_parser.add_argument("help_command", nargs="?", choices=["bots"])

    subparsers.add_parser("backfill")
    subparsers.add_parser("update")

    for cmd in ["add", "chat", "interview"]:
        cmd_parser = subparsers.add_parser(cmd)
        cmd_parser.add_argument("user_id", help="The user_id for the bot you'd like to test")

    try:
        return parser.parse_args(user_input.split())
    except (argparse.ArgumentError, SystemExit):
        return None


def test():
    config_data, scenario_data = initialize()

    setup_readline()

    while True:
        user_input = input("> ")
        if user_input.strip() == "":
            continue
        args = parse_args(user_input)

        if args is None:
            print("Invalid command. Available commands are: \"help\", \"add\", \"backfill\", \"chat\", \"interview\", \"update\".")
            continue

        if args.command == "help":
            if args.help_command == "bots":
                print(scenario_data["users"]["bots"])
            else:
                print("Invalid help command. Available help commands are: \"bots\".")

        elif args.command == "add":
            if args.user_id in config_data["test"]["bot_datas"]:
                if args.user_id not in scenario_data["users"]["bots"]:
                    scenario_data["users"]["bots"].append(args.user_id)
                else:
                    print(f"User {args.user_id} is already in the room.")
            else:
                print(f"User {args.user_id} not found in bot_datas.")
                

        elif args.command == "backfill":
            backfill_scenario(config_data, scenario_data)

        elif args.command in ["chat", "interview"]:
            bot_data = get_bot_data(config_data["test"]["bot_datas"], args.user_id)
            if bot_data:
                if args.command == "chat":
                    response = get_bot_response(config_data, scenario_data, bot_data)
                    print(json.dumps(response))
                else:
                    ask_bot_questions(config_data, scenario_data, bot_data, config_data["test"]["questions"])
            else:
                print(f"User {args.user_id} not found.")

        elif args.command == "update":
            update_bots_memory(config_data, scenario_data)

        else:
            print("How'd you get here?")


if __name__ == "__main__":
    test()