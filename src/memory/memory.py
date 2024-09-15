import sys
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.storage import storage


def _generate_conversation_stm(config_data, scenerio_data):
    # fetch current stm
    # fetch ltm
    # generate new stm
    # save new stm
    pass  # TODO: add this


def _generate_bot_stm(config_data, scenerio_data, bot_data):
    # fetch current stm
    # fetch ltm
    # generate new stm
    # save new stm
    pass  # TODO: add this


def update_stm(config_data, scenerio_data):
    new_conversation_state = _generate_conversation_stm(config_data, scenerio_data)
    storage.save_conversation_state(config_data, scenerio_data, new_conversation_state)

    for bot_data in scenerio_data["users"]["bots"]:
        new_bot_state = _generate_bot_stm(config_data, scenerio_data, bot_data)
        storage.save_bot_state(config_data, scenerio_data, bot_data, new_bot_state)


def update_bot_ltm(config_data, scenerio_data, bot_data, event):
    storage.save_message(config_data, scenerio_data, bot_data, event)


def update_ltm(config_data, scenerio_data, message):
    for bot_data in scenerio_data["users"]["bots"]:
        update_bot_ltm(config_data, scenerio_data, bot_data, message)
