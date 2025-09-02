from types import SimpleNamespace as Obj

import pytest

from backend.app.policy import Permission, Role, can_read_feedback, has_permission


def actor(role, id="a", grants=()):
    return Obj(role=role, id=id, grants=[Obj(permission=p) for p in grants])


@pytest.mark.parametrize("role", list(Role))
def test_draft_author_scope_never_widened_by_privilege(role):
    feedback = Obj(state="draft", employee_id="e", author_id="m", escalated=False)
    target = Obj(manager_id="m", active=True)
    assert not can_read_feedback(
        actor(role, grants=[Permission.FEEDBACK_ORGANIZATION]), feedback, target
    )


def test_manager_scope_and_admin_separation():
    feedback = Obj(state="published", employee_id="e", author_id="m", escalated=False)
    target = Obj(manager_id="m", active=True)
    assert can_read_feedback(actor(Role.MANAGER, "m"), feedback, target)
    assert not can_read_feedback(actor(Role.MANAGER, "other"), feedback, target)
    assert not can_read_feedback(actor(Role.ADMIN), feedback, target)
    assert has_permission(actor(Role.ADMIN), Permission.PEOPLE_MANAGE)
    assert not has_permission(actor(Role.ADMIN), Permission.FEEDBACK_ORGANIZATION)


def test_senior_only_sees_explicit_escalation_without_grant():
    feedback = Obj(state="published", employee_id="e", author_id="m", escalated=True)
    assert can_read_feedback(actor(Role.SENIOR), feedback, Obj(manager_id="m", active=True))
