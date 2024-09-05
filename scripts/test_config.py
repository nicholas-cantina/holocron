import configparser
import itertools
import os
import sys
import openai

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import common


def _get_questions_pipeline_config_data(config, root_dir):
    questions_dict = common.read_json_file(os.path.join(root_dir, config["Questions"]["questions_file"]))
    questions = list(itertools.chain.from_iterable(questions_dict))
    question_reframe_template = common.read_file(
        os.path.join(root_dir, config["Questions"]["question_reframe_template_file"])
    )
    question_answer_few_shot_examples = common.read_jsonl_file(
        os.path.join(root_dir, config["Questions"]["question_answer_few_shot_examples_file"])
    )
    question_reframed_question_few_shot_examples = common.read_jsonl_file(
        os.path.join(root_dir, config["Questions"]["question_reframed_question_few_shot_examples_file"])
    )
    question_output_schema = common.read_json_file(
        os.path.join(root_dir, config["Questions"]["question_output_schema_file"])
    )
    answer_template = common.read_file(
        os.path.join(root_dir, config["Questions"]["answer_template_file"])    
    )
    return {
        "questions": questions,
        "question_reframe_template": question_reframe_template,
        "question_reframed_question_few_shot_examples": question_reframed_question_few_shot_examples,
        "question_output_schema": question_output_schema,
        "question_reframe_model": config["Questions"]["question_reframe_model"],
        "question_reframe_temperature": float(config["Questions"]["question_reframe_temperature"]),
        "answer_template": answer_template,
        "answer_few_shot_examples": question_answer_few_shot_examples,
        "answer_model": config["Questions"]["answer_model"],
        "answer_temperature": float(config["Questions"]["answer_temperature"]),
        "num_messages_generate_answers": int(config["Questions"]["num_messages_generate_answers"])
    }


def _get_actions_pipeline_config_data(config, root_dir):
    actions_template = common.read_file(
        os.path.join(root_dir, config["Actions"]["actions_template_file"]))
    actions_few_shot_examples = common.read_jsonl_file(
        os.path.join(root_dir, config["Actions"]["actions_few_shot_examples_file"]))
    return {
        "actions_template": actions_template,
        "actions_few_shot_examples": actions_few_shot_examples,
        "actions_model": config["Actions"]["actions_model"],
        "answer_temperature": float(config["Actions"]["answer_temperature"]),
        "num_messages_generate_actions": int(config["Actions"]["num_messages_generate_actions"])
    }


def _get_chat_pipeline_config_data(config, root_dir):
    chat_template = common.read_file(os.path.join(root_dir, config["Chats"]["chat_template_file"]))
    return {
        "chat_template": chat_template,
        "chat_model": config["Chats"]["chat_model"],
        "chat_temperature": float(config["Chats"]["chat_temperature"]),
        "num_messages_generate_chat": int(config["Chats"]["num_messages_generate_chat"])
    }


def _get_search_config_data(config):
    return {
        "embedding_model": config["Search"]["embedding_model"],
    }


def _get_database_config_data(config, root_dir):
    return {
        "params": {
            "dbname": config["Database"]["dbname"],
            "host": config["Database"]["host"],
            "port": config["Database"]["port"]
        },
        "schema": config["Database"]["schema"],
        "message_table": config["Database"]["message_table"],
        "conversation_state_table": config["Database"]["conversation_state_table"],
        "bot_state_table": config["Database"]["bot_state_table"],
        "delete_db_script": os.path.join(root_dir, config["Database"]["delete_db_script"]),
        "create_db_script": os.path.join(root_dir, config["Database"]["create_db_script"]),
        "sql_file": os.path.join(root_dir, config["Database"]["sql_file"])
    }


def _get_config_data(config, root_dir):
    conversations = common.read_jsonl_file(os.path.join(root_dir, config["Test"]["conversations_file"]))
    root_config = configparser.ConfigParser()
    root_config.read(os.path.join(root_dir, config["Test"]["root_config_file"]))

    openai_client = openai.OpenAI(
        api_key=root_config["OPENAI"]["OPENAI_API_KEY"]
    )
    return {
        "conversations": conversations,
        "how_many_conversations": int(config["Test"]["how_many_conversations"]),
        "test_save_output_filepath": os.path.join(root_dir, config["Test"]["test_save_output_file"]),
        "openai_client": openai_client
    }


def get_config_data():
    file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.join(file_dir, "..")
    
    config = configparser.ConfigParser()
    config.read(os.path.join(file_dir, "test_config.ini"))

    return {
        'test': _get_config_data(config, root_dir),
        'database': _get_database_config_data(config, root_dir),
        'search': _get_search_config_data(config),
        'questions': _get_questions_pipeline_config_data(config, root_dir),
        'actions': _get_actions_pipeline_config_data(config, root_dir),
        'chat': _get_chat_pipeline_config_data(config, root_dir)
    }
