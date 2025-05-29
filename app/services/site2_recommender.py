import os
import json
from collections import defaultdict

BASE_PATH = "data/site2_db"

# ✅ 추천 메뉴 + 가중치 리스트 생성 함수
def get_top5_menu_with_weights(input_menu: str):
    weight_map = defaultdict(lambda: defaultdict(float))

    for file in os.listdir(BASE_PATH):
        if not file.endswith(".json"):
            continue

        file_path = os.path.join(BASE_PATH, file)
        key_name = file.replace(".json", "")  # 예: alchol, price, etc

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for entry in data:
            if entry.get("menu") == input_menu:
                for cat in entry.get("category", []):
                    menu_name = cat["type"]
                    weight_map[menu_name][f"{key_name}_weight"] += cat["weight"]

    result = []
    for menu, weights in weight_map.items():
        total = sum(weights.values())
        item = {
            "menu": menu,
            "weight_sum": round(total, 4),
            **{k: round(v, 4) for k, v in weights.items()}
        }
        result.append(item)

    return sorted(result, key=lambda x: x["weight_sum"], reverse=True)[:5]