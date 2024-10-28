import os
import configparser


def _get_config_data(config):
    return {
        **config["IntentDetection"],
        "template": config["IntentDetection"]["prompt_path"],
        "model_params": {
            "model": config["IntentDetection"]["model"],
            "temperature": config["IntentDetection"]["temperature"]
        }
    }


def _get_test_data(config, root_dir):
    root_config = configparser.ConfigParser()
    root_config.read(os.path.join(root_dir, "config.ini"))
    return {
        "openai_key": root_config["Api"]["OPENAI_API_KEY"]
    }


def get_config_data():
    file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.join(file_dir, "..", "..")

    config = configparser.ConfigParser()
    config.read(os.path.join(file_dir, "test_config.ini"))
    return {
        "intent_detection": _get_config_data(config),
        "test": _get_test_data(config, root_dir)
    }
