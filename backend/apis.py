from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from modules.mysql_connector import MySQLConnector
from apis import cognito_sign


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

# React 앱의 빌드 파일을 제공
app.mount("/static", StaticFiles(directory="../frontend/build/static"), name="static")
app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="react")

# API 라우터 포함
app.include_router(cognito_sign.router, prefix="/api/auth", tags=["authentication"])


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
