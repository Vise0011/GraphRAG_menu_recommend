import pandas as pd
import json

# CSV 파일 경로
df = pd.read_csv(r"C:\Download\16_team\data\non_var\menu_time_edges.csv")

# weight을 float로 변환
df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(0.0).astype(float)

# ✅ target 기준으로 그룹핑
grouped = df.groupby("target")

# JSON 결과 생성
result = []
for target_name, group in grouped:
    categories = [
        {
            "type": row["source"],
            "weight": round(row["weight"], 4)
        } for _, row in group.iterrows()
    ]
    result.append({
        "menu": target_name,
        "category": categories
    })

# JSON 파일로 저장
with open("time.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
