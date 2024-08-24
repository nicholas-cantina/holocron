import configparser
import os
import sys
import openai

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import common


def get_test_data():
    
    file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.join(file_dir, "..")
    
    config = configparser.ConfigParser()
    config.read(os.path.join(file_dir, "test_config.ini"))

    conversations = common.read_jsonl_file(os.path.join(root_dir, config["Test"]["conversations_file"]))
    questions = common.read_json_file(os.path.join(root_dir, config["Test"]["questions_file"]))

    question_reframe_template = common.read_file(
        os.path.join(root_dir, config["Template"]["question_reframe_template_file"])
    )
    answer_template = common.read_file(
        os.path.join(root_dir, config["Template"]["answer_template_file"])    
    )
    actions_template = common.read_file(
        os.path.join(root_dir, config["Template"]["actions_template_file"])
    )
    chat_template = common.read_file(
        os.path.join(root_dir, config["Template"]["chat_template_file"])
    )

    question_answer_few_shot_examples_file = common.read_json_file(
        os.path.join(root_dir, config["Template"]["question_answer_few_shot_examples_file"])
    )
    question_reframed_question_few_shot_examples_file = common.read_json_file(
        os.path.join(root_dir, config["Template"]["question_reframed_question_few_shot_examples_file"])
    )
    question_output_schema = common.read_json_file(
        os.path.join(root_dir, config["Template"]["question_output_schema_file"])
    )

    root_config = configparser.ConfigParser()
    root_config.read(os.path.join(root_dir, config["Test"]["root_config_file"]))

    openai_client = openai.OpenAI(
        api_key=root_config["OPENAI"]["OPENAI_API_KEY"]
    )

    # TODO: group by step in process
    # TODO: rename the template variables to be keyed by the template they'll be a part of
    return {
        "database": {
            "params": {
                "dbname": config["Database"]["dbname"],
                "host": config["Database"]["host"],
                "port": config["Database"]["port"]
            },
            "schema": config["Database"]["schema"],
            "search_table": config["Database"]["search_table"],
            "delete_db_script": os.path.join(root_dir, config["Database"]["delete_db_script"]),
            "create_db_script": os.path.join(root_dir, config["Database"]["create_db_script"]),
            "sql_file": os.path.join(root_dir, config["Database"]["sql_file"])
        },
        "template": {
            "question_reframe_template": question_reframe_template,
            "question_reframed_question_few_shot_examples": question_reframed_question_few_shot_examples_file,
            "question_answer_few_shot_examples": question_answer_few_shot_examples_file,
            "question_output_schema": question_output_schema,
            "answer_template": answer_template,
            "actions_template": actions_template,
            "chat_template": chat_template,
        },
        "generation": {
            "embedding_model": config["Generation"]["embedding_model"],
            "question_model": config["Generation"]["question_model"],
            "answer_model": config["Generation"]["answer_model"],
            "chat_model": config["Generation"]["chat_model"],
            "question_temperature": float(config["Generation"]["question_temperature"]),
            "answer_temperature": float(config["Generation"]["answer_temperature"]),
            "chat_temperature": float(config["Generation"]["chat_temperature"]),
            "openai_client": openai_client
        },
        "memory": {
            "num_messages_generate_answers": int(config["Memory"]["num_messages_generate_answers"]),
            "num_messages_generate_chat": int(config["Memory"]["num_messages_generate_chat"])
        },
        "test": {
            "conversations": conversations,
            "questions": questions,
            "how_many_conversations": int(config["Test"]["how_many_conversations"]),
            "test_save_output_filepath": os.path.join(root_dir, config["Test"]["test_save_output_file"]),
        },
    }
