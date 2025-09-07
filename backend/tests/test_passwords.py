import pytest

from backend.app.passwords import hash_password, validate_password, verify_password


def test_password_hashes_are_salted_and_reject_wrong_credentials():
    first = hash_password("A strong passphrase 42")
    assert first != hash_password("A strong passphrase 42")
    assert verify_password("A strong passphrase 42", first)
    assert not verify_password("wrong", first)


@pytest.mark.parametrize("value", ["", "short", " " * 14, "a" * 129])
def test_password_bounds(value):
    with pytest.raises(ValueError):
        validate_password(value)


@pytest.mark.parametrize("value", ["invalid", "pbkdf2_sha256$999999999$x$y", "other$310000$x$y"])
def test_malformed_hash_fails_closed(value):
    assert not verify_password("password", value)
