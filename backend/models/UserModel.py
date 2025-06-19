from pydantic import BaseModel, Field, validator, EmailStr
from bson import ObjectId
from typing import Optional, Literal
from datetime import date

class User(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    dob: date
    role: Literal["Manager", "Employee", "Admin"]
    department: Literal["HR", "Sales", "Engineering", "Marketing"]
    managerId: Optional[str] = Field(default=None)

    # @validator("managerId")
    # def check_valid_objectid(cls, v):
    #     if v is not None and not ObjectId.is_valid(v):
    #         raise ValueError("Invalid MongoDB ObjectId")
    #     return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(User):
    id: str = Field(alias="_id")

    @validator("id", pre=True, always=True)
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
