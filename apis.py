from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from modules.mysql_connector import MySQLConnector
from apis import cognito_sign
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 제공
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# 메인 페이지 라우트를 먼저 정의
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 그 다음에 API 라우터 포함
app.include_router(cognito_sign.router, prefix="/api/auth", tags=["authentication"])


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/favicon.ico")
async def get_favicon():
    return Response(content="", media_type="image/x-icon")


@app.get("/api/health")
async def health_check():
    # 데이터베이스 연결 상태 확인
    try:
        await MySQLConnector.fetch_one("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {"status": "healthy", "database": db_status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apis:app", host="0.0.0.0", port=8000, reload=True)