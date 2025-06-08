from fastapi import APIRouter

from api.dependency.authentication.backend import authentication_backend
from api.routes.fastapi_users import fastapi_users
from schemas.user import UserCreate, UserRead

router = APIRouter(prefix='/auth', tags=['Auth'])

# /login
# /logout
router.include_router(router=fastapi_users.get_auth_router(authentication_backend))

# /register
router.include_router(router=fastapi_users.get_register_router(UserRead, UserCreate))

# /forgot-password
# /reset-password
router.include_router(router=fastapi_users.get_reset_password_router())
