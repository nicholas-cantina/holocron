import sys
import os
import argparse
import json
import readline
import uuid

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, parent_dir)

from scripts import test_config, setup, show
from src import pipeline
from src.storage import retrieve


def initialize():
    config_data = test_config.get_config_data()
    scenario_data = config_data["test"]["scenario"]
    setup.initialize_data_stores(config_data)
    return config_data, scenario_data


def backfill_scenario(config_data, scenario_data):
    backfills = scenario_data["events"]["messages"]
    for backfill in backfills:
        message = pipeline.format_text_message(config_data, backfill)
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


def chat_as_self(config_data, scenario_data, text):
    message = pipeline.format_text_message(config_data, {"user_id": "sean", "message": text})
    pipeline.update_stm(config_data, scenario_data, message)
    print(json.dumps({**message, "timestamp": message["timestamp"].isoformat()}, indent=4, sort_keys=True))


def get_bot_data(bot_datas, user_id):
    if user_id is None and len(bot_datas) == 1:
        return next(iter(bot_datas.values()))
    return bot_datas.get(user_id)


def setup_readline():
    import atexit
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, ".test_history")
    try:
        readline.read_history_file(history_file)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    atexit.register(readline.write_history_file, history_file)


class SilentArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(None, message)


def parse_args(user_input):
    parser = SilentArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("show_command", nargs="?", choices=["bots", "history", "trace"])

    for cmd in ["add", "remove", "reply", "interview"]:  # TODO: add the memories
        cmd_parser = subparsers.add_parser(cmd)
        cmd_parser.add_argument("user_id")
        for cmd in ["reply"]:
          cmd_parser.add_argument("--no-memory", action="store_true")

    subparsers.add_parser("backfill")
    subparsers.add_parser("remember")

    chat_parser = subparsers.add_parser("chat")
    chat_parser.add_argument("message", nargs="*")

    try:
        return parser.parse_args(user_input.split())
    except (argparse.ArgumentError, SystemExit):
        return None


def test():
    setup_readline()

    config_data, scenario_data = initialize()
    while True:
        user_input = input("> ")
        if user_input.strip() == "":
            continue
        args = parse_args(user_input)

        if args is None:
            print("Invalid command. Available commands are: \"help\", \"add\", \"backfill\", \"reply\", \"interview\", \"update\".")
            continue

        elif args.command == "show":
            if args.show_command == "bots":
                print(scenario_data["users"]["bots"])
            elif args.show_command == "history":
                show.show_scenerio_messages_helper(config_data, scenario_data)
            elif args.show_command == "trace":
                show.show_trace_requests_helper(config_data, scenario_data)
            else:
                print("Invalid help command. Available help commands are: \"bots\".")

        elif args.command == "backfill":
            backfill_scenario(config_data, scenario_data)

        elif args.command == "chat":
            text = " ".join(args.message)
            chat_as_self(config_data, scenario_data, text)

        elif args.command in ["add", "remove", "reply", "interview", "stm", "mtm", "ltm"]:
            bot_data = get_bot_data(config_data["test"]["bot_datas"], args.user_id)
            if bot_data:
                if args.command == "add":
                    if args.user_id not in scenario_data["users"]["bots"] and args.user_id in config_data["test"]["bot_datas"]:
                        scenario_data["users"]["bots"].append(args.user_id)
                elif args.command == "remove":
                    if args.user_id in scenario_data["users"]["bots"]:
                        scenario_data["users"]["bots"] = [
                            user for user in scenario_data["users"]["bots"] if user != args.user_id]
                elif args.command == "reply":
                    scenario_data["test"]["trace_id"] = uuid.uuid4()
                    if args.no_memory:
                        scenario_data["test"]["memory"] = False
                    make_bot_reply(config_data, scenario_data, bot_data)
                    scenario_data["test"]["memory"] = True
                elif args.command == "interview":
                    scenario_data["test"]["trace_id"] = uuid.uuid4()
                    ask_bot_questions(config_data, scenario_data, bot_data, config_data["test"]["questions"])
            else:
                print(f"User {args.user_id} not found.")

        elif args.command == "remember":
            scenario_data["test"]["trace_id"] = uuid.uuid4()
            update_bots_memory(config_data, scenario_data)

        else:
            print("How'd you get here?")


if __name__ == "__main__":
    test()
