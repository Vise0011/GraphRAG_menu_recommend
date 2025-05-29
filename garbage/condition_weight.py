from fastapi import APIRouter, Body
from app.services.condition_weight import get_top5_with_sources
from sub.hf_llm import ask_hf_llama

router = APIRouter()

@router.post("/condition-weight")
async def recommend_from_conditions(data: dict = Body(...)):
    top5_detailed = get_top5_with_sources(data)

    llm_response = ask_hf_llama(top5_detailed)

    return {
        "top5": top5_detailed,
        "description": llm_response
    }
