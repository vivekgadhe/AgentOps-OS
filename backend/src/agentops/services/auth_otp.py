"""OTP generation, keyed hashing, throttling and persistence helpers."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from agentops.core.config import Settings
from agentops.db.models.auth_action_token import AuthActionToken


def _otp_digest(settings: Settings, *, purpose: str, email: str, otp: str) -> str:
    pepper = (
        settings.otp_pepper.get_secret_value()
        if settings.otp_pepper is not None
        else settings.jwt_secret.get_secret_value()
    )
    payload = f"agentops-otp:v1:{purpose}:{email}:{otp}".encode()
    return hmac.new(pepper.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def issue_otp(
    db: Session,
    settings: Settings,
    *,
    purpose: str,
    email: str,
    role: str | None = None,
    created_by_user_id: UUID | None = None,
) -> tuple[str, datetime]:
    """Issue a six-digit OTP, enforcing resend and hourly request limits."""
    now = datetime.now(UTC)
    recent = db.scalar(
        select(AuthActionToken.id)
        .where(
            AuthActionToken.purpose == purpose,
            AuthActionToken.email == email,
            AuthActionToken.created_at
            >= now - timedelta(seconds=settings.otp_resend_cooldown_seconds),
        )
        .limit(1)
    )
    if recent is not None:
        raise HTTPException(status_code=429, detail="Please wait before requesting another code.")

    request_count = (
        db.scalar(
            select(func.count())
            .select_from(AuthActionToken)
            .where(
                AuthActionToken.purpose == purpose,
                AuthActionToken.email == email,
                AuthActionToken.created_at >= now - timedelta(hours=1),
            )
        )
        or 0
    )
    if request_count >= settings.otp_max_requests_per_hour:
        raise HTTPException(status_code=429, detail="Too many code requests. Try again later.")

    db.execute(
        update(AuthActionToken)
        .where(
            AuthActionToken.purpose == purpose,
            AuthActionToken.email == email,
            AuthActionToken.consumed_at.is_(None),
            AuthActionToken.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )
    otp = ""
    digest = ""
    for _ in range(10):
        candidate = f"{secrets.randbelow(1_000_000):06d}"
        candidate_digest = _otp_digest(settings, purpose=purpose, email=email, otp=candidate)
        if (
            db.scalar(
                select(AuthActionToken.id).where(AuthActionToken.token_hash == candidate_digest)
            )
            is None
        ):
            otp, digest = candidate, candidate_digest
            break
    if not otp:
        raise HTTPException(status_code=503, detail="Unable to issue a verification code.")

    expires_at = now + timedelta(minutes=settings.otp_expiry_minutes)
    db.add(
        AuthActionToken(
            purpose=purpose,
            email=email,
            role=role,
            token_hash=digest,
            created_by_user_id=created_by_user_id,
            expires_at=expires_at,
            attempts=0,
            max_attempts=settings.otp_max_attempts,
        )
    )
    db.flush()
    return otp, expires_at


def consume_otp(
    db: Session,
    settings: Settings,
    *,
    purpose: str | tuple[str, ...],
    email: str,
    otp: str,
) -> AuthActionToken:
    """Consume a matching OTP, counting failures under row locks.

    Registration accepts both the new public-registration purpose and the
    legacy administrator-invitation purpose. Other callers pass one purpose.
    """
    now = datetime.now(UTC)
    purposes = (purpose,) if isinstance(purpose, str) else purpose
    records = list(
        db.scalars(
            select(AuthActionToken)
            .where(
                AuthActionToken.purpose.in_(purposes),
                AuthActionToken.email == email,
                AuthActionToken.consumed_at.is_(None),
                AuthActionToken.revoked_at.is_(None),
                AuthActionToken.expires_at > now,
            )
            .order_by(AuthActionToken.created_at.desc())
            .with_for_update()
        ).all()
    )
    if not records:
        raise HTTPException(status_code=400, detail="The code is invalid or expired.")

    for record in records:
        expected = _otp_digest(settings, purpose=record.purpose, email=email, otp=otp)
        if hmac.compare_digest(record.token_hash, expected):
            if record.attempts >= record.max_attempts:
                break
            record.consumed_at = now
            return record

    # Count a failed attempt against the newest outstanding code only.
    record = records[0]
    record.attempts += 1
    if record.attempts >= record.max_attempts:
        record.revoked_at = now
    db.commit()
    raise HTTPException(status_code=400, detail="The code is invalid or expired.")
