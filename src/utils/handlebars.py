import json
import re
import html
from html.parser import HTMLParser

from functools import partial
from typing import Any, Dict, List, Optional
from pybars import Compiler


CLEAN_COMPILED_TEMPLATE = re.compile(r"\{[^{}]*\}|[^{}]+")


def not_helper(_scope: Any, value: Any, *_args: Any) -> bool:
    """Returns True if the value is False."""
    return not value


def gt_helper(_scope: Any, value1: Any, value2: Any, *_args: Any) -> bool:
    """Returns True if value1 is greater than value2."""
    return value1 > value2


def eq_helper(_scope: Any, value1: Any, value2: Any, *_args: Dict) -> bool:
    """Returns True if value1 equals value2."""
    return value1 == value2


def ne_helper(_scope: Any, value1: Any, value2: Any, *_args: Dict) -> bool:
    """Returns True if value1 equals value2."""
    return value1 != value2


def or_helper(_scope: Any, *args: Any) -> bool:
    """Returns True if any argument is True."""
    return any(args)


def and_helper(_scope: Any, *args: Any) -> bool:
    """Returns True if all arguments are True."""
    return all(args)


def len_helper(_scope: Any, data: List, *_args: Any) -> int:
    """Returns the length of a list."""
    return len(data)


def to_json_helper(_scope: Any, data: Dict, *_args: Any) -> str:
    """Converts a dictionary to a JSON string."""
    pruned_data = {k: v for k, v in data.items(
    ) if k in ["message", "user_id", "first_name", "full_name", "timestamp"]}

    json_string = json.dumps(pruned_data, ensure_ascii=False, sort_keys=True)
    json_string = json_string.replace("\"", "\\\"")
    return json_string


def role_helper(role: str, scope: Any, context: Any, *_args: Any) -> str:
    """Returns True if the role matches the expected role."""
    return json.dumps({
        "role": role,
        "content": "".join(context["fn"](scope)).strip(),
    }, separators=(',', ':'))


def test_helper(scope: Any, context: Any, *_args: Any) -> bool:
    """Returns True if the value is True."""
    return json.dumps({
        "role": "user",
        "content": "".join(context["fn"](scope)).strip(),
    }, separators=(',', ':'))


HELPERS = {
    "not": not_helper,
    "gt": gt_helper,
    "eq": eq_helper,
    "ne": ne_helper,
    "or": or_helper,
    "and": and_helper,
    "len": len_helper,
    "to_json": to_json_helper,
    "system": partial(role_helper, "system"),
    "assistant": partial(role_helper, "assistant"),
    "user": test_helper,
}


def compile_prompt(prompt_template: str, prompt_data: Dict[str, Any]) -> Optional[str]:
    compiler = Compiler()
    compiled_template = compiler.compile(prompt_template)
    return compiled_template(prompt_data, helpers=HELPERS)


def clean_compiled_prompt(raw_string: str) -> List[Dict[str, str]]:
    cleaned_string = raw_string.replace("\\\\", "\\").replace("\\\\", "\\")
    cleaned_string = html.unescape(cleaned_string)

    json_parts = re.split(r'(?=\{\"role\")', cleaned_string.strip())[1:]
    json_parts = [part.strip() for part in json_parts]

    return [json.loads(part) for part in json_parts]


def get_prompt_messages(prompt_template: str, prompt_data: Dict[str, Any]) -> List[Dict[str, str]]:
    compiled_prompt = compile_prompt(prompt_template, prompt_data)
    if compiled_prompt is None:
        return []
    return clean_compiled_prompt(compiled_prompt)
