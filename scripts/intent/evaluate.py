import os
import sys
import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, parent_dir)

from scripts.intent import config
from src.utils import common, handlebars, generate
from src.intent import intent


def main():
    config_data = config.get_config_data()

    correct_predictions = 0
    incorrect_predictions = 0
    incorrect_span_ids = []

    dataset_path = config_data["intent_detection"]["test_dataset"]
    csv_data = common.read_csv_file(os.path.join(parent_dir, dataset_path))
    if csv_data is None:
        print("No dataset found.")
        return

    for idx in range(len(csv_data)):
        messages = intent.extract_messages(csv_data[idx]['user_prompt'])
        chat_history_only = messages['chat_history']
        last_message = messages['last_message']

        prompt_template = config_data["intent_detection"]["template"]
        prompt_data = {'chat_history': chat_history_only, 'last_message': last_message}
        model = config_data["intent_detection"]["model"]

        prompt_messages = handlebars.get_prompt_messages(prompt_template, prompt_data)

        intent_response = generate.get_completion(
            config_data,
            config_data["intent_detection"]["api_provider"],
            {"model": model, "temperature": float(config_data["intent_detection"]["temperature"])},
            prompt_messages
        )

        # Canned response to avoid calling the API
        # intent_response = """{
# "send_image": false
# }"""

        try:
            is_correct = intent.evaluate_response(intent_response, csv_data[idx]['response'])

            if is_correct:
                correct_predictions += 1
            else:
                incorrect_predictions += 1
                incorrect_span_ids.append(csv_data[idx]['span_id'])

            csv_data[idx]['new_model'] = model
            csv_data[idx]['new_response'] = intent_response
            csv_data[idx]['is_correct'] = is_correct
        except ValueError as e:
            print(f"\nWarning: evaluating response failed: {str(e)} on span_id {csv_data[idx]['span_id']}")

        print(".", end="")

    report = intent.generate_report(correct_predictions, incorrect_predictions, incorrect_span_ids)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"report_{timestamp}.txt"

    common.save_file(report_path, report)

    evaluation_output_path = f"evaluation_{timestamp}.csv"
    common.save_csv_file(evaluation_output_path, csv_data)


if __name__ == "__main__":
    main()
