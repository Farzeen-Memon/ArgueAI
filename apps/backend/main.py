from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

from app.api import debates, auth, websocket, analytics
from app.core.config import settings
from app.core.database import init_db
from app.websocket.manager import ConnectionManager

app = FastAPI(
    title="DebateAI API",
    description="AI Debate Club Platform Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(debates.router, prefix="/api/debates", tags=["debates"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# WebSocket manager
manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    await init_db()
    print("🚀 DebateAI API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 DebateAI API shutting down")

@app.get("/")
async def root():
    return {"message": "DebateAI API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DebateAI API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
