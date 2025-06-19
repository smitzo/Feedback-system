from fastapi import APIRouter, Request
from controllers.UserController import get_employees, get_manager_employees, delete_user
from middlewares.auth import require_roles
router = APIRouter()

@router.get("/admin/employees/", dependencies=[require_roles([])])
async def get_all_employees(request:Request):
    return await get_employees()

@router.get("/manager/employees", dependencies=[require_roles(['Manager'])])
async def _get_manager_employees(request:Request):
    return await get_manager_employees()

@router.delete("/users/{user_id}", dependencies=[require_roles([])])
async def remove_users(request:Request):
    return await delete_user()

@router.put("/users/{user_id}", dependencies=[require_roles([])])
async def edit_user(request:Request):
    return await edit_user()