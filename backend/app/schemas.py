from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .passwords import validate_password

Text = Annotated[str, Field(min_length=1, max_length=4000)]
Name = Annotated[str, Field(min_length=1, max_length=120)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Login(Input):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalized_email(cls, value):
        return value.lower()


class PasswordChange(Input):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str

    @field_validator("new_password")
    @classmethod
    def strong_password(cls, value):
        return validate_password(value)


class VersionInput(Input):
    version: int = Field(ge=1)
