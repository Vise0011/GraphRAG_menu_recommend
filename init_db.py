# init_db.py
from app.database import engine, Base
from app.db.models.user import User  # 이걸 import 해야 테이블이 인식됨

def init_db():
    print("데이터베이스 테이블 생성 중...")
    
    # 정의된 모든 모델(User 등)을 MySQL 테이블로 변환
    Base.metadata.create_all(bind=engine)
    
    print("테이블 생성 완료! (users 테이블이 만들어졌습니다)")

if __name__ == "__main__":
    init_db()