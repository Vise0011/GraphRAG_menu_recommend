# app/api/v2/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.utils.security import SECRET_KEY, ALGORITHM

# 토큰을 헤더에서 꺼내주는 도구
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login")

def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """
    토큰을 해석해서 그 안에 들어있는 user_id와 username을 꺼내는 함수
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="자격 증명이 유효하지 않습니다 (토큰 오류)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("uid")
        
        if username is None or user_id is None:
            raise credentials_exception
            
        return {"id": user_id, "username": username}
        
    except JWTError:
        raise credentials_exception