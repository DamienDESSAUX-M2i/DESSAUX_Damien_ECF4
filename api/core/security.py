import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from api.core.settings import get_settings


def hash_password(password: str) -> str:
    settings = get_settings()

    iterations = settings.iterations
    salt = os.urandom(16).hex()

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()

    return f"pbkdf2_sha256${iterations}${salt}${password_hash}"


def verify_password(password: str, stored_value: str) -> bool:
    try:
        algorithm_name, iterations_str, salt, stored_hash = stored_value.split("$")

        if algorithm_name != "pbkdf2_sha256":
            return False

        computed_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations_str),
        ).hex()

        return hmac.compare_digest(computed_hash, stored_hash)

    except (ValueError, TypeError):
        return False


def create_access_token(
    data: Dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    settings = get_settings()

    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )

    to_encode = data.copy()
    to_encode.update(
        {
            "exp": expire,
            "iat": now,
        }
    )

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    settings = get_settings()

    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
