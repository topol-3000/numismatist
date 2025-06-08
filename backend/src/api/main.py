from contextlib import asynccontextmanager
from logging import Logger
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from settings import settings
from utils.logger import get_logger

logger: Logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logger.info('Starting API server')
    yield
    logger.info('Gracefully shutdown API server')


app = FastAPI(
    title=settings.api.title,
    description=settings.api.description,
    version=settings.api.version,
    default_response=ORJSONResponse,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def root():
    return {'message': 'Numismatist API'}


@app.get('/health')
async def health_check():
    return {'status': 'ok'}