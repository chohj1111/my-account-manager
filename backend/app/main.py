from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, goals

app = FastAPI(
    title="My Account Manager",
    description="Target-Date 기반 절세형 자산 관리 및 리밸런싱 솔루션",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["goals"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
