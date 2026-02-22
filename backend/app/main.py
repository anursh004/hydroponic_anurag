from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.exceptions import AppException, app_exception_handler
from app.core.logging_config import setup_logging
from app.core.redis_client import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    await init_redis()
    yield
    await close_redis()
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    description="Hydroponic Farm Management Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)

# API Router
from app.api.v1.router import api_v1_router  # noqa: E402

app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": f"{settings.APP_NAME} API"}
