from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, users, collections, documents, chat, research, search, evaluation, admin
from app.config import settings
from app.database import engine
import app.models  # Ensures all models are registered
from app.models.base import Base
from app.qdrant_client import init_qdrant


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create PostgreSQL tables on startup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"DB Initialization Warning: {e}")

    # Initialize Qdrant vector collection
    try:
        init_qdrant()
        print("Qdrant collection initialized successfully.")
    except Exception as e:
        print(f"Qdrant Initialization Warning: {e}")

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(collections.router, prefix=f"{settings.API_V1_STR}/collections", tags=["collections"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(research.router, prefix=f"{settings.API_V1_STR}/research", tags=["research"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(evaluation.router, prefix=f"{settings.API_V1_STR}/evaluation", tags=["evaluation"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])


@app.get("/health")
async def health_check():
    return {"status": "online", "platform": settings.PROJECT_NAME, "version": "1.0.0"}