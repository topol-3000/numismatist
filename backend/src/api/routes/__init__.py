from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from .auth import router as auth_router
from .collections import router as collections_router
from .counterparties import router as counterparties_router
from .grading_company import router as grading_company_router
from .items import router as items_router
from .users import router as users_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api", dependencies=[Depends(http_bearer)])
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(items_router)
router.include_router(collections_router)
router.include_router(counterparties_router)
router.include_router(grading_company_router)
