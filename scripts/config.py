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

    chat_prompt_template = common.read_file(
        os.path.join(root_dir, config["Template"]["chat_prompt_template_file"])
    )
    memory_prompt_template = common.read_file(
        os.path.join(root_dir, config["Template"]["memory_prompt_template_file"])    
    )

    root_config = configparser.ConfigParser()
    root_config.read(os.path.join(root_dir, config["Test"]["root_config_file"]))

    openai_client = openai.OpenAI(
        api_key=root_config["OPENAI"]["OPENAI_API_KEY"]
    )

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
        "test": {
            "conversations": conversations,
            "questions": questions,
            "how_many_conversations": int(config["Test"]["how_many_conversations"]),
            "test_save_output_filepath": os.path.join(root_dir, config["Test"]["test_save_output_file"]),
        },
        "template": {
            "chat_prompt_template": chat_prompt_template,
            "memory_prompt_template": memory_prompt_template
        },
        "generation": {
            "openai_client": openai_client,
            "memory_model": config["Generation"]["memory_model"],
            "chat_model": config["Generation"]["chat_model"],
            "memory_temperature": float(config["Generation"]["memory_temperature"]),
            "chat_temperature": float(config["Generation"]["chat_temperature"]),
            "embedding_model": config["Generation"]["embedding_model"]
        },
        "memory": {
            "num_messages_generate_answers": int(config["Memory"]["num_messages_generate_answers"]),
            "num_messages_generate_chat": int(config["Memory"]["num_messages_generate_chat"])
        }
    }
