# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from neo4j import GraphDatabase
import os

# ==========================================
# 1. MySQL 설정 (유저 정보 저장용)
# ==========================================
# 접속 정보: 유저명:비번@주소/DB명
# 주의: 소켓 에러 방지를 위해 127.0.0.1 사용
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://dev_user:password@127.0.0.1:3306/menu_system"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    MySQL 세션을 생성하고, 사용 후 자동으로 닫아주는 의존성 함수
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# 2. Neo4j 설정 (메뉴 그래프용)
# ==========================================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        return self.driver.session()

# 전역 Neo4j 인스턴스 생성
neo4j_conn = Neo4jConnection()

def get_graph_db():
    """
    Neo4j 세션을 반환하는 의존성 함수
    """
    session = neo4j_conn.get_session()
    try:
        yield session
    finally:
        session.close()