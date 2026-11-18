"""Authentication, self-service email registration, invitations and password recovery."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from agentops.api.deps import get_current_user, get_db
from agentops.core.config import Settings
from agentops.core.security import create_access_token, hash_password, verify_password
from agentops.db.models.auth_action_token import AuthActionToken
from agentops.db.models.user import User
from agentops.schemas.auth import (
    InvitationCreateRequest,
    InvitationCreateResponse,
    LoginRequest,
    MessageResponse,
    PasswordResetIssueRequest,
    PasswordResetIssueResponse,
    PasswordResetRequest,
    PasswordResetStartRequest,
    RegistrationRequest,
    RegistrationStartRequest,
    TokenResponse,
    UserResponse,
)
from agentops.services.auth_otp import consume_otp, issue_otp
from agentops.services.email import EmailDeliveryError, send_authentication_otp

router = APIRouter(prefix="/auth", tags=["authentication"])


def _require_admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="An active administrator account is required.")


def _send_otp_or_revoke(
    db: Session, settings: Settings, *, email: str, otp: str, purpose: str
) -> None:
    try:
        send_authentication_otp(
            settings,
            recipient=email,
            otp=otp,
            purpose=purpose,
            expires_minutes=settings.otp_expiry_minutes,
        )
    except EmailDeliveryError as exc:
        db.execute(
            update(AuthActionToken)
            .where(
                AuthActionToken.purpose == purpose,
                AuthActionToken.email == email,
                AuthActionToken.consumed_at.is_(None),
                AuthActionToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        db.commit()
        raise HTTPException(
            status_code=503, detail="Email delivery is temporarily unavailable."
        ) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if (
        user is None
        or not verify_password(payload.password, user.password_hash)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings: Settings = request.app.state.settings
    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
        secret=settings.jwt_secret.get_secret_value(),
        expires_in=timedelta(minutes=settings.access_token_ttl_minutes),
    )
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(user)


@router.post("/register/request", response_model=MessageResponse)
def request_registration_code(
    payload: RegistrationStartRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Send an email OTP for public self-service registration.

    This endpoint explicitly reports an existing account so the registration
    page can guide the user to sign in or recover their password. This reveals
    account existence; see the Phase 1 audit notes for that product/security
    trade-off.
    """
    email = str(payload.email).strip().lower()
    settings: Settings = request.app.state.settings

    existing = db.scalar(select(User.id).where(User.email == email))
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "An account already exists for this email. Please sign in or "
                "use Forgot password if you cannot access your account."
            ),
        )

    if not settings.smtp_host or not settings.smtp_from_email:
        raise HTTPException(status_code=503, detail="SMTP email delivery is not configured.")

    # Do not hide rate-limit errors behind a success response. The frontend must
    # remain on the email step when no new verification email was sent.
    otp, _ = issue_otp(db, settings, purpose="registration", email=email)
    db.commit()
    _send_otp_or_revoke(db, settings, email=email, otp=otp, purpose="registration")
    return MessageResponse(
        message=(
            f"A six-digit verification code has been sent to your email address. "
            f"It expires in {settings.otp_expiry_minutes} minutes."
        )
    )


