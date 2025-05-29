from pydantic import BaseModel, Field
from typing import List

class MenuItem(BaseModel):
    menu: str = Field(..., example="연어초밥세트")
    category: str = Field(..., example="초밥")
    price: str = Field(..., example="중간")  # 저가, 중간, 고가
    season: str = Field(..., example="summer")
    time: str = Field(..., example="18:00")
    rain: str = Field(..., example="0~3mm")
    people: List[int] = Field(..., example=[1, 2])
