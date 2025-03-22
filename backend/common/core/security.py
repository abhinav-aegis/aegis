from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import re
import bcrypt
import jwt
from cryptography.fernet import Fernet
import hashlib
from fastapi.security import HTTPBearer

from backend.common.core.config import settings

fernet = Fernet(str.encode(settings.ENCRYPT_KEY))

JWT_ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}

    return jwt.encode(
        payload=to_encode,
        key=settings.ENCRYPT_KEY,
        algorithm=JWT_ALGORITHM,
    )


def create_refresh_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc)  + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}

    return jwt.encode(
        payload=to_encode,
        key=settings.ENCRYPT_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        jwt=token,
        key=settings.ENCRYPT_KEY,
        algorithms=[JWT_ALGORITHM],
    )


def verify_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()

    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(plain_password: str | bytes) -> str:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()

    return bcrypt.hashpw(plain_password, bcrypt.gensalt()).decode()


def get_data_encrypt(data) -> str:
    data = fernet.encrypt(data)
    return data.decode()


def get_content(variable: str) -> str:
    return fernet.decrypt(variable.encode()).decode()

def hash_secret_sha256(secret: str) -> str:
    """
    Hash a secret using SHA256 in a deterministic manner.

    This function produces a fixed-length, irreversible hash using the SHA256 algorithm.
    It is suitable for use cases where:
      - The secret is a long, randomly generated string (e.g., API keys).
      - Deterministic lookup is required (i.e., you need to compare the hash later).
      - You want to index and search on the hashed value in a database.

    !!! SECURITY WARNING !!!
    SHA256 is a fast, deterministic hash. It should only be used for secrets that are:
      - Cryptographically strong (e.g., 32+ bytes of randomness).
      - Never user-generated (i.e., not passwords).
      - Used internally in trusted environments (e.g., service-to-service API keys).

    For hashing passwords or user-facing secrets, use a slow hashing algorithm like bcrypt or Argon2
    to protect against brute-force attacks.

    Args:
        secret (str): The secret or API key to hash.

    Returns:
        str: A SHA256 hash of the input secret.
    """
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()

http_bearer_scheme = HTTPBearer(auto_error=False)


ALLOWED_CHARS_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{20,}$")

def validate_api_key_format(raw_key: str, valid_prefixes: list[str]) -> None:
    if not any(raw_key.startswith(prefix) for prefix in valid_prefixes):
        raise ValueError(f"API key must start with one of: {', '.join(valid_prefixes)}")

    key_without_prefix = raw_key.split("_", 1)[-1]

    if len(key_without_prefix) < 20:
        raise ValueError("API key is too short. Must be at least 20 characters after the prefix.")

    if not ALLOWED_CHARS_PATTERN.match(key_without_prefix):
        raise ValueError("API key contains invalid characters. Only URL-safe characters are allowed.")

def get_key_preview(secret: str, prefix_len: int = 6, suffix_len: int = 4) -> str:
    if len(secret) <= prefix_len + suffix_len:
        return secret
    return f"{secret[:prefix_len]}...{secret[-suffix_len:]}"
