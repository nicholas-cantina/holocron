import random
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, parent_dir)

from src.utils import parse


def extract_messages(messages):
    chat_history = messages

    chat_history = chat_history.replace("CHAT HISTORY:", "")
    chat_history = chat_history.replace(
        "Determine whether the LAST MESSAGE in this chat history is requesting an image.", "")
    chat_history = chat_history.replace("LAST MESSAGE:", "")
    chat_history = chat_history.replace("OUTPUT:", "")

    messages = chat_history.strip().split("\n")

    chat_history_only = "\n".join(messages[:-1])

    last_message = messages[-1]

    return {"chat_history": chat_history_only, "last_message": last_message}


def evaluate_response(intent_response, dataset_response):
    intent_response = parse.parse_raw_json_response(intent_response)
    dataset_response = parse.parse_raw_json_response(dataset_response)

    if intent_response is None:
        raise ValueError("Invalid intent response data")

    if dataset_response is None:
        raise ValueError("Invalid dataset response data")

    if intent_response['send_image'] is False and dataset_response['send_image'] is False:
        return True

    if intent_response['send_image'] != dataset_response['send_image']:
        return False

    if intent_response['is_selfie'] != dataset_response['is_selfie']:
        return False

    return True


def generate_report(correct_predictions, incorrect_predictions, incorrect_span_ids):
    report = f"Correct predictions: {correct_predictions}\n"
    report += f"Incorrect predictions: {incorrect_predictions}\n"
    total_predictions = correct_predictions + incorrect_predictions
    accuracy = (correct_predictions / total_predictions) * 100
    report += f"Accuracy: {accuracy:.2f}%\n"
    report += "Incorrect span IDs:\n"
    for span_id in incorrect_span_ids:
        report += f"- {span_id}\n"
    return report


def get_intent(_config_data, scenario_data, latest_event):
    eligible_bots = [bot for bot in scenario_data["users"]["bots"] 
                     if bot["id"] != latest_event["user_id"]]
    
    return {
        "intent": "chat",
        "bot_data": random.choice(eligible_bots) if eligible_bots else scenario_data["users"]["bots"] [0],
        "event": latest_event,
    }