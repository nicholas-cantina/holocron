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


def evaluate_response(intent_response, dataset_response):
    response = dict()

    intent_response = parse.parse_raw_json_response(intent_response)
    dataset_response = parse.parse_raw_json_response(dataset_response)

    if intent_response is None:
        raise ValueError("Invalid intent response data")

    if dataset_response is None:
        raise ValueError("Invalid dataset response data")
    
    response['is_correct'] = 1

    if intent_response['send_image'] is False and dataset_response['send_image'] is False:
        response['is_correct'] = 1
    elif intent_response['send_image'] != dataset_response['send_image']:
        response['is_correct'] =  0
    elif intent_response['is_selfie'] != dataset_response['is_selfie']:
        response['is_correct'] =  0

    response['image_prompt_cosine_similarity'] = 0.0

    if intent_response['send_image'] is True and dataset_response['send_image'] is True:
        response['image_prompt_cosine_similarity'] = calculate_cosine_similarity(
            intent_response['image_prompt'], dataset_response['image_prompt'])

    return response


def generate_report(csv_data, incorrect_span_ids):
    report = dict()

    csv_data_len = len(csv_data)

    is_correct = np.zeros(csv_data_len)
    image_prompt_cosine_similarity = np.zeros(csv_data_len)

    for idx in range(csv_data_len):
        if 'is_correct' in csv_data[idx]:
            is_correct[idx] = int(csv_data[idx]['is_correct'])

        if 'image_prompt_cosine_similarity' in csv_data[idx]:
            image_prompt_cosine_similarity[idx] = float(csv_data[idx]['image_prompt_cosine_similarity'])


    report['total_examples'] = csv_data_len
    report['response_accuracy'] = round(is_correct.mean()  * 100, 2)
    report['response_accuracy_std'] = is_correct.std()
    report['image_prompt_cosine_similarity_avg'] = round(image_prompt_cosine_similarity.mean(), 2)
    report['image_prompt_cosine_similarity_std'] = image_prompt_cosine_similarity.std()

    report['incorrect_span_ids'] = incorrect_span_ids

    return report


def get_intent(_config_data, scenario_data, latest_event):
    eligible_bots = [bot for bot in scenario_data["users"]["bots"] 
                     if bot["id"] != latest_event["user_id"]]
    
    return {
        "intent": "chat",
        "bot_data": random.choice(eligible_bots) if eligible_bots else scenario_data["users"]["bots"] [0],
        "event": latest_event,
    }