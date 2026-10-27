"""Password hashing and JWT access-token utilities."""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "agentops-os"

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128

_password_hasher = PasswordHasher()


class TokenError(Exception):
    """Raised when an access token is invalid or expired."""


def validate_password_strength(password: str) -> None:
    """Enforce the application's password-length policy."""
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must contain between "
            f"{MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters."
        )


def hash_password(password: str) -> str:
    """Return an Argon2id password hash."""
    validate_password_strength(password)
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password without exposing credential-validation errors."""
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    """Check whether a stored hash needs updating."""
    return _password_hasher.check_needs_rehash(password_hash)


def create_access_token(
    *,
    subject: str,
    secret: str,
    expires_in: timedelta,
    role: str | None = None,
    now: datetime | None = None,
) -> str:
    """Create a signed JWT access token."""
    if not subject.strip():
        raise ValueError("Token subject cannot be empty.")

    if expires_in <= timedelta(0):
        raise ValueError("Token lifetime must be positive.")

    if len(secret) < 32:
        raise ValueError("JWT secret must contain at least 32 characters.")

    issued_at = now or datetime.now(UTC)

    if issued_at.tzinfo is None:
        raise ValueError("Token timestamp must be timezone-aware.")

    claims: dict[str, Any] = {
        "sub": subject,
        "iss": JWT_ISSUER,
        "iat": issued_at,
        "exp": issued_at + expires_in,
        "jti": secrets.token_hex(16),
    }

    if role is not None:
        claims["role"] = role

    return jwt.encode(claims, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str, secret: str) -> dict[str, Any]:
    """Validate a JWT and return its claims."""
    try:
        claims: dict[str, Any] = jwt.decode(
            token,
            secret,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            options={
                "require": ["exp", "iat", "sub", "iss", "jti"],
            },
        )
    except jwt.PyJWTError as exc:
        raise TokenError("Invalid or expired access token.") from exc

    if not isinstance(claims.get("sub"), str) or not claims["sub"].strip():
        raise TokenError("Invalid access-token subject.")

    return claims
