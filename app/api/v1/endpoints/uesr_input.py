from fastapi import APIRouter
from app.db.models.user_inputs import UserInput
from app.services.recommender import get_top5_menus
from app.db.database import load_menu_data

router = APIRouter()

@router.post("/user-input")
async def receive_user_input(data: UserInput):
    # 메뉴 DB 로딩
    menu_db = load_menu_data()

    # 추천 알고리즘 실행
    top5 = get_top5_menus(data.dict(), menu_db)

    # 결과 반환
    return {
        "status": "success",
        "message": "추천 메뉴 계산 완료",
        "top5": top5
    }
