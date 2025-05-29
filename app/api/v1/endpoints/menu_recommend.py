from fastapi import APIRouter
from pydantic import BaseModel
from app.services.site2_recommender import get_top5_menu_with_weights

router = APIRouter()

class MenuRequest(BaseModel):
    menu: str

from app.services.hf_llm import ask_site2_llama  # site1용이 아닌 새 함수

@router.post("/menu-recommend")
def recommend_menu(req: MenuRequest):
    top5_list = get_top5_menu_with_weights(req.menu)
    menu_names = [m["menu"] for m in top5_list]
    reason = ask_site2_llama(top5_list, req.menu)  # 수정된 부분

    return {
        "top5": [m["menu"] for m in top5_list],
        "reason": reason  # ← 이게 None이거나 누락되어 있으면 웹에 안 보임
    }
