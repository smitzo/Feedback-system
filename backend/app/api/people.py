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


@router.post("", status_code=201)
def create_person(
    data: PersonCreate, actor: User = Depends(current_user), db: Session = Depends(get_db)
):
    require(actor, Permission.PEOPLE_MANAGE)
    if actor.role != Role.ADMIN and data.role != Role.EMPLOYEE:
        fail(403, "Only an administrator can assign privileged roles")
    email = str(data.email).lower()
    if db.scalar(select(User.id).where(User.email == email)):
        fail(409, "An account already uses that email")
    validate_manager(db, None, data.manager_id)
    user = User(
        **data.model_dump(exclude={"password", "email"}),
        email=email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.flush()
    db.add(
        AuditEvent(
            actor_id=actor.id, action="person.created", resource_type="user", resource_id=user.id
        )
    )
    return public_user(user)


@router.patch("/{user_id}")
def update_person(
    user_id: str,
    data: PersonUpdate,
    actor: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require(actor, Permission.PEOPLE_MANAGE)
    # Serialize graph and final-administrator changes on databases supporting row locks.
    db.scalars(select(User).order_by(User.id).with_for_update()).all()
    target = db.get(User, user_id)
    if not target:
        fail(404, "Employee not found")
    updates = data.model_dump(exclude_unset=True)
    if any(value is None for key, value in updates.items() if key != "manager_id"):
        fail(422, "Only manager_id may be cleared")
    if actor.role != Role.ADMIN and ("role" in updates or target.role != Role.EMPLOYEE):
        fail(403, "Only an administrator can change privileged accounts")
    role = updates.get("role", target.role)
    active = updates.get("active", target.active)
    if target.role == Role.ADMIN and (role != Role.ADMIN or not active):
        others = db.scalar(
            select(func.count())
            .select_from(User)
            .where(User.role == Role.ADMIN, User.active, User.id != target.id)
        )
        if not others:
            fail(409, "Keep at least one active administrator")
    if (target.role == Role.MANAGER and role != Role.MANAGER) or not active:
        if db.scalar(select(User.id).where(User.manager_id == target.id, User.active).limit(1)):
            fail(409, "Reassign active direct reports first")
    if "manager_id" in updates:
        validate_manager(db, target.id, updates["manager_id"])
    for key, value in updates.items():
        setattr(target, key, value)
    if {"role", "active", "manager_id"} & updates.keys():
        revoke_sessions(db, target.id)
    db.add(
        AuditEvent(
            actor_id=actor.id, action="person.updated", resource_type="user", resource_id=target.id
        )
    )
    return public_user(target)


@router.get("/{user_id}/grants")
def grants(user_id: str, actor: User = Depends(current_user), db: Session = Depends(get_db)):
    if actor.role != Role.ADMIN:
        fail(403, "Only administrators manage grants")
    target = db.get(User, user_id)
    if not target:
        fail(404, "Employee not found")
    return {"items": [grant.permission for grant in target.grants], "available": list(Permission)}


@router.post("/{user_id}/grants", status_code=204)
def add_grant(
    user_id: str,
    data: GrantInput,
    actor: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if actor.role != Role.ADMIN:
        fail(403, "Only administrators manage grants")
    target = db.get(User, user_id)
    if not target:
        fail(404, "Employee not found")
    if not any(g.permission == data.permission for g in target.grants):
        db.add(Grant(user_id=user_id, permission=data.permission))
        revoke_sessions(db, user_id)
        db.add(
            AuditEvent(
                actor_id=actor.id, action="grant.added", resource_type="user", resource_id=user_id
            )
        )


@router.delete("/{user_id}/grants/{permission}", status_code=204)
def remove_grant(
    user_id: str,
    permission: Permission,
    actor: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if actor.role != Role.ADMIN:
        fail(403, "Only administrators manage grants")
    target = db.get(User, user_id)
    if not target:
        fail(404, "Employee not found")
    for grant in target.grants:
        if grant.permission == permission:
            db.delete(grant)
            revoke_sessions(db, user_id)
            db.add(
                AuditEvent(
                    actor_id=actor.id,
                    action="grant.removed",
                    resource_type="user",
                    resource_id=user_id,
                )
            )
