from fastapi import APIRouter, Depends
from app.database import get_graph_db
from app.api.v2.deps import get_current_user_info
from app.services.hf_llm import ask_hf_llama

router = APIRouter()

@router.get("/recommend")
def recommend_menus(
    current_user: dict = Depends(get_current_user_info),
    graph_session = Depends(get_graph_db)
):
    user_id = current_user["username"]
    
    # 쿼리 수정: 추천된 메뉴(rec_menu)가 '나의 어떤 메뉴(my_menu)' 때문에 추천됐는지(history) 같이 가져옴
    query = """
    MATCH (me:User {username: $uid})-[:ORDERED]->(my_menu:Menu)
    MATCH (other:User)-[:ORDERED]->(my_menu)
    WHERE other.username <> $uid
    MATCH (other)-[:ORDERED]->(rec_menu:Menu)
    WHERE NOT (me)-[:ORDERED]->(rec_menu)
    RETURN 
        rec_menu.name AS menu, 
        count(*) AS score,
        collect(DISTINCT my_menu.name)[0..3] AS history  // 내가 먹었던 메뉴 3개까지만 가져오기
    ORDER BY score DESC
    LIMIT 5
    """
    
    result = graph_session.run(query, uid=user_id)
    
    top_menus = []
    my_history = [] # 내가 먹은 메뉴들 저장용

    for record in result:
        top_menus.append({"menu": record["menu"], "weight_sum": record["score"]})
        if not my_history: 
            my_history = record["history"] # 첫 번째 기록에서 내 과거 이력 가져오기

    # 데이터 부족 시 처리
    if not top_menus:
        return {
            "type": "fallback",
            "message": "데이터 부족",
            "menus": [],
            "llm_advice": "주문 이력이 쌓이면 비슷한 입맛의 유저를 찾아드릴게요!"
        }

    # ✅ LLM에게 보낼 '강제 조건' (2번 로직: 주문 데이터 기반)
    # 내가 먹은 메뉴(history)를 문자열로 만들어서 보냄
    history_str = ", ".join(my_history) if my_history else "기존 주문 메뉴"
    
    forced_conditions = {
        "logic": "User Similarity",  # 모드 식별자
        "history": history_str       # "현재 ~~메뉴를 시켜 드셨는데" 에 들어갈 내용
    }

    llm_reason = ask_hf_llama(top_menus, conditions=forced_conditions)

    return {
        "type": "personalized",
        "message": "비슷한 유저 추천 결과",
        "menus": [item['menu'] for item in top_menus],
        "llm_advice": llm_reason
    }