from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from .core.config import settings
from .api import tasks, auth, chat

from contextlib import asynccontextmanager
from .db import create_db_and_tables
from .models import user, task, conversation, message  # Import models to register them with SQLModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    # Log validation errors for debugging
    print(f"Validation error: {exc.errors()}")
    print(f"Request body: {exc.model.__name__ if hasattr(exc, 'model') else 'Unknown'}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Request validation failed", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log full traceback to server stdout for debugging
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api/tasks")
app.include_router(chat.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

# Routers will be registered here in Phase 3
