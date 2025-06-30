from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from .auth import router as auth_router
from .collections import router as collections_router
from .items import router as items_router
from .users import router as users_router
from .dealers import router as dealers_router
from .transactions import router as transactions_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix='/api', dependencies=[Depends(http_bearer)])
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(items_router)
router.include_router(collections_router)
router.include_router(dealers_router)
router.include_router(transactions_router)
