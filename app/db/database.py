import json

def load_menu_data():
    with open("data/menu_db.json", "r", encoding="utf-8") as f:
        return json.load(f)