@router.post("/invitations", response_model=InvitationCreateResponse, status_code=201)
def create_invitation(
    payload: InvitationCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user),
) -> InvitationCreateResponse:
    """Optional administrator invitation flow retained for managed workspaces."""
    _require_admin(admin)
    email = str(payload.email).strip().lower()
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(status_code=409, detail="An account already exists for this email.")
    settings: Settings = request.app.state.settings
    if not settings.smtp_host or not settings.smtp_from_email:
        raise HTTPException(status_code=503, detail="SMTP email delivery is not configured.")
    otp, expires_at = issue_otp(
        db,
        settings,
        purpose="invitation",
        email=email,
        role=payload.role,
        created_by_user_id=admin.id,
    )
    db.commit()
    _send_otp_or_revoke(db, settings, email=email, otp=otp, purpose="invitation")
    return InvitationCreateResponse(
        message=(
            "A six-digit invitation verification code has been sent to the supplied email address."
        ),
        email=email,
        expires_at=expires_at,
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    payload: RegistrationRequest, request: Request, db: Session = Depends(get_db)
) -> TokenResponse:
    """Create a default operator account after verifying an email OTP.

    New self-service registrations use the ``registration`` OTP purpose. For
    backward compatibility, administrator-issued ``invitation`` OTPs are also
    accepted; their configured role is preserved.
    """
    email = str(payload.email).strip().lower()
    now = datetime.now(UTC)
    settings: Settings = request.app.state.settings
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "An account already exists for this email. Please sign in or "
                "use Forgot password if you cannot access your account."
            ),
        )

    verified_token = consume_otp(
        db,
        settings,
        purpose=("registration", "invitation"),
        email=email,
        otp=payload.otp,
    )
    role = verified_token.role if verified_token.purpose == "invitation" else "operator"
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role=role or "operator",
        is_active=True,
    )
    db.add(user)
    try:
        db.flush()
        access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
            secret=settings.jwt_secret.get_secret_value(),
            expires_in=timedelta(minutes=settings.access_token_ttl_minutes),
        )
        db.execute(
            update(AuthActionToken)
            .where(
                AuthActionToken.email == email,
                AuthActionToken.purpose.in_(("registration", "invitation")),
                AuthActionToken.id != verified_token.id,
                AuthActionToken.consumed_at.is_(None),
                AuthActionToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "An account already exists for this email. Please sign in or "
                "use Forgot password if you cannot access your account."
            ),
        ) from None
    return TokenResponse(access_token=access_token)


@router.post("/password-reset/request", response_model=MessageResponse)
def request_password_reset(
    payload: PasswordResetStartRequest, request: Request, db: Session = Depends(get_db)
) -> MessageResponse:
    """Send an OTP when the account exists, with a non-enumerating response."""
    email = str(payload.email).strip().lower()
    settings: Settings = request.app.state.settings
    generic = "If an active account exists for that email, a password reset code has been sent."
    if not settings.smtp_host or not settings.smtp_from_email:
        raise HTTPException(status_code=503, detail="SMTP email delivery is not configured.")
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    if user is None:
        return MessageResponse(message=generic)
    try:
        otp, _ = issue_otp(db, settings, purpose="password_reset", email=email)
    except HTTPException as exc:
        if exc.status_code == 429:
            return MessageResponse(message=generic)
        raise
    db.commit()
    _send_otp_or_revoke(db, settings, email=email, otp=otp, purpose="password_reset")
    return MessageResponse(message=generic)


@router.post("/password-reset/issue", response_model=PasswordResetIssueResponse)
def issue_password_reset(
    payload: PasswordResetIssueRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user),
) -> PasswordResetIssueResponse:
    """Administrator-triggered resend using the same email OTP workflow."""
    _require_admin(admin)
    email = str(payload.email).strip().lower()
    settings: Settings = request.app.state.settings
    if not settings.smtp_host or not settings.smtp_from_email:
        raise HTTPException(status_code=503, detail="SMTP email delivery is not configured.")
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    if user is not None:
        otp, _ = issue_otp(
            db,
            settings,
            purpose="password_reset",
            email=email,
            created_by_user_id=admin.id,
        )
        db.commit()
        _send_otp_or_revoke(db, settings, email=email, otp=otp, purpose="password_reset")
    return PasswordResetIssueResponse(
        message="If an active account exists, a reset code has been sent."
    )


@router.post("/password-reset", response_model=MessageResponse)
def reset_password(
    payload: PasswordResetRequest, request: Request, db: Session = Depends(get_db)
) -> MessageResponse:
    email = str(payload.email).strip().lower()
    settings: Settings = request.app.state.settings
    reset_record = consume_otp(
        db, settings, purpose="password_reset", email=email, otp=payload.token
    )
    user = db.scalar(
        select(User).where(User.email == email, User.is_active.is_(True)).with_for_update()
    )
    if user is None:
        db.rollback()
        raise HTTPException(status_code=400, detail="The code is invalid or expired.")
    user.password_hash = hash_password(payload.new_password)
    db.execute(
        update(AuthActionToken)
        .where(
            AuthActionToken.purpose == "password_reset",
            AuthActionToken.email == email,
            AuthActionToken.id != reset_record.id,
            AuthActionToken.consumed_at.is_(None),
            AuthActionToken.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )
    db.commit()
    return MessageResponse(message="Password updated. You can now sign in with your new password.")
