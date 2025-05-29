import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ✅ 로컬 모델 경로 (이미 다운로드된 경로)
MODEL_DIR = "/root/16_team/app/llama/Llama-3.1-8B-Instruct"

# ✅ 모델 및 토크나이저 로드 (최초 실행 시 느릴 수 있음)
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16
).to("cuda")


def ask_hf_llama(top5_list: list[dict]) -> str:
    prompt_text = "다음은 메뉴 추천을 위한 데이터 분석 결과이다.\n"
    prompt_text += "추천 메뉴 5가지를 선정하고, 각 메뉴의 추천 이유를 설명해 달라.\n"
    prompt_text += "설명에는 데이터 기반 요소(각 요소별 가중치 등) 외에도 일반적인 특징(맛, 계절, 어울리는 상황 등)을 포함해달라.\n"
    prompt_text += "설명은 이야기 형식으로 작성하고, 수치는 가중치로 명확히 표시해라.\n\n"

    for i, item in enumerate(top5_list, 1):
        menu = item.get("menu", f"추천{i}")
        total_score = item.get("weight_sum", 0.0)

        detailed_weights = {
            k.replace("_weight", ""): v
            for k, v in item.items()
            if k.endswith("_weight")
        }

        weight_str = ', '.join([
            f"{key} ({value:.2f})" for key, value in sorted(detailed_weights.items(), key=lambda x: x[1], reverse=True)
        ])

        prompt_text += f"- 추천 메뉴 {i}: {menu} (총합 가중치: {total_score:.2f})\n"
        prompt_text += f"  - 이 메뉴는 {weight_str}와 같은 요소를 반영하여 추천되었다.\n"
        prompt_text += f"  - 또한, {menu}의 일반적인 특징과 어울리는 상황을 고려해 자세히 설명해달라.\n"

    prompt_text += "\n[질문]\n"
    prompt_text += "위 정보를 바탕으로 각 메뉴가 추천된 이유를 자연스럽게 설명해줘."

    print("🧠 [프롬프트 전송]")
    print(prompt_text)

    # ✅ 토크나이징
    inputs = tokenizer(prompt_text, return_tensors="pt").to("cuda")

    # ✅ 생성
    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=True,
        top_p=0.9,
        temperature=0.7,
        repetition_penalty=1.2,
        eos_token_id=tokenizer.eos_token_id
    )

    # ✅ 결과 디코딩
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    only_response = full_text[len(prompt_text):].strip()

    print("🧠 [LLM 응답]")
    print(only_response)

    return only_response

def ask_site2_llama(top5_list, base_menu=None):
    print("🧠 [Site2 프롬프트 전송] 기준 메뉴:", base_menu)
    return ask_hf_llama(top5_list)