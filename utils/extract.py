import re

from datetime import datetime


CAPTURE_FULL_NAME_PATTERN = re.compile(r"Your full_name is(.*?),")
CAPTURE_USER_NAME_PATTERN = re.compile(r"your user_id is(.*?)\.")
CAPTURE_PERSONALITY_PATTERN = re.compile(
    r"identity is defined as:\n(.*?)\n\n Your full_name is", re.DOTALL)
CAPTURE_OTHER_USER_NAME_PATTERN = re.compile(r"^(.*?)\:")

SPICE_LEVEL_PATTERN = re.compile(r"Profanity is always allowed and encouraged.")
CONVERSATION_STYLE_SHORT_PATTERN = re.compile(r"Keep messages short, under 15 words")
CONVERSATION_STYLE_MEDIUM_PATTERN = re.compile(r"Keep messages short. Do not exceed 45 words")
CONVERSATION_STYLE_LONG_PATTERN = re.compile(
    r"Keep messages short, when possible. Keep responses under 300 words")

def find_first(lst, condition):
    return next((x for x in lst if condition(x)), None)

def extract_bot(conversation):
    first_user_message_content = conversation["conversations"][1]["content"]
    user_name = re.search(CAPTURE_USER_NAME_PATTERN, first_user_message_content).group(1).strip()
    full_name = re.search(CAPTURE_FULL_NAME_PATTERN, first_user_message_content).group(1).strip()
    personality = re.search(CAPTURE_PERSONALITY_PATTERN, first_user_message_content).group(1).strip()
    spice_level = "spicy" if re.search(SPICE_LEVEL_PATTERN, first_user_message_content) else "mild"
    conversation_style, word_limit = ("short", 15) if \
        re.search(CONVERSATION_STYLE_SHORT_PATTERN, first_user_message_content) \
            else ("medium", 45) if re.search(CONVERSATION_STYLE_MEDIUM_PATTERN, first_user_message_content) \
            else ("long", 256 * 3 / 4)

    return {
        "text_model": "gpt-4o",
        "full_name": full_name,
        "first_name": full_name.split(" ")[0],
        "user_name": user_name,
        "spice_level": spice_level,
        "conversation_style": conversation_style,
        "personality": personality,
        "greeting": "",  # not testing this yet
        "word_limit": word_limit,  # not testing this yet
    }

def extract_conversation(conversation):
    last_message = find_first(reversed(conversation["conversations"]), lambda message: message["role"] == "user")
    last_message_user_id = re.search(CAPTURE_OTHER_USER_NAME_PATTERN, last_message["content"]).group(1)
    return {
        "should_retry_with_different_token_length": False,  # setting to False for now
        "misattribution_retry_count": 0,  # setting to 0 for now
        "inappropriateness_retry_count": 0,  # setting to 0 for now
        "is_greeting": False,  # not testing this yet
        "is_goodbye": False,  # not testing this yet
        "is_welcome_room_greeting": False,  # not testing this yet
        "welcome_room_user_first_name": "",  # not testing this yet
        "last_human_message_fullname": last_message_user_id, # assumes users have same user_id and full name
    }

def extract_current_time():
    return datetime.now().strftime("%H:%M")

def extract_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def extract_channel(conversation):
    # assumes all users are in the room before the final message
    users_in_room = {}
    sent_messages = conversation["conversations"][2:]
    for message in sent_messages:
        if message["role"] == "user":
            user_id = re.search(CAPTURE_OTHER_USER_NAME_PATTERN, message["content"]).group(1)
            users_in_room[user_id] = {
                "first_name": user_id.split(" ")[0],
                "last_name": ""  # assumes user has no last name
            }
    return {
        "users_in_room": users_in_room.values()
    }

def extract_sent_messages(conversation):
    first_user_message_content = conversation["conversations"][1]["content"]
    bot_user_name = re.search(CAPTURE_USER_NAME_PATTERN, first_user_message_content).group(1).strip()
    bot_full_name = re.search(CAPTURE_FULL_NAME_PATTERN, first_user_message_content).group(1).strip()

    sent_message_objects = []
    sent_messages = conversation["conversations"][2:]
    for message in sent_messages:
        if message["role"] == "user":
            user_id = re.search(CAPTURE_OTHER_USER_NAME_PATTERN, message["content"]).group(1)
            sent_message_objects.append({
                "user_id": user_id,
                "first_name": user_id.split(" ")[0],  # assumes users have no last name
                "full_name": user_id,  # assumes users have same user_id and full name
                "message": message["content"]
            })
        else:
            sent_message_objects.append({
                "user_id": bot_user_name,
                "first_name": bot_full_name.split(" ")[0],
                "full_name": "",  # assumes bot has no last name
                "message": message["content"]
            })
    return sent_message_objects

def extract_prompt_data(conversation):
    return {
        "bot": extract_bot(conversation),
        "conversation": extract_conversation(conversation),
        "current_time": extract_current_time(),
        "current_date": extract_current_date(),
        "channel": extract_channel(conversation),
        "messages": extract_sent_messages(conversation)
    }
