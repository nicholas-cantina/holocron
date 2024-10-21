import os
import configparser
import json

from src.utils import common


def _get_database_config_data(config, root_dir):
    return {
        **config["database"],
        "params": {
            "dbname": config["database"]["dbname"],
            "host": config["database"]["host"],
            "user": config["database"]["user"],
            "port": config["database"]["port"]
        },
        "stm_schema": config["database"]["stm_schema"],
        "mtm_schema": config["database"]["mtm_schema"],
        "ltm_schema": config["database"]["ltm_schema"],
        "logging_schema": config["database"]["logging_schema"],
        "stm_table": config["database"]["stm_table"],
        "mtm_table": config["database"]["mtm_table"],
        "ltm_table": config["database"]["ltm_table"],
        "request_logging_table": config["database"]["request_logging_table"],
        "fetch_logging_table": config["database"]["fetch_logging_table"],
        "delete_db_script": os.path.join(root_dir, config["database"]["delete_db_script"]),
        "create_db_script": os.path.join(root_dir, config["database"]["create_db_script"]),
        "sql_file": os.path.join(root_dir, config["database"]["sql_file"])
    }


def _get_summarize_config_data(config, root_dir):
    mtm_template = common.read_file(
        os.path.join(root_dir, config["summarize"]["mtm_template_file"]))
    ltm_template = common.read_file(
        os.path.join(root_dir, config["summarize"]["ltm_template_file"]))
    return {
        **config["summarize"],
        "mtm_template": mtm_template,
        "mtm_model": config["summarize"]["mtm_model"],
        "mtm_temperature": float(config["summarize"]["mtm_temperature"]),
        "num_recent_messages_generate_mtm": int(config["summarize"]["num_recent_messages_generate_mtm"]),
        "num_ltm_memories_generate_mtm": int(config["summarize"]["num_ltm_memories_generate_mtm"]),
        "ltm_template": ltm_template,
        "ltm_model": config["summarize"]["ltm_model"],
        "ltm_temperature": float(config["summarize"]["ltm_temperature"]),
        "num_ltm_memories_generate_ltm": int(config["summarize"]["num_ltm_memories_generate_ltm"]),
        "num_recent_messages_generate_ltm": int(config["summarize"]["num_recent_messages_generate_ltm"]),
    }


def _get_questions_pipeline_config_data(config, root_dir):
    question_reframe_template = common.read_file(os.path.join(
        root_dir, config["create"]["question_reframe_template_file"]))
    question_reframed_question_few_shot_examples = [json.dumps(example).replace("\"", "\\\"") for example in common.read_jsonl_file(
        os.path.join(root_dir, config["create"]["question_reframed_question_few_shot_examples_file"]))]
    answer_template = common.read_file(os.path.join(root_dir, config["create"]["answer_template_file"]))
    return {
        **config["create"],
        "question_reframe_template": question_reframe_template,
        "question_reframed_question_few_shot_examples": question_reframed_question_few_shot_examples,
        "question_reframe_model": config["create"]["question_reframe_model"],
        "question_reframe_temperature": float(config["create"]["question_reframe_temperature"]),
        "answer_template": answer_template,
        "answer_model": config["create"]["answer_model"],
        "answer_temperature": float(config["create"]["answer_temperature"]),
        "num_ltm_memories_generate_answer": int(config["create"]["num_ltm_memories_generate_answer"]),
        "num_recent_messages_generate_answer": int(config["create"]["num_recent_messages_generate_answer"])
    }


def _get_chat_pipeline_config_data(config, root_dir):
    chat_template = common.read_file(os.path.join(root_dir, config["chat"]["chat_template_file"]))
    return {
        **config["chat"], 
        "chat_template": chat_template,
        "chat_model": config["chat"]["chat_model"],
        "chat_temperature": float(config["chat"]["chat_temperature"]),
        "num_ltm_memories_generate_chat": int(config["chat"]["num_ltm_memories_generate_chat"]),
        "num_recent_messages_generate_chat": int(config["chat"]["num_recent_messages_generate_chat"]),
    }


def _get_search_config_data(config):
  return config["search"]


def _get_test_data(config, root_dir):
    scenario = common.read_json_file(os.path.join(root_dir, config["test"]["scenario_file"]))
    bot_datas = list(common.read_jsonl_file(os.path.join(root_dir, config["test"]["bots_file"])))
    bots_data_dict = {bot["id"]: bot for bot in bot_datas}
    user_datas = list(common.read_jsonl_file(os.path.join(root_dir, config["test"]["users_file"])))
    users_data_dict = {bot["id"]: bot for bot in user_datas}
    questions_dict = common.read_json_file(os.path.join(root_dir, config["test"]["questions_file"]))
    questions = [question for questions in questions_dict.values() for question in questions]

    root_config = configparser.ConfigParser()
    root_config.read(os.path.join(root_dir, config["common"]["root_config_file"]))
    return {
        **config["test"],
        "scenario": scenario,
        "bot_datas": bots_data_dict,
        "user_datas": users_data_dict,
        "questions": questions
    }


def get_config_data():
    file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.join(file_dir, "..", "..")

    config = configparser.ConfigParser()
    config.read(os.path.join(file_dir, "config.ini"))

    return {
        "test": _get_test_data(config, root_dir),
        "database": _get_database_config_data(config, root_dir),
        "summarize": _get_summarize_config_data(config, root_dir),
        "search": _get_search_config_data(config),
        "create": _get_questions_pipeline_config_data(config, root_dir),
        "chat": _get_chat_pipeline_config_data(config, root_dir),
    }
