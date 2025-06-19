import datetime
from bson import ObjectId

import bcrypt
from jose import jwt
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from models.UserModel import User
from config.database import user_collection
from utils.ErrorHandler import http_exception, server_error, conflict_error, not_found_error, bad_request_error
# from utils.SendMail import send_mail

async def get_manager_employees(user: User) -> JSONResponse:
    if user.role != 'Manager':
        raise unauthorized_error("You are not authorised to access details of other employees")
    try:
        res = user_collection.find({"managerId": str(user.id)})
        employees = []
        async for employee in res:
            employee["_id"] = str(employee["_id"])
            employees.append(employee)

        return JSONResponse(status_code=200, content={"employees": employees})

    except Exception as e:
        raise server_error(str(e))

async def get_employees(user: User) -> JSONResponse:
    try:
        res = user_collection.find({})
        employees = []
        async for employee in res:
            employee["_id"] = str(employee["_id"])
            employees.append(employee)

        return JSONResponse(status_code=200, content={"employees": employees})

    except Exception as e:
        raise server_error(str(e))

async def delete_user(user: User, user_id: str) -> JSONResponse:
    try:
        result = await user_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise not_found_error("User not found")

        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "User deleted successfully"})

    except HTTPException:
        raise

    except Exception as e:
        raise server_error(str(e))

