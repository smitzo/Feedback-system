from sqlalchemy import delete, select

from .errors import fail
from .models import LoginSession, User
from .policy import Permission, Role, has_permission, manages


def visible_people(actor):
    query = select(User)
    if has_permission(actor, Permission.PEOPLE_MANAGE):
        return query
    if actor.role == Role.MANAGER:
        return query.where((User.id == actor.id) | ((User.manager_id == actor.id) & User.active))
    return query.where(User.id == actor.id)


def employee_record(db, actor, employee_id):
    target = db.get(User, employee_id)
    if not target or (target.id != actor.id and not manages(actor, target)):
        fail(404, "Employee not found")
    return target


def revoke_sessions(db, user_id):
    db.execute(delete(LoginSession).where(LoginSession.user_id == user_id))


def validate_manager(db, target_id, manager_id):
    if manager_id is None:
        return
    visited = {target_id}
    current = db.get(User, manager_id)
    if not current or not current.active or current.role != Role.MANAGER:
        fail(422, "Choose an active manager")
    while current:
        if current.id in visited:
            fail(422, "Reporting relationships cannot contain a cycle")
        visited.add(current.id)
        current = db.get(User, current.manager_id) if current.manager_id else None
