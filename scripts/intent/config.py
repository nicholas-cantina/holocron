import os
import configparser

from src.utils import common


def _get_config_data(config, root_dir):
    template = common.read_file(os.path.join(root_dir, config["intent_detection"]["template_file"]))
    return {
        **config["intent_detection"],
        "template": template,
        "model_params": {
            "model": config["intent_detection"]["model"],
            "temperature": config["intent_detection"]["temperature"]
        }
    }


def _get_test_data(config, root_dir):
    root_config = configparser.ConfigParser()
    root_config.read(os.path.join(root_dir, config["common"]["root_config_file"]))
    return {
        "openai_key": root_config["api"]["OPENAI_API_KEY"]
    }


def get_config_data():
    file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.join(file_dir, "..", "..")

    config = configparser.ConfigParser()
    config.read(os.path.join(file_dir, "config.ini"))
    return {
        "intent_detection": _get_config_data(config, root_dir),
        "test": _get_test_data(config, root_dir)
    }
