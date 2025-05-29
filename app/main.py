from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.endpoints import condition_weight

from dotenv import load_dotenv
import os

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")


app = FastAPI() 

# 정적 파일 mount
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 디렉토리 지정
templates = Jinja2Templates(directory="app/templates")

# 페이지 라우터
@app.get("/", response_class=HTMLResponse)
async def first_page(request: Request):
    return templates.TemplateResponse("first_page.html", {"request": request})

@app.get("/second", response_class=HTMLResponse)
async def second_page(request: Request):
    return templates.TemplateResponse("second_page.html", {"request": request})

# API 라우터 등록
app.include_router(condition_weight.router, prefix="/api/v1")


from app.api.v1.endpoints import menu_recommend

app.include_router(menu_recommend.router, prefix="/api/v1")
