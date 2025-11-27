import pytest
from pydantic import ValidationError

from backend.app.settings import Settings


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"secure_cookies": True},
        {"secure_cookies": True, "allowed_origins": ["*"]},
        {
            "secure_cookies": True,
            "allowed_origins": ["https://example.com"],
            "database_url": "sqlite:///:memory:",
        },
    ],
)
def test_production_requires_https_and_durable_storage(values):
    with pytest.raises(ValidationError):
        Settings(environment="production", **values)


def test_valid_production_settings():
    assert Settings(
        environment="production",
        secure_cookies=True,
        allowed_origins=["https://feedback.example.com"],
    ).secure_cookies
