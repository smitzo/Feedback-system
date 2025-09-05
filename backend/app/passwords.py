import hashlib
import hmac
import secrets

ITERATIONS = 310_000


def validate_password(password: str) -> str:
    if not 12 <= len(password) <= 128 or password.isspace():
        raise ValueError("Use a password of 12 to 128 characters")
    return password


def hash_password(password: str) -> str:
    validate_password(password)
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$")
        rounds = int(iterations)
        if (
            algorithm != "pbkdf2_sha256"
            or not 100_000 <= rounds <= 1_000_000
            or len(password) > 128
        ):
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), rounds)
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError, AttributeError):
        return False
