from fastapi import APIRouter, Depends, Query
from pydantic import EmailStr, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..dependencies import current_user, get_db, public_user, require
from ..errors import fail
from ..models import AuditEvent, Grant, User
from ..passwords import hash_password, validate_password
from ..people import revoke_sessions, validate_manager, visible_people
from ..policy import Permission, Role
from ..schemas import Input, Name

router = APIRouter(prefix="/people", tags=["People"])


class PersonCreate(Input):
    name: Name
    email: EmailStr
    password: str
    role: Role = Role.EMPLOYEE
    department: str = Field(default="General", min_length=1, max_length=80)
    title: str = Field(default="", max_length=120)
    manager_id: str | None = None

    @field_validator("password")
    @classmethod
    def strong_password(cls, value):
        return validate_password(value)


class PersonUpdate(Input):
    name: Name | None = None
    role: Role | None = None
    department: str | None = Field(default=None, min_length=1, max_length=80)
    title: str | None = Field(default=None, max_length=120)
    manager_id: str | None = None
    active: bool | None = None


class GrantInput(Input):
    permission: Permission


@router.get("")
def people(
    q: str = Query(default="", max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=100),
    actor: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    query = visible_people(actor)
    if q:
        query = query.where(User.name.icontains(q, autoescape=True))
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = db.scalars(query.order_by(User.name, User.id).offset(offset).limit(limit)).all()
    return {
        "items": [public_user(user) for user in items],
        "total": total,
        "offset": offset,
        "limit": limit,
    }
