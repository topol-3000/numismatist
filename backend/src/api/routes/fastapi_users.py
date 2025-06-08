from fastapi_users import FastAPIUsers

from api.dependency.authentication.backend import authentication_backend
from api.dependency.authentication.user_manager import get_user_manager
from models import User
from utils.types import UserIdType

fastapi_users = FastAPIUsers[User, UserIdType](get_user_manager, [authentication_backend])

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
