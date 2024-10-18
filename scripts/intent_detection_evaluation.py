import os
import sys
import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, parent_dir)

from scripts import test_config
from src.utils import parse, common, handlebars, generate, intent


def main():
    config_data = test_config.get_config_data()

    correct_predictions = 0
    incorrect_predictions = 0
    incorrect_span_ids = []

    system_prompt_path = config_data["intent_detection"]["system_prompt_path"]
    user_prompt_path = config_data["intent_detection"]["user_prompt_path"]
    dataset_path = config_data["intent_detection"]["intent_detection_test_dataset"]

    model = config_data["intent_detection"]["model"]
    temperature = float(config_data["intent_detection"]["model_temperature"])

    system_prompt_content = common.read_file(os.path.join(parent_dir, system_prompt_path))

    if system_prompt_content is None:
        print("No system prompt content found.")
        return

    csv_data = common.read_csv_file(os.path.join(parent_dir, dataset_path))
    if csv_data is None:
        print("No Dataset data found.")
        return

    user_prompt_content = common.read_file(os.path.join(parent_dir, user_prompt_path))

    if user_prompt_content is None:
        print("No user prompt content found.")
        return

    for i in range(len(csv_data)):
        messages = intent.extract_messages(csv_data[i]['user_prompt'])
        chat_history_only = messages['chat_history']
        last_message = messages['last_message']

        user_prompt_data = {'chat_history': chat_history_only, 'last_message': last_message}

        user_prompt_rendered = handlebars.compile_prompt(user_prompt_content, user_prompt_data)

        if user_prompt_rendered is None:
            print("No user prompt content rendered.")
            return

        messages = [
            {"role": "system", "content": system_prompt_content},
            {"role": "user", "content": user_prompt_rendered},
        ]

        intent_response = generate.get_simple_completion(config_data, messages, model, temperature)

        # Canned response to avoid calling the API
        # intent_response = """{
# "send_image": false
# }"""

        try:
            isCorrect = intent.evaluate_response(intent_response, csv_data[i]['response'])

            if (isCorrect):
                correct_predictions += 1
            else:
                incorrect_predictions += 1
                incorrect_span_ids.append(csv_data[i]['span_id'])

            csv_data[i]['new_model'] = model
            csv_data[i]['new_response'] = intent_response
            csv_data[i]['is_correct'] = isCorrect
        except ValueError as e:
            print(f"\nWarning: evaluating response failed: {str(e)} on span_id {csv_data[i]['span_id']}")

        print(".", end="")

    report = intent.generate_report(correct_predictions, incorrect_predictions, incorrect_span_ids)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"report_{timestamp}.txt"

    common.save_file(report_path, report)

    evaluation_output_path = f"evaluation_{timestamp}.csv"
    common.save_csv_file(evaluation_output_path, csv_data)


if __name__ == "__main__":
    main()
