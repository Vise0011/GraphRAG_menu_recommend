import json

# Load alchol.json
with open("alchol.json", "r", encoding="utf-8") as f:
    alchol_data = json.load(f)

# Load category.json
with open("category.json", "r", encoding="utf-8") as f:
    category_data = json.load(f)

# 메뉴별 통합 딕셔너리
menu_dict = {}

# 1. 술 → 메뉴들
for item in alchol_data:
    drink = item["menu"]
    for entry in item["category"]:
        menu = entry["type"]
        weight = entry["weight"]
        if menu not in menu_dict:
            menu_dict[menu] = {"menu": menu, "alchol": [], "category": []}
        menu_dict[menu]["alchol"].append({"type": drink, "weight": weight})

# 2. 카테고리 → 메뉴들
for item in category_data:
    category = item["menu"]
    for entry in item["category"]:
        menu = entry["type"]
        weight = entry["weight"]
        if menu not in menu_dict:
            menu_dict[menu] = {"menu": menu, "alchol": [], "category": []}
        menu_dict[menu]["category"].append({"type": category, "weight": weight})

# JSON으로 저장
with open("menu_merged.json", "w", encoding="utf-8") as f:
    json.dump(list(menu_dict.values()), f, ensure_ascii=False, indent=2)

print("병합 완료: menu_merged.json 생성됨")
