# C:\Download\16_team\app\services\llm_prompt.py
import requests
import os

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
HUGGINGFACE_TOKEN = os.getenv("HF_API_TOKEN")  # 또는 직접 문자열로 넣기

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
    "Content-Type": "application/json"
}

def build_prompt(menu_list):
    menu_str = ", ".join(menu_list)
    return f"추천할 메뉴는 다음과 같습니다: {menu_str}. 각 메뉴에 대해 간단한 설명을 해주세요."

def ask_llama3_external(menu_list):
    prompt = build_prompt(menu_list)

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        return result
    else:
        return f"에러: {response.status_code} - {response.text}"
