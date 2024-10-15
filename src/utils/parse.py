import json


def parse_raw_json_response(response):
    return json.loads(response.strip("```").strip().lstrip('json').strip())
