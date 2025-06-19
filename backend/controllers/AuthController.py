from fastapi.responses import JSONResponse
from jose import jwt
from fastapi import HTTPException
import bcrypt
import os
from datetime import datetime, timedelta, time
from models.UserModel import UserLogin, User
from config.database import user_collection

# Secret and algorithm (you should keep this in .env and load via settings)
SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key")
ALGORITHM = "HS256"

async def login(userlogin: UserLogin) -> JSONResponse:
    if not userlogin.email.strip() or not userlogin.password:
        raise HTTPException(status_code=401, detail="Please provide all details.")

    user = await user_collection.find_one({'email': userlogin.email})

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if "password" in user and bcrypt.checkpw(userlogin.password.encode(), user["password"].encode()):
        # Create JWT payload
        payload = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "exp": datetime.utcnow() + timedelta(days=1)
        }

        # Generate token
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # Remove sensitive data before returning
        user.pop("password", None)

        # Create response and set token as HTTP-only cookie
        response = JSONResponse(content={
            "message": "User login success",
            "user": user
        })
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",
            max_age=86400  # 1 day
        )

        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

async def register(registeruser: User) -> JSONResponse:
    # Validate required fields
    if not all([
        registeruser.email.strip(),
        registeruser.password,
        registeruser.firstName.strip(),
        registeruser.lastName.strip(),
        registeruser.dob,
        registeruser.department,
        registeruser.role
    ]):
        raise HTTPException(status_code=400, detail="Please provide all details.")

    # Check if user already exists
    existing_user = await user_collection.find_one({"email": registeruser.email})
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Hash password
    hashed_password = bcrypt.hashpw(registeruser.password.encode(), bcrypt.gensalt()).decode()

    # Prepare user document
    user_dict = registeruser.dict()
    user_dict.update({
        'password': hashed_password,
        'dob': datetime.combine(registeruser.dob, time.min).isoformat(),  # Convert to ISO string
        'created_at': datetime.utcnow().isoformat()  # Convert to ISO string
    })

    # Insert user
    result = await user_collection.insert_one(user_dict)
    user = await user_collection.find_one({"_id": result.inserted_id})

    # Generate JWT token
    payload = {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Prepare response data - manually convert all dates and ObjectIds to strings
    response_user = {
        "_id": str(user["_id"]),
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "email": user["email"],
        "dob": user["dob"].isoformat() if isinstance(user["dob"], datetime) else user["dob"],
        "department": user["department"],
        "role": user["role"],
        "created_at": user["created_at"].isoformat() if isinstance(user.get("created_at"), datetime) else user.get("created_at")
    }
    response_user.pop("password", None)

    response = JSONResponse(
        content={
            "message": "User registration success",
            "user": response_user
        },
        status_code=201
    )

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="Lax",
        max_age=86400
    )

    return response
