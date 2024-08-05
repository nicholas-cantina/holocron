import json

from typing import Dict, Optional, Generator


def read_file(filepath: str) -> Optional[str]:
    """Reads a text file and returns its content as a string. Returns None if there"s an error."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except OSError as e:
        print(f"An error occurred while reading {filepath}: {e}")
        return None


def read_json_file(filepath: str) -> Optional[Dict]:
    """Reads a JSON file and returns a dictionary. Returns None if there"s an error."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as e:
        print(f"An error occurred while reading {filepath}: {e}")
        return None


def read_jsonl_file(filepath: str) -> Generator[Dict, None, None]:
    """Reads a .jsonl file and yields each JSON object as a dictionary."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    yield json.loads(line)
    except (OSError, json.JSONDecodeError) as e:
        print(f"An error occurred while reading {filepath}: {e}")


def save_json_file(filepath: str, data: Dict) -> None:
    """Saves a dictionary as a JSON file. Prints an error message if the save fails."""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"Data successfully saved to {filepath}")
    except OSError as e:
        print(f"An error occurred while saving to {filepath}: {e}")


def save_jsonl_file(filepath: str, data: Generator[Dict, None, None]) -> None:
    """Saves a generator of dictionaries as a .jsonl file. Prints an error message if the save fails."""
    try:
        with open(filepath, "a", encoding="utf-8") as file:
            for item in data:
                file.write(json.dumps(item, ensure_ascii=False) + "\n")
            print(f"Data successfully saved to {filepath}")
    except OSError as e:
        print(f"An error occurred while saving to {filepath}: {e}")
