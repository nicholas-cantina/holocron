import datetime


def get_prompt_data(scenerio_data, bot_data, messages, memories):
    dt_now = datetime.datetime.now()
    return {
        "current_date": dt_now.strftime("%Y-%m-%d"),
        "current_time": dt_now.strftime("%H:%M:%S"),
        "bot": {
            "first_name": bot_data["first_name"],
            "full_name": bot_data["full_name"],
            "personality": bot_data["personality"]
        },
        "users_in_conversation": scenerio_data["users"]["bots"] + scenerio_data["users"]["humans"],
        "memories": memories,
        "messages": messages,
    }