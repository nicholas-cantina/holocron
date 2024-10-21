import sys
import os
import argparse
import readline
import uuid
import atexit

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, parent_dir)

from scripts import show, test_utils


def get_user_data(bot_datas, user_id):
    if user_id is None and len(bot_datas) == 1:
        return next(iter(bot_datas.values()))
    return bot_datas.get(user_id)


def setup_readline():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, "../data/.test_history")  # TODO: fix this path to the home directory
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

    for cmd in ["add", "remove", "reply", "interview", "chat"]:
        cmd_parser = subparsers.add_parser(cmd)
        cmd_parser.add_argument("user_id")
        if cmd in ["reply"]:
          cmd_parser.add_argument("--no-memory", action="store_true")
        if cmd in ["chat"]:
          cmd_parser.add_argument("message", nargs="*")

    subparsers.add_parser("backfill")
    subparsers.add_parser("remember")
    
    try:
        return parser.parse_args(user_input.split())
    except (argparse.ArgumentError, SystemExit):
        return None


def test():
    setup_readline()

    config_data, scenario_data = test_utils.initialize()
    while True:
        user_input = input("> ")
        if user_input.strip() == "":
            continue
        args = parse_args(user_input)

        if args is None:
            print("Invalid command. Available commands are: show, add, remove, reply, interview, chat, backfill, and remember.")
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
            test_utils.backfill_scenario(config_data, scenario_data)

        elif args.command in ["add", "remove", "reply", "interview"]:
            bot_data = get_user_data(config_data["test"]["bot_datas"], args.user_id)
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
                    test_utils.make_bot_reply(config_data, scenario_data, bot_data)
                    scenario_data["test"]["memory"] = True

                elif args.command == "interview":
                    scenario_data["test"]["trace_id"] = uuid.uuid4()
                    test_utils.ask_bot_questions(config_data, scenario_data, bot_data, config_data["test"]["questions"])
            else:
                print(f"User {args.user_id} not found.")

        elif args.command in ["chat"]:
            user_data = get_user_data(config_data["test"]["user_datas"], args.user_id)
            if user_data:
                test_utils.chat_as_self(config_data, scenario_data, user_data, " ".join(args.message))
            else:
                print(f"User {args.user_id} not found.")

        elif args.command == "remember":
            scenario_data["test"]["trace_id"] = uuid.uuid4()
            test_utils.update_bots_memory(config_data, scenario_data)

        else:
            print("How'd you get here?")


if __name__ == "__main__":
    test()
