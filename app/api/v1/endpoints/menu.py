from fastapi import APIRouter, Query
from app.services.condition_recommender import get_top5_menus_by_conditions

router = APIRouter()

@router.get("/menu/recommendation")
async def recommend_menu(
    category: str = Query(...),
    price: str = Query(...),
    people: int = Query(...),
    season: str = Query(...),
    time: str = Query(...),
    rain: str = Query(...)
):
    input_conditions = {
        "category": category,
        "price": price,
        "people": str(people),
        "season": season,
        "time": time,
        "rain": rain
    }

    top5 = get_top5_menus_by_conditions(input_conditions)  # 함수 호출

    return {
        "status": "success",
        "top5": top5
    }
