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


def make_bot_respond(config_data, scenario_data, bot_data):
    message = retrieve.get_latest_event(config_data, scenario_data)
    response = pipeline.chat(config_data, scenario_data, bot_data, message)
    pipeline.update_stm(config_data, scenario_data, bot_data, response)
    print(json.dumps(response))


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

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("show_command", nargs="?", choices=["bots"])
    show_parser.add_argument("show_command", nargs="?", choices=["history"])  # TODO: add this
    show_parser.add_argument("show_command", nargs="?", choices=["trace"])  # TODO: add this


    for cmd in ["add", "remove", "chat", "interview", "stm", "mtm", "ltm"]:  # TODO: add the memories
        cmd_parser = subparsers.add_parser(cmd)
        cmd_parser.add_argument("user_id")

    subparsers.add_parser("backfill")
    subparsers.add_parser("remember")

    try:
        return parser.parse_args(user_input.split())
    except (argparse.ArgumentError, SystemExit):
        return None


def test():
    config_data, scenario_data = initialize()

    setup_readline()

    while True:
        trace_id += 1
        config_data["test"]["trace_id"] = -1

        user_input = input("> ")
        if user_input.strip() == "":
            continue
        args = parse_args(user_input)

        if args is None:
            print("Invalid command. Available commands are: \"help\", \"add\", \"backfill\", \"chat\", \"interview\", \"update\".")
            continue

        if args.command == "show":
            if args.help_command == "bots":
                print(scenario_data["users"]["bots"])
            else:
                print("Invalid help command. Available help commands are: \"bots\".")

        elif args.command == "backfill":
            config_data["test"]["trace_id"] = trace_id
            backfill_scenario(config_data, scenario_data)

        elif args.command in ["add", "remove", "chat", "interview", "stm", "mtm", "ltm"]:  # TODO: implement memories
            bot_data = get_bot_data(config_data["test"]["bot_datas"], args.user_id)
            if bot_data:
                config_data["test"]["trace_id"] = trace_id
                if args.command == "add":
                    scenario_data["users"]["bots"].append(args.user_id)
                elif args.command == "remove":
                    scenario_data["users"]["bots"] = [user for user in scenario_data["users"]["bots"] if user != args.user_id]
                elif args.command == "chat":    
                    make_bot_respond(config_data, scenario_data, bot_data)
                elif args.command == "interview":
                    ask_bot_questions(config_data, scenario_data, bot_data, config_data["test"]["questions"])
            else:
                print(f"User {args.user_id} not found.")

        elif args.command == "remember":
            config_data["test"]["trace_id"] = trace_id
            update_bots_memory(config_data, scenario_data)

        else:
            print("How'd you get here?")


if __name__ == "__main__":
    test()