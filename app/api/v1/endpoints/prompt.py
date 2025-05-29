from fastapi import APIRouter, Body
from garbage.llm_prompt import ask_llama3

router = APIRouter()

@router.post("/prompt/ask")
async def get_llm_response(data: dict = Body(...)):
    menu_list = data.get("menus", [])
    if not menu_list:
        return {"error": "빈 메뉴 리스트입니다."}

    response_text = ask_llama3(menu_list)
    return {"response": response_text}
