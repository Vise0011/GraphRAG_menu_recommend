from fastapi import APIRouter, Body
from app.db.database import save_order_history, load_order_history, load_menu_data
from app.services.recommender import recommend_from_order

router = APIRouter()

# 주문 이력 저장
@router.post("/order/history")
async def save_order(data: dict = Body(...)):
    order_items = data.get("order_items", [])
    if not order_items:
        return {"status": "error", "message": "주문 내역이 비어 있습니다."}

    # 주문 이력 저장
    save_order_history(order_items)
    return {"status": "received", "message": "주문 이력이 저장되었습니다."}


# 주문 이력 기반 추천
@router.get("/order-based/recommendation")
async def recommend_by_order():
    # 이전 주문 내역과 전체 메뉴 로드
    order_history = load_order_history()
    menu_db = load_menu_data()

    # 추천 알고리즘 실행
    recommended = recommend_from_order(order_history, menu_db)

    return {"recommended": recommended}
