import pytest
from pydantic import ValidationError

from backend.app.settings import Settings


def test_settings_reject_weak_privacy_and_wildcards():
    for values in ({"aggregate_minimum": 2}, {"allowed_origins": ["*"]}, {"session_seconds": 1}):
        with pytest.raises(ValidationError):
            Settings(_env_file=None, **values)


def test_settings_use_environment_prefix(monkeypatch):
    monkeypatch.setenv("FEEDBACK_SESSION_SECONDS", "3600")
    assert Settings(_env_file=None).session_seconds == 3600
