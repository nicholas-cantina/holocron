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

    incorrect_span_ids = []

    dataset_path = config_data["intent_detection"]["intent_detection_test_dataset"]
    csv_data = common.read_csv_file(os.path.join(parent_dir, dataset_path))
    if csv_data is None:
        print("No dataset found.")
        return
    
    prompt_template = config_data["intent_detection"]["prompt_path"]
    prompt_content = common.read_file(os.path.join(parent_dir, prompt_template))

    csv_data_len = len(csv_data)

    print(f"Evaluating {csv_data_len} examples...")

    for idx in range(csv_data_len):
        messages = intent.extract_messages(csv_data[idx]['user_prompt'])
        chat_history_only = messages['chat_history']
        last_message = messages['last_message']

        prompt_data = {'chat_history': chat_history_only, 'last_message': last_message}
        model = config_data["intent_detection"]["model"]
        temperature = float(config_data["intent_detection"]["temperature"])

        prompt_messages = handlebars.get_prompt_messages(prompt_content, prompt_data)

        intent_response = generate.get_completion(
           config_data,
           config_data["intent_detection"]["api_provider"],
           {"model": model, "temperature": temperature},
           prompt_messages
        )

        # Canned response false to avoid calling the API
#         intent_response = """{
#  "send_image": false
#  }"""

    # Canned response true to avoid calling the API
#         intent_response = """{
#  "send_image": true,
#  "user_requestor": "jacob8601",
#  "bot_senders": [],
#  "is_selfie": true,
#  "main_subject": "<self> #dolphins",
#  "additional_subjects": [],
#  "image_prompt": "#dolphins"
#  }"""

        try:
            response = intent.evaluate_response(intent_response, csv_data[idx]['response'])

            is_response_correct = response['is_response_correct']
            
            if is_response_correct == 0:
                incorrect_span_ids.append(csv_data[idx]['span_id'])

            csv_data[idx]['new_model'] = model
            csv_data[idx]['new_response'] = intent_response
            csv_data[idx]['is_response_correct'] = is_response_correct
            csv_data[idx]['image_prompt_cosine_similarity'] = response['image_prompt_cosine_similarity']
            csv_data[idx]['is_senders_correct'] = response['is_senders_correct']
            csv_data[idx]['is_requestor_correct'] = response['is_requestor_correct']
        except ValueError as e:
            print(f"\nWarning: evaluating response failed: {str(e)} on span_id {csv_data[idx]['span_id']}")

        print(".", end="")
        sys.stdout.flush()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    evaluation_output_path = f"evaluation_{timestamp}.csv"
    common.save_csv_file(evaluation_output_path, csv_data)

    print("Generating report...")
    report = intent.generate_report(csv_data, incorrect_span_ids, model, temperature)

    baseline_path = config_data["intent_detection"]["baseline_path"]

    if baseline_path is None:
        print("Warning: no baseline found.")
    else:
        baseline_data = common.read_json_file(baseline_path)
        baseline_comparison = intent.compare_with_baseline(report, baseline_data)
        report = report | baseline_comparison

    report_path = f"evaluation_report_{timestamp}.json"

    common.save_json_file(report_path, report)


if __name__ == "__main__":
    main()
