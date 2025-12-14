from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db, get_graph_db
from app.api.v2.deps import get_current_user_info

router = APIRouter()

class OrderRequest(BaseModel):
    menu_name: str

@router.post("/order")
def create_order(
    order: OrderRequest,
    current_user: dict = Depends(get_current_user_info), # 토큰 검사
    graph_session = Depends(get_graph_db)                # Neo4j 연결
):
    user_id = current_user["id"]
    menu_name = order.menu_name

    # ====================================================
    #  Neo4j 그래프 업데이트
    # 1. 유저 노드 찾기 (MATCH)
    # 2. 메뉴 노드 찾거나 만들기 (MERGE)
    # 3. 둘 사이에 'ORDERED' 관계 선 긋기 (MERGE)
    # 4. 주문 횟수(count) 1 증가시키기
    # ====================================================
    query = """
    MATCH (u:User {user_id: $uid})
    MERGE (m:Menu {name: $menu_name})
    MERGE (u)-[r:ORDERED]->(m)
    ON CREATE SET r.count = 1, r.last_eaten = datetime()
    ON MATCH SET r.count = r.count + 1, r.last_eaten = datetime()
    RETURN u, r, m
    """
    
    graph_session.run(query, uid=user_id, menu_name=menu_name)

    return {
        "status": "success",
        "message": f"'{menu_name}' 주문이 그래프에 기록되었습니다.",
        "user": current_user["username"]
    }