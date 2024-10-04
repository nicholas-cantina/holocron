import random


def get_intent(config_data, scenario_data, latest_event):
    eligible_bots = [bot for bot in scenario_data["users"]["bots"] 
                     if bot["id"] != latest_event["user_id"]]
    
    return {
        "intent": "chat",
        "bot_data": random.choice(eligible_bots) if eligible_bots else scenario_data["users"]["bots"] [0],
        "event": latest_event,
    }