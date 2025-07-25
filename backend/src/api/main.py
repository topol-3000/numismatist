from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import Logger
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router
from database import database
from settings import StorageBackend, settings
from utils.logger import get_logger

logger: Logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting API server")
    yield
    logger.info("Gracefully shutdown API server")
    await database.close()


app = FastAPI(
    title=settings.api.title,
    description=settings.api.description,
    version=settings.api.version,
    default_response=ORJSONResponse,
    lifespan=lifespan,
)

# Mount static files for local storage
if settings.storage.backend == StorageBackend.LOCAL:
    # Ensure the uploads directory exists
    uploads_path = Path(settings.storage.local_path)
    uploads_path.mkdir(parents=True, exist_ok=True)

    # Mount static files
    app.mount("/static", StaticFiles(directory=str(uploads_path)), name="static")

app.include_router(router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Numismatist API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
