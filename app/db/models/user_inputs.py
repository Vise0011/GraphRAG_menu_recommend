from pydantic import BaseModel, Field

class UserInput(BaseModel):
    category: str = Field(..., example="초밥")
    price_range: str = Field(..., example="중간")
    people: int = Field(..., example=2)
    season: str = Field(..., example="summer")  # 또는 "봄", "여름" 등
    time: str = Field(..., example="18:00")      # HH:MM 형식
    rain: str = Field(..., example="0~3mm")
