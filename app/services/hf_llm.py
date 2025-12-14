import torch
import gc
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

MODEL_DIR = "/root/16_team/app/llama/Llama-3.1-8B-Instruct"

_model = None
_tokenizer = None

def load_model():
    global _model, _tokenizer
    if _model is not None: return _model, _tokenizer

    print("⏳ 모델 로딩 중...")
    gc.collect()
    torch.cuda.empty_cache()
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )

    _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    _model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    # Llama-3 패딩 토큰 설정
    if _tokenizer.pad_token_id is None:
        _tokenizer.pad_token_id = _tokenizer.eos_token_id
        
    return _model, _tokenizer

class PromptRequest(BaseModel):
    top5: list

@app.post("/prompt")
async def generate_prompt(req: PromptRequest):
    return {"result": ask_hf_llama(req.top5)}

def ask_hf_llama(top5_list: list[dict], conditions: dict = None) -> str:
    model, tokenizer = load_model()

    menu_names = [item.get("menu", "") for item in top5_list]
    rec_menu_str = ", ".join(menu_names)
    target_menu = menu_names[0] if menu_names else "추천 메뉴"

    # ====================================================
    # 🎯 1. 로직 분기 (상황 vs 유저) - 문맥(Context) 생성
    # ====================================================
    if conditions and conditions.get("logic") == "User Similarity":
        # [2번] 비슷한 유저 Pick
        history = conditions.get("history", "이전 메뉴")
        context_desc = f"사용자는 과거에 '{history}'를 주문했음. 유사한 입맛의 그룹은 '{target_menu}'를 선호함."
        
        guide_sentence = (
            f"손님, 이전에 {history}를 맛있게 드셨군요! "
            f"회원님과 입맛이 꼭 닮은 미식가분들은 주로 {target_menu}를 선택하셨어요. "
            f"이 메뉴는 [맛/식감 특징]이 있어서 회원님 취향을 저격할 거예요!"
        )
    
    elif conditions:
        # [1번] 상황 기반 추천
        cond_list = []
        if conditions.get('people'): cond_list.append(f"인원 {conditions['people']}")
        if conditions.get('rain') and conditions['rain'] not in ['없음', '0mm']: 
            cond_list.append(f"날씨 {conditions['rain']} 비")
        elif conditions.get('season'):
            cond_list.append(f"계절 {conditions['season']}")
        if conditions.get('time'): cond_list.append(f"시간 {conditions['time']}")
        
        price = conditions.get('price', '0')
        if price in ['0', '0~10000원']: price_desc = "가성비 예산"
        else: price_desc = f"예산 {price}"
        cond_list.append(price_desc)

        if conditions.get('category'): cond_list.append(f"선호 카테고리 {conditions['category']}")

        situation_summary = ", ".join(cond_list)
        context_desc = f"현재 상황: {situation_summary}. 추천 메뉴: {target_menu}."
        
        guide_sentence = (
            f"손님, 현재 {situation_summary}인 상황에 맞춰, "
            f"다른 손님들이 가장 많이 찾으신 {target_menu}를 강력 추천드려요! "
            f"이 메뉴는 [맛/식감 특징]이 있어서 지금 상황에 딱입니다."
        )

    else:
        # 기본
        context_desc = f"일반 추천 상황. 메뉴: {target_menu}"
        guide_sentence = f"손님, 요즘 제일 잘 나가는 {target_menu}를 추천드려요!"

    # ====================================================
    # 📝 2. Llama-3 전용 Chat 프롬프트 구성 (핵심 수정)
    # ====================================================
    
    # System Message: 역할 부여
    system_prompt = (
        "너는 이자카야의 친절하고 센스 있는 점장이다. "
        "주어진 상황과 메뉴에 대해 손님에게 권하는 말을 한 마디로 작성해라. "
        "설명은 구체적이고 감각적이어야 하며(3문장 이상), 없는 재료를 지어내면 안 된다."
    )

    # User Message: 입력 데이터와 지시사항
    user_prompt = f"""
    [상황 정보]
    {context_desc}

    [답변 가이드라인]
    다음 문장 흐름을 자연스럽게 이어서 완성해라:
    "{guide_sentence}"

    [주의사항]
    1. 가이드라인의 문장으로 시작하되, 뒤에 메뉴의 맛과 식감을 아주 풍성하게 묘사해라.
    2. '답안:', '점장:', '주의:' 같은 헤더를 절대 붙이지 마라.
    3. 오직 점장의 대사만 출력해라.
    """

    # 🔥 Llama-3 Chat Template 적용
    # <|begin_of_text|>...<|start_header_id|>assistant<|end_header_id|>
    prompt = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        f"점장: 손님," # 👈 AI가 여기서부터 말하도록 강제 시작점 생성
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=400,
            do_sample=True,
            top_p=0.9,
            temperature=0.4, 
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id
        )

    # ====================================================
    # 🧹 3. 후처리 (Cleaning)
    # ====================================================
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # "점장: 손님," 뒷부분만 잘라내기
    if "점장: 손님," in full_text:
        # prompt에 넣었던 시작점 뒤에 AI가 생성한 텍스트를 붙임
        generated_part = full_text.split("점장: 손님,")[-1].strip()
        final_response = "손님, " + generated_part
    else:
        # 혹시라도 포맷이 깨지면 프롬프트 제거 후 사용
        final_response = full_text.replace(prompt, "").strip()

    # 잡다한 기호 제거
    garbage = ["[답안]", "답:", "*주의*", "Note:", "비고:", "시스템:", "user:", "assistant:"]
    for g in garbage:
        final_response = final_response.replace(g, "")
        
    return final_response.strip()

# 호환성 유지
def ask_site2_llama(top5_list, base_menu=None):
    return ask_hf_llama(top5_list)