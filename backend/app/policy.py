from enum import StrEnum


class Role(StrEnum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    SENIOR = "senior_management"
    ADMIN = "admin"


class Permission(StrEnum):
    PEOPLE_MANAGE = "people.manage"
    GRANTS_MANAGE = "grants.manage"
    CYCLES_MANAGE = "cycles.manage"
    AUDIT_READ = "audit.read"
    ORGANIZATION_READ = "dashboard.organization"
    FEEDBACK_ORGANIZATION = "feedback.read_organization"
    FEEDBACK_EXPORT = "feedback.export"


DEFAULT_PERMISSIONS = {
    Role.EMPLOYEE: frozenset(),
    Role.MANAGER: frozenset(),
    Role.SENIOR: frozenset({Permission.ORGANIZATION_READ}),
    Role.ADMIN: frozenset(
        {
            Permission.PEOPLE_MANAGE,
            Permission.GRANTS_MANAGE,
            Permission.CYCLES_MANAGE,
            Permission.AUDIT_READ,
        }
    ),
}


def has_permission(actor, permission: Permission) -> bool:
    return permission in DEFAULT_PERMISSIONS.get(actor.role, ()) or permission in {
        grant.permission for grant in actor.grants
    }


def manages(actor, target) -> bool:
    return actor.role == Role.MANAGER and target.manager_id == actor.id and target.active


def can_read_feedback(actor, feedback, target) -> bool:
    if feedback.state == "draft":
        return feedback.author_id == actor.id and manages(actor, target)
    return (
        feedback.employee_id == actor.id
        or manages(actor, target)
        or has_permission(actor, Permission.FEEDBACK_ORGANIZATION)
        or (actor.role == Role.SENIOR and feedback.escalated)
    )


def can_write_feedback(actor, feedback, target) -> bool:
    return feedback.author_id == actor.id and manages(actor, target)
