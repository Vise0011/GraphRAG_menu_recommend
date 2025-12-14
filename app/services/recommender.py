def get_top5_menus(user_input: dict, menu_db: list) -> list:
    filtered = [
        item for item in menu_db
        if item["category"] == user_input["category"]
        and item["price"] == user_input["price_range"]
        and user_input["people"] in item["people"]
        and item["season"] == user_input["season"]
        and item["rain"] == user_input["rain"]
    ]

    # 상위 5개를 가중치 기준으로 정렬
    top5 = sorted(filtered, key=lambda x: x.get("weight_sum", 0), reverse=True)[:5]

    return top5 
