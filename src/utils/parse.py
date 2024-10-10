import json


def parse_raw_json_response(response):
    return json.loads(response.strip("```").strip().lstrip('json').strip())


def cleanup_and_load_json(response):
    response = response.replace("```json", "")
    response = response.replace("```", "")
    response = response.strip()

    if (response == ""):
        return None

    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        print(response)
        print(f"Invalid JSON: {e.msg}")

    return data
