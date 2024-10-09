import configparser
import os
import json
import sys
import openai

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import common


def _get_database_config_data(config, root_dir):
    return {
        "params": {
            "dbname": config["Database"]["dbname"],
            "host": config["Database"]["host"],
            "user": config["Database"]["user"],
            "port": config["Database"]["port"]
        },
        "stm_schema": config["Database"]["stm_schema"],
        "mtm_schema": config["Database"]["mtm_schema"],
        "ltm_schema": config["Database"]["ltm_schema"],
        "logging_schema": config["Database"]["logging_schema"],
        "stm_table": config["Database"]["stm_table"],
        "mtm_table": config["Database"]["mtm_table"],
        "ltm_table": config["Database"]["ltm_table"],
        "request_logging_table": config["Database"]["request_logging_table"],
        "fetch_logging_table": config["Database"]["fetch_logging_table"],
        "delete_db_script": os.path.join(root_dir, config["Database"]["delete_db_script"]),
        "create_db_script": os.path.join(root_dir, config["Database"]["create_db_script"]),
        "sql_file": os.path.join(root_dir, config["Database"]["sql_file"])
    }


def _get_summarize_config_data(config, root_dir):
    mtm_template = common.read_file(
        os.path.join(root_dir, config["Summarize"]["mtm_template_file"]))
    ltm_template = common.read_file(
        os.path.join(root_dir, config["Summarize"]["ltm_template_file"]))
    return {
        "mtm_template": mtm_template,
        "mtm_model": config["Summarize"]["mtm_model"],
        "mtm_temperature": float(config["Summarize"]["mtm_temperature"]),
        "num_recent_messages_generate_mtm": int(config["Summarize"]["num_recent_messages_generate_mtm"]),
        "num_ltm_memories_generate_mtm": int(config["Summarize"]["num_ltm_memories_generate_mtm"]),
        "ltm_template": ltm_template,
        "ltm_model": config["Summarize"]["ltm_model"],
        "ltm_temperature": float(config["Summarize"]["ltm_temperature"]),
        "num_ltm_memories_generate_ltm": int(config["Summarize"]["num_ltm_memories_generate_ltm"]),
        "num_recent_messages_generate_ltm": int(config["Summarize"]["num_recent_messages_generate_ltm"]),
    }


def _get_questions_pipeline_config_data(config, root_dir):
    question_reframe_template = common.read_file(os.path.join(
        root_dir, config["Create"]["question_reframe_template_file"]))
    question_reframed_question_few_shot_examples = [json.dumps(example).replace("\"", "\\\"") for example in common.read_jsonl_file(
        os.path.join(root_dir, config["Create"]["question_reframed_question_few_shot_examples_file"]))]
    answer_template = common.read_file(os.path.join(root_dir, config["Create"]["answer_template_file"]))
    return {
        "question_reframe_template": question_reframe_template,
        "question_reframed_question_few_shot_examples": question_reframed_question_few_shot_examples,
        "question_reframe_model": config["Create"]["question_reframe_model"],
        "question_reframe_temperature": float(config["Create"]["question_reframe_temperature"]),
        "answer_template": answer_template,
        "answer_model": config["Create"]["answer_model"],
        "answer_temperature": float(config["Create"]["answer_temperature"]),
        "num_ltm_memories_generate_answer": int(config["Create"]["num_ltm_memories_generate_answer"]),
        "num_recent_messages_generate_answer": int(config["Create"]["num_recent_messages_generate_answer"])
    }


def _get_chat_pipeline_config_data(config, root_dir):
    chat_template = common.read_file(os.path.join(root_dir, config["Chat"]["chat_template_file"]))
    return {
        "chat_template": chat_template,
        "chat_model": config["Chat"]["chat_model"],
        "chat_temperature": float(config["Chat"]["chat_temperature"]),
        "num_ltm_memories_generate_chat": int(config["Chat"]["num_ltm_memories_generate_chat"]),
        "num_recent_messages_generate_chat": int(config["Chat"]["num_recent_messages_generate_chat"]),
    }


def _get_search_config_data(config):
    return {
        "embedding_model": config["Search"]["embedding_model"],
    }


def _get_test_data(config, root_dir):
    scenario = common.read_json_file(os.path.join(root_dir, config["Test"]["scenario_file"]))
    bot_datas = list(common.read_jsonl_file(os.path.join(root_dir, config["Test"]["bots_file"])))
    bots_data_dict = {bot["id"]: bot for bot in bot_datas}
    questions_dict = common.read_json_file(os.path.join(root_dir, config["Test"]["questions_file"]))
    questions = [question for questions in questions_dict.values() for question in questions]

    root_config = configparser.ConfigParser()
    root_config.read(os.path.join(root_dir, config["Test"]["root_config_file"]))
    openai_client = openai.OpenAI(
        api_key=root_config["OPENAI"]["OPENAI_API_KEY"]
    )
    return {
        "scenario": scenario,
        "bot_datas": bots_data_dict,
        "questions": questions,
        "openai_client": openai_client
    }


def get_config_data():
    file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.join(file_dir, "..")

    config = configparser.ConfigParser()
    config.read(os.path.join(file_dir, "test_config.ini"))

    return {
        "test": _get_test_data(config, root_dir),
        "database": _get_database_config_data(config, root_dir),
        "summarize": _get_summarize_config_data(config, root_dir),
        "search": _get_search_config_data(config),
        "create": _get_questions_pipeline_config_data(config, root_dir),
        "chat": _get_chat_pipeline_config_data(config, root_dir)
    }
