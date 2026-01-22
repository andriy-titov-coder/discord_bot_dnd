import json
import os
import math


LEVEL_UP_MULTIPLIER = 1.10
EXP_PER_LEVEL = 100

def get_player_path(user_id):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "src", "database", "players", f"{user_id}.json")

def load_player(user_id):
    path = get_player_path(user_id)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_player(user_id, data):
    path = get_player_path(user_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def add_experience(user_id, amount):
    data = load_player(user_id)
    if not data:
        return False, None

    if "level" not in data: data["level"] = 1
    if "exp" not in data: data["exp"] = 0

    data["exp"] += amount
    level_up = False
    new_level = data["level"]


    while data["exp"] >= EXP_PER_LEVEL:
        data["exp"] -= EXP_PER_LEVEL
        data["level"] += 1
        new_level = data["level"]
        level_up = True


        for stat in ["strength", "agility", "magic", "max_health"]:
            if stat in data["stats"]:
                data["stats"][stat] = math.floor(data["stats"][stat] * LEVEL_UP_MULTIPLIER)


        data["stats"]["health"] = data["stats"]["max_health"]


    if data["exp"] < 0:
        data["exp"] = 0

    save_player(user_id, data)
    return level_up, new_level