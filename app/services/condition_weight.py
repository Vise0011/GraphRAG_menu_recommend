import os
import json
from collections import defaultdict

BASE_PATH = "/root/16_team/data/site1_db"

def load_condition_weights(condition_name, condition_value):
    """
    조건 값에 해당하는 메뉴별 가중치를 로드
    ex) people = "2" → people.json에서 "2"에 해당하는 메뉴와 가중치 반환
    """
    path = os.path.join(BASE_PATH, f"{condition_name}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}

    for entry in data:
        if entry["menu"] == condition_value:
            return {item["type"]: item["weight"] for item in entry["category"]}
    return {}

def get_weighted_top5(user_input: dict) -> list[dict]:
    """
    사용자 입력을 기반으로 각 조건별 가중치를 합산하여
    상위 5개의 추천 메뉴와 해당 가중치 상세 정보를 반환합니다.
    """
    condition_keys = ["people", "price", "time", "rain", "season", "alcohol", "category"]
    total_weights = defaultdict(lambda: defaultdict(float))

    for key in condition_keys:
        cond_val = user_input.get(key)
        if not cond_val:
            continue  # 조건값이 누락되었으면 건너뜀

        weights = load_condition_weights(key, cond_val)
        for menu, weight in weights.items():
            total_weights[menu][f"{key}_weight"] = weight
            total_weights[menu]["total_weight"] += weight

    # 총합 가중치 기준 정렬 후 상위 5개 메뉴 추출
    sorted_menus = sorted(
        total_weights.items(),
        key=lambda x: x[1]["total_weight"],
        reverse=True
    )[:5]

    result = []
    for menu_name, weights in sorted_menus:
        weights["menu"] = menu_name

        for key in condition_keys:
            weights.setdefault(f"{key}_weight", 0.0)

        result.append(dict(weights))  # defaultdict → dict

    return result
