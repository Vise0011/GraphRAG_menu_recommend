from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

# V1 라우터
from app.api.v1.endpoints import condition_weight, menu_recommend

# V2 라우터 (Auth, Order, Recommend, RAG, Weighted RAG)
from app.api.v2 import auth, order, recommend, rag_recommend, rag_weighted, visualize

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

app = FastAPI()

# 1. 정적 파일 연결 (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. 템플릿 엔진 설정
templates = Jinja2Templates(directory="app/templates")

# ==========================================
# [API] 백엔드 라우터 등록
# ==========================================

# V1
app.include_router(condition_weight.router, prefix="/api/v1", tags=["V1 Condition"])
app.include_router(menu_recommend.router, prefix="/api/v1", tags=["V1 Menu"])

# V2
app.include_router(auth.router, prefix="/api/v2/auth", tags=["V2 Auth"])
app.include_router(order.router, prefix="/api/v2", tags=["V2 Order"])
app.include_router(recommend.router, prefix="/api/v2", tags=["V2 Recommend"])
app.include_router(rag_recommend.router, prefix="/api/v2", tags=["V2 Graph RAG"])
app.include_router(rag_weighted.router, prefix="/api/v2", tags=["V2 Weighted RAG"])
app.include_router(visualize.router, prefix="/api/v2", tags=["Visualization"])

# ==========================================
# [View] HTML 페이지 라우터
# ==========================================

# 로그인 페이지
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 회원가입 페이지 연결
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def first_page(request: Request):
    return templates.TemplateResponse("first_page.html", {"request": request})

# 두 번째 페이지
@app.get("/second", response_class=HTMLResponse)
async def second_page(request: Request):
    return templates.TemplateResponse("second_page.html", {"request": request})