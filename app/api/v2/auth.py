from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db, get_graph_db
from app.db.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.utils.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel

router = APIRouter()

# ==========================================
# 1. 회원가입 API (나이, 성별 포함)
# ==========================================
@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    graph_session = Depends(get_graph_db)
):
    # 1. MySQL 중복 체크
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="이미 존재하는 사용자명입니다."
        )

    # 2. MySQL 저장 (age, gender 추가)
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username, 
        password_hash=hashed_password,
        age=user.age,          # [NEW]
        gender=user.gender     # [NEW]
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 3. Neo4j 노드 생성 (age, gender 속성 추가!)
    try:
        query = """
        CREATE (u:User {
            user_id: $uid, 
            username: $uname, 
            age: $age, 
            gender: $gender,
            created_at: datetime()
        })
        RETURN u
        """
        graph_session.run(
            query, 
            uid=new_user.id, 
            uname=new_user.username,
            age=new_user.age,       
            gender=new_user.gender  
        )
        print(f" Neo4j: User 노드 생성 완료 (ID: {new_user.id}, Age: {new_user.age})")
    except Exception as e:
        print(f" Neo4j 에러: {e}")
        # Neo4j 실패 시 롤백 로직이 필요할 수 있음

    return new_user


# ==========================================
# 2. 로그인 API
# ==========================================
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # 1. 유저 조회
    user = db.query(User).filter(User.username == login_data.username).first()
    
    # 2. 아이디/비번 검증
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 잘못되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. 토큰 발급
    access_token = create_access_token(data={"sub": user.username, "uid": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }