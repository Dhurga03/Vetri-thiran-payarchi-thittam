import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "pocketsmart-development-secret-change-this"
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def hash_password(password: str) -> str:
    salt = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    ).hex()

    return f"pbkdf2_sha256${salt}${password_hash}"


def verify_password(
    password: str,
    stored_hash: str
) -> bool:
    try:
        algorithm, salt, expected_hash = (
            stored_hash.split("$", 2)
        )

        if algorithm != "pbkdf2_sha256":
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            200_000,
        ).hex()

        return hmac.compare_digest(
            actual_hash,
            expected_hash,
        )

    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if "sub" not in payload:
            return None

        return payload

    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        TypeError,
        ValueError,
    ):
        return None