from fastapi import APIRouter, Depends
from app.database import get_graph_db
from app.api.v2.deps import get_current_user_info
from app.services.hf_llm import ask_hf_llama 

router = APIRouter()

@router.get("/rag-recommend")
def graph_rag_recommend(
    current_user: dict = Depends(get_current_user_info),
    graph_session = Depends(get_graph_db)
):
    user_id = current_user["id"]
    username = current_user["username"]

    # 1. Retrieval: 그래프 탐색 (Graph Traversal)
    # 논리: 내가 주문한 메뉴들 -> 그 메뉴들이 가진 태그(특징) -> 그 태그를 가진 다른 메뉴 추천
    query = """
    MATCH (u:User {user_id: $uid})-[:ORDERED]->(eaten:Menu)-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(rec:Menu)
    WHERE NOT (u)-[:ORDERED]->(rec)
    RETURN 
        rec.name as menu, 
        collect(DISTINCT t.name) as reasons, 
        count(t) as score
    ORDER BY score DESC
    LIMIT 3
    """
    
    result = graph_session.run(query, uid=user_id)
    
    # 데이터를 LLM이 이해하기 쉬운 문장으로 변환 (Context Construction)
    rag_context = []
    top_menus = []
    
    for record in result:
        menu_name = record["menu"]
        tags = record["reasons"]
        
        # LLM에게 줄 힌트 문장 생성
        context_str = f"추천 후보: {menu_name} (이유: 사용자가 선호하는 {', '.join(tags)} 특징을 가지고 있음)"
        rag_context.append(context_str)
        
        top_menus.append({"menu": menu_name, "weight_sum": record["score"]}) # ask_hf_llama 형식 맞춤

    if not rag_context:
        return {"message": "데이터가 부족해서 RAG 추론이 어렵습니다. 주문을 더 해주세요!"}

    # 2. Generation: LLM에게 맥락 주입
    print(f" [Graph RAG Context]: {rag_context}")
    
    llm_reason = ask_hf_llama(top_menus)

    return {
        "type": "Graph-RAG",
        "user_context": f"{username}님의 취향 그래프 분석 결과",
        "retrieved_knowledge": rag_context, 
        "llm_advice": llm_reason            
    }