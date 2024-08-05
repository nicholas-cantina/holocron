import json
import re

from functools import partial
from typing import Any, Dict, List, Optional
from pybars import Compiler


CLEAN_COMPILED_TEMPLATE = re.compile(r"\{[^{}]*\}|[^{}]+")


def not_helper(scope: Any, value: Any, *args: Any) -> bool:
    """Returns True if the value is False."""
    return not value


def gt_helper(scope: Any, value1: Any, value2: Any, *args: Any) -> bool:
    """Returns True if value1 is greater than value2."""
    return value1 > value2


def eq_helper(scope: Any, value1: Any, value2: Any, *args: Dict) -> bool:
    """Returns True if value1 equals value2."""
    return value1 == value2


def ne_helper(scope: Any, value1: Any, value2: Any, *args: Dict) -> bool:
    """Returns True if value1 equals value2."""
    return value1 != value2


def or_helper(scope: Any, *args: Any) -> bool:
    """Returns True if any argument is True."""
    return any(args)


def and_helper(scope: Any, *args: Any) -> bool:
    """Returns True if all arguments are True."""
    return all(args)


def len_helper(scope: Any, data: List, *args: Any) -> int:
    """Returns the length of a list."""
    return len(data)


def to_json_helper(scope: Any, data: Dict, *args: Any) -> str:
    """Converts a dictionary to a JSON string."""
    pruned_data = {k: v for k, v in data.items(
    ) if k in ["message", "user_id", "first_name", "full_name"]}
    return json.dumps(pruned_data, indent=4, ensure_ascii=False)


def role_helper(role: str, scope: Any, context: Any, *args: Any) -> str:
    """Returns True if the role matches the expected role."""
    return json.dumps({
        "role": role,
        "content": "".join(context["fn"](scope)).strip(),
    })


def test_helper(scope: Any, context: Any, *args: Any) -> bool:
    """Returns True if the value is True."""
    return json.dumps({
        "role": "user",
        "content": "".join(context["fn"](scope)).strip(),
    })


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
    cleaned_string = raw_string.replace("&quot;", '\\"')
    cleaned_string = cleaned_string.replace("\\\\", "\\").replace("\\\\", "\\")
    cleaned_string = cleaned_string.replace("\\'", "'")

    json_parts = re.split(r'(?=\{\"role\")', cleaned_string.strip())[1:]
    json_parts = [part.strip() for part in json_parts]

    return [json.loads(part) for part in json_parts]


def get_prompt_messages(prompt_template: str, prompt_data: Dict[str, Any]) -> List[Dict[str, str]]:
    compiled_prompt = compile_prompt(prompt_template, prompt_data)
    if compiled_prompt is None:
        return []
    return clean_compiled_prompt(compiled_prompt)
