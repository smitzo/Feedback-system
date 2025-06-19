from fastapi import APIRouter, Response

from controllers.AuthController import login, register
from models.UserModel import User, UserLogin
from middlewares.auth import require_roles

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login_user(user:UserLogin):
    """Login endpoint"""
    return await login(user)

@router.post("/register", dependencies=[require_roles([])])
async def register_user(user:User):
    """Login endpoint"""
    return await register(user)

# @router.post("/logout")
# async def logout(response: Response):
#     """Logout endpoint"""
#     return await auth_controller.logout(response)
