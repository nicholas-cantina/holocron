from src.memory import memory, create, summarize
from src.chat import chat as chat_


def update_stm(config_data, scenario_data, message):
    memory.update_stm(config_data, scenario_data, message)


def update_mtm(config_data, scenario_data, message):
    memory.update_mtm(config_data, scenario_data, message)


def update_ltm(config_data, scenario_data, message):
    memory.update_ltm(config_data, scenario_data, message)


def answer_question(config_data, scenario_data, bot_data, question):
    create.answer_question(config_data, scenario_data, bot_data, question)


def reply(config_data, scenario_data, bot_data, message):
    chat_.reply(config_data, scenario_data, bot_data, message)
