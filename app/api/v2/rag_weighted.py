from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from app.database import get_graph_db
from app.services.hf_llm import ask_hf_llama

router = APIRouter()

# 입력 데이터 검증용 모델
class RecommendationRequest(BaseModel):
    people: str | None = None
    price: str | None = None
    time: str | None = None
    rain: str | None = None
    season: str | None = None
    alcohol: str | None = None
    category: str | None = None

@router.post("/rag-weighted-recommend")
async def recommend_by_context(request: RecommendationRequest, graph_session=Depends(get_graph_db)):
    conditions = request.dict(exclude_none=True)

    # 1. 입력값 딕셔너리로 변환
    conditions = request.dict(exclude_none=True)
    print(f"📡 [요청 수신]: {conditions}")

    # ==========================================
    # [Value Mapping] 프론트엔드 값 -> DB 값 보정
    # ==========================================
    # 1) 인원수 (예: "3" -> "3명")
    if "people" in conditions:
        val = str(conditions["people"]).replace("명", "")
        conditions["people"] = f"{val}명"

    # 2) 시간 (예: "18" -> "18시")
    if "time" in conditions:
        try:
            t = int(str(conditions["time"]).replace("시", ""))
            conditions["time"] = f"{t}시"
        except:
            pass

    # 3) 계절 매핑
    season_map = {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}
    if "season" in conditions and conditions["season"] in season_map:
        conditions["season"] = season_map[conditions["season"]]

    # 4) 강수량 매핑
    rain_map = {
        "0mm": "0mm", "3mm": "0~3mm", "15mm": "3~15mm", 
        "30mm": "30mm 이상", "30mm_high": "30mm 이상"
    }
    if "rain" in conditions and conditions["rain"] in rain_map:
        conditions["rain"] = rain_map[conditions["rain"]]

    # 5) 주류 매핑
    alcohol_map = {
        "no_alchol": "없음", "fr_beer": "생맥주", "soju": "소주", "beer": "맥주",
        "high": "하이볼", "wisky": "위스키", "pri_sohu": "증류소주", "sake": "사케"
    }
    if "alcohol" in conditions and conditions["alcohol"] in alcohol_map:
        conditions["alcohol"] = alcohol_map[conditions["alcohol"]]

    print(f"🔧 [DB 매핑 후 조건]: {conditions}")

    # ==========================================
    # [Core Logic] 하드코딩 점수 기반 쿼리
    # ==========================================
    # 설명: DB에 weight 속성이 없어도, 여기서 점수(THEN 3)를 강제로 줍니다.
    
    query = """
    MATCH (m:Menu)
    
    // 1. 계절 (맞으면 2점)
    OPTIONAL MATCH (m)<-[:GOOD_MATCH]-(:Context {value: $season})
    WITH m, CASE WHEN $season IS NOT NULL THEN 2 ELSE 0 END AS s_score
    
    // 2. 날씨 (맞으면 3점)
    OPTIONAL MATCH (m)<-[:GOOD_MATCH]-(:Context {value: $rain})
    WITH m, s_score, CASE WHEN $rain IS NOT NULL THEN 3 ELSE 0 END AS w_score
    
    // 3. 시간대 (맞으면 2점)
    OPTIONAL MATCH (m)<-[:GOOD_MATCH]-(:Context {value: $time})
    WITH m, s_score, w_score, CASE WHEN $time IS NOT NULL THEN 2 ELSE 0 END AS t_score
    
    // 4. 인원수 (맞으면 1점)
    OPTIONAL MATCH (m)<-[:GOOD_MATCH]-(:Context {value: $people})
    WITH m, s_score, w_score, t_score, CASE WHEN $people IS NOT NULL THEN 1 ELSE 0 END AS p_score
    
    // 5. 주류 (강력 추천 +5점)
    OPTIONAL MATCH (m)<-[:PAIRED_WITH]-(:Menu {name: $alcohol})
    WITH m, s_score, w_score, t_score, p_score, CASE WHEN $alcohol IS NOT NULL THEN 5 ELSE 0 END AS a_score

    // 6. 총점 계산
    WITH m, (s_score + w_score + t_score + p_score + a_score) AS total_score
    
    // 하나라도 점수를 얻은 메뉴만 조회
    WHERE total_score > 0
    RETURN m.name AS menu, total_score
    ORDER BY total_score DESC
    LIMIT 3
    """

    # 쿼리에 넣을 파라미터 준비 (없는 키는 None 처리)
    params = {
        "season": conditions.get("season"),
        "rain": conditions.get("rain"),
        "time": conditions.get("time"),
        "people": conditions.get("people"),
        "alcohol": conditions.get("alcohol")
    }

    result = graph_session.run(query, **params)
    
    # 결과 변환
    top_menus = [{"menu": r["menu"], "weight_sum": r["total_score"]} for r in result]
    rag_context = [f"메뉴 '{item['menu']}' (추천 점수: {item['weight_sum']}점)" for item in top_menus]

    # ==========================================
    # [Fallback] 결과가 0개일 때 비상 대책
    # ==========================================
    message = "선택하신 조건에 딱 맞는 메뉴입니다!"
    
    if not top_menus:
        print("⚠️ 검색 결과 0건 -> 베스트셀러 모드 작동")
        message = "조건에 완벽히 맞는 메뉴가 없어서, 요즘 인기 있는 메뉴를 추천해 드려요!"
        
        fallback_query = """
        MATCH (m:Menu)<-[r:ORDERED]-()
        RETURN m.name AS menu, count(r) AS score
        ORDER BY score DESC LIMIT 3
        """
        fb_result = graph_session.run(fallback_query)
        top_menus = [{"menu": r["menu"], "weight_sum": r["score"]} for r in fb_result]
        rag_context = [f"인기 메뉴 '{item['menu']}' (주문 수: {item['weight_sum']}회)" for item in top_menus]

    # ==========================================
    # [LLM] 설명 생성 요청
    # ==========================================
    llm_reason = ask_hf_llama(top_menus, conditions=conditions)

    return {
        "type": "Context-Aware RAG",
        "menus": [m['menu'] for m in top_menus],
        "llm_advice": llm_reason # "현재 비가 오고..." 멘트 생성
    }