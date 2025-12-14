from pydantic import BaseModel
from typing import Optional

# 회원가입 시 받을 데이터
class UserCreate(BaseModel):
    username: str
    password: str
    age: Optional[int] = None
    gender: Optional[str] = None

# 응답으로 줄 데이터
class UserOut(BaseModel):
    id: int
    username: str
    age: Optional[int]
    gender: Optional[str]

    class Config:
        from_attributes = True