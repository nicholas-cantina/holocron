import json
import re
from functools import partial

from typing import Any, Dict, List, Optional
from pybars import Compiler


CLEAN_COMPILED_TEMPLATE = re.compile(r"\{[^{}]*\}|[^{}]+")

def remove_chars_outside_braces(text):
    # This regex matches any text within braces and marks it as a group
    # and captures everything outside braces
    regex = r'\{[^{}]*\}|[^{}]+'
    
    # Function to replace only the characters outside braces
    def replacement(match):
        if match.group().startswith('{') and match.group().endswith('}'):
            return match.group()
        else:
            return ''
    
    result = re.sub(regex, replacement, text, flags=re.DOTALL)
    return result

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

def to_json_helper(scope: Any, data: Any, *args: Any) -> str:
    """Converts a dictionary to a JSON string."""
    return json.dumps(data, indent=4, ensure_ascii=False)

def role_helper(role: str, scope: Any, context: Any, *args: Any) -> str:
    """Returns True if the role matches the expected role."""
    return json.dumps({
        "content": "".join(context["fn"](scope)).strip(),
        "role": role
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
    "user": partial(role_helper, "user"),
}

def generate_prompt(prompt_template: str, prompt_data: Dict[str, Any]) -> Optional[str]:
    """Generates a prompt using a handlebars template."""
    compiler = Compiler()
    compiled_template = compiler.compile(prompt_template)
    return compiled_template(prompt_data, helpers=HELPERS)

def make_messages(prompt_template: str, prompt_data: Dict[str, Any]) -> List[Dict[str, str]]:
    generated_prompt = generate_prompt(prompt_template, prompt_data)
    if generated_prompt is None:
        return []
    return remove_chars_outside_braces(generated_prompt)
