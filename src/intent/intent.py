import random
import os
import sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, parent_dir)

from src.utils import parse


def calculate_cosine_similarity(text1, text2):
    paragraphs = [text1, text2]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(paragraphs)

    similarity_matrix = cosine_similarity(tfidf_matrix)

    return similarity_matrix[0][1]

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


def evaluate_intent_response(intent_response, dataset_response):
    if intent_response['send_image'] is False and dataset_response['send_image'] is False:
        return 1
    elif intent_response['send_image'] != dataset_response['send_image']:
        return  0
    elif intent_response['is_selfie'] != dataset_response['is_selfie']:
        return  0

    return 1

def evaluate_senders(intent_response, dataset_response):
    if 'bot_senders' not in intent_response or 'bot_senders' not in dataset_response:
        return 0

    # TODO: convert to lowercase
    intent_senders = set(intent_response['bot_senders'])
    dataset_senders = set(dataset_response['bot_senders'])
    intent_senders_len = len(intent_senders)
    dataset_senders_len = len(dataset_senders)

    if intent_senders_len == 0 and dataset_senders_len == 0:
        return 1
    else:
        intersection = intent_senders.intersection(dataset_senders)
        intersection_len = len(intersection)
        if intersection_len == 0:
            return 0
        elif intersection_len == len(intent_senders) and intersection_len == len(dataset_senders):
            return 1
        else:
            max_len = max(intent_senders_len, dataset_senders_len)
            return intersection_len / max_len

def evaluate_requestor(intent_response, dataset_response):
    if 'user_requester' not in intent_response or 'user_requestor' not in dataset_response:
        return 0

    if intent_response['user_requester'].lower() == dataset_response['user_requestor'].lower():
        return 1
    else:
        return 0

def evaluate_response(intent_response, dataset_response):
    response = dict()

    intent_response = parse.parse_raw_json_response(intent_response)
    dataset_response = parse.parse_raw_json_response(dataset_response)

    if intent_response is None:
        raise ValueError("Invalid intent response data")

    if dataset_response is None:
        raise ValueError("Invalid dataset response data")
    
    # Response
    response['is_response_correct'] = evaluate_intent_response(intent_response, dataset_response)

    # Cosine Similarity
    response['image_prompt_cosine_similarity'] = 0.0

    if intent_response['send_image'] is True and dataset_response['send_image'] is True:
        response['image_prompt_cosine_similarity'] = calculate_cosine_similarity(
            intent_response['image_prompt'], dataset_response['image_prompt'])

    # Senders
    response['is_senders_correct'] = evaluate_senders(intent_response, dataset_response)

    # Requestor
    response['is_requestor_correct'] = evaluate_requestor(intent_response, dataset_response)

    return response


def generate_report(csv_data, incorrect_span_ids, model, temperature):
    report = dict()

    csv_data_len = len(csv_data)

    is_response_correct = np.zeros(csv_data_len)
    image_prompt_cosine_similarity = np.zeros(csv_data_len)
    is_sender_correct = np.zeros(csv_data_len)
    is_requestor_correct = np.zeros(csv_data_len)

    for idx in range(csv_data_len):
        if 'is_response_correct' in csv_data[idx]:
            is_response_correct[idx] = int(csv_data[idx]['is_response_correct'])

        if 'image_prompt_cosine_similarity' in csv_data[idx]:
            image_prompt_cosine_similarity[idx] = float(csv_data[idx]['image_prompt_cosine_similarity'])

        if 'is_senders_correct' in csv_data[idx]:
            is_sender_correct[idx] = float(csv_data[idx]['is_senders_correct'])

        if 'is_requestor_correct' in csv_data[idx]:
            is_requestor_correct[idx] = float(csv_data[idx]['is_requestor_correct'])
    
    report['model'] = model
    report['temperature'] = temperature
    report['total_examples'] = csv_data_len
    report['response_accuracy'] = round(is_response_correct.mean()  * 100, 2)
    report['image_prompt_cosine_similarity_avg'] = round(image_prompt_cosine_similarity.mean(), 2)
    report['senders_accuracy'] = round(is_sender_correct.mean() * 100, 2)
    report['requestor_accuracy'] = round(is_requestor_correct.mean() * 100, 2)

    report['incorrect_span_ids'] = incorrect_span_ids

    return report

def compare_with_baseline(report, baseline_data):
    if baseline_data is None:
        return
    
    updated_report = dict()

    if 'response_accuracy' in report and 'response_accuracy' in baseline_data:
        updated_report['response_accuracy_change'] = float(report['response_accuracy']) - float(baseline_data['response_accuracy'])
    if 'image_prompt_cosine_similarity_avg' in report and 'image_prompt_cosine_similarity_avg' in baseline_data:
        updated_report['image_prompt_cosine_similarity_change'] = float(report['image_prompt_cosine_similarity_avg']) - float(baseline_data['image_prompt_cosine_similarity_avg'])
    if 'senders_accuracy' in report and 'senders_accuracy' in baseline_data:
        updated_report['senders_accuracy_change'] = float(report['senders_accuracy']) - float(baseline_data['senders_accuracy'])
    if 'requestor_accuracy' in report and 'requestor_accuracy' in baseline_data:
        updated_report['requestor_accuracy_change'] = float(report['requestor_accuracy']) - float(baseline_data['requestor_accuracy'])

    return updated_report

def get_intent(_config_data, scenario_data, latest_event):
    eligible_bots = [bot for bot in scenario_data["users"]["bots"] 
                     if bot["id"] != latest_event["user_id"]]
    
    return {
        "intent": "chat",
        "bot_data": random.choice(eligible_bots) if eligible_bots else scenario_data["users"]["bots"] [0],
        "event": latest_event,
    }