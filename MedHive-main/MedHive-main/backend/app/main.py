from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional

from app.api.routes import users, auth, models, federated_learning, chat
from app.core.config import settings

app = FastAPI(
    title="HachathonHub API",
    description="Backend API for HachathonHub - AI-powered healthcare insights with federated learning",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(models.router, prefix="/api/models", tags=["ML Models"])
app.include_router(federated_learning.router, prefix="/api/federated-learning", tags=["Federated Learning"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to HachathonHub API",
        "version": "0.1.0",
        "documentation": "/docs",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 