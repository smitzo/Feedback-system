from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from typing import List, Union
from bson import ObjectId

from utils.exceptions import UnauthorizedException, ForbiddenException
from models.UserModel import User
from config.database import user_collection

security = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key")
ALGORITHM = "HS256"


def require_roles(allowed_roles: List[str]):
    """Dependency to check if user has required role"""
    async def role_checker(request: Request, user:User):
        try:
            allowed_roles += 'Admin'
            token = request.cookies.get("token")

            if not token:
                raise UnauthorizedException("Authentication required")

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")

            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")

            user = await user_collection.find_one({"_id": ObjectId(user_id)})

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if user['role'] not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "Forbidden",
                        "required_roles": allowed_roles,
                        "your_role": user['role'],
                        "message": "Access denied."
                    }
                )

            return user
        except (JWTError, ValueError) as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    return Depends(role_checker)
