from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix='/api', dependencies=[Depends(http_bearer)])
