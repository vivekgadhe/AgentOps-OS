"""Local account provisioning for AgentOps-OS development workspaces.

Run from the backend directory after applying migrations:

    uv run python scripts/manage_users.py list-users
    uv run python scripts/manage_users.py bootstrap-admin --email admin@example.com
    uv run python scripts/manage_users.py create-user --email user@example.com --role operator
    uv run python scripts/manage_users.py reset-password --email admin@example.com
    uv run python scripts/manage_users.py create-invitation --email user@example.com --role operator
    uv run python scripts/manage_users.py issue-password-reset --email user@example.com

Passwords are entered interactively and are never accepted as command-line
arguments. This utility refuses to modify a database configured as APP_ENV=prod.
It is intended for a trusted local developer/operator with direct DB access.
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

# Allow direct execution from a source checkout, including before editable install.
SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from pydantic import EmailStr, TypeAdapter, ValidationError  # noqa: E402
from sqlalchemy import func, select, update  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from agentops.core.config import get_settings  # noqa: E402
from agentops.core.security import (  # noqa: E402
    hash_password,
    validate_password_strength,
)
from agentops.db.models.auth_action_token import AuthActionToken  # noqa: E402
from agentops.db.models.user import User  # noqa: E402
from agentops.services.auth_otp import issue_otp  # noqa: E402
from agentops.services.email import EmailDeliveryError, send_authentication_otp  # noqa: E402
from agentops.db.session import create_db_engine  # noqa: E402

_EMAIL_ADAPTER = TypeAdapter(EmailStr)
_ALLOWED_ROLES = ("admin", "operator", "viewer")


def _normalise_email(value: str) -> str:
    try:
        return str(_EMAIL_ADAPTER.validate_python(value.strip())).lower()
    except ValidationError as exc:
        raise ValueError("Enter a valid email address.") from exc


def _prompt_password() -> str:
    password = getpass.getpass("Password (12–128 characters): ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise ValueError("Passwords do not match.")
    validate_password_strength(password)
    return password


def _open_engine():
    settings = get_settings()
    if settings.app_env == "prod":
        raise ValueError(
            "This local account utility refuses to modify a production database. "
            "Use your approved production account-administration process instead."
        )
    return create_db_engine(settings)


def list_users() -> None:
    engine = _open_engine()
    try:
        with Session(engine) as session:
            users = list(session.scalars(select(User).order_by(User.created_at, User.email)).all())
            if not users:
                print("No AgentOps-OS user accounts exist yet.")
                return
            print(f"{'EMAIL':<40} {'ROLE':<12} {'ACTIVE':<8}")
            print("-" * 62)
            for user in users:
                print(f"{user.email:<40} {user.role:<12} {str(user.is_active):<8}")
    finally:
        engine.dispose()


def bootstrap_admin(email: str) -> None:
    engine = _open_engine()
    try:
        with Session(engine) as session:
            existing_count = int(session.scalar(select(func.count()).select_from(User)) or 0)
            if existing_count:
                raise ValueError(
                    f"The users table already contains {existing_count} account(s). "
                    "First-admin bootstrap is allowed only when the users table is empty. "
                    "Use list-users and then reset-password or create-user as appropriate."
                )
            password = _prompt_password()
            session.add(
                User(
                    email=email,
                    password_hash=hash_password(password),
                    role="admin",
                    is_active=True,
                )
            )
            session.commit()
            print(f"Administrator account created successfully for {email}.")
            print("Sign in to AgentOps-OS with this email and the password you entered.")
    finally:
        engine.dispose()


def create_user(email: str, role: str) -> None:
    if role not in _ALLOWED_ROLES:
        raise ValueError(f"Role must be one of: {', '.join(_ALLOWED_ROLES)}.")
    engine = _open_engine()
    try:
        with Session(engine) as session:
            admin_exists = session.scalar(
                select(User.id).where(User.role == "admin", User.is_active.is_(True)).limit(1)
            )
            if admin_exists is None:
                raise ValueError(
                    "No active administrator exists. Create the first admin with bootstrap-admin."
                )
            existing = session.scalar(select(User.id).where(User.email == email))
            if existing is not None:
                raise ValueError(f"An account already exists for {email}.")
            password = _prompt_password()
            session.add(
                User(
                    email=email,
                    password_hash=hash_password(password),
                    role=role,
                    is_active=True,
                )
            )
            session.commit()
            print(f"{role.capitalize()} account created successfully for {email}.")
    finally:
        engine.dispose()


def reset_password(email: str) -> None:
    engine = _open_engine()
    try:
        with Session(engine) as session:
            user = session.scalar(select(User).where(User.email == email))
            if user is None:
                raise ValueError(f"No account exists for {email}.")
            if not user.is_active:
                raise ValueError(
                    "This account is inactive. Ask an administrator to review its status "
                    "before resetting the password."
                )
            print(f"Account: {user.email} | Role: {user.role} | Active: {user.is_active}")
            expected = f"RESET {email}"
            entered = input(f"Type '{expected}' to confirm the password reset: ").strip()
            if entered != expected:
                raise ValueError("Confirmation did not match. No changes were made.")
            user.password_hash = hash_password(_prompt_password())
            session.commit()
            print(f"Password updated successfully for {email}.")
    finally:
        engine.dispose()


def _active_admin(session: Session) -> User:
    admin = session.scalar(
        select(User)
        .where(User.role == "admin", User.is_active.is_(True))
        .order_by(User.created_at, User.email)
        .limit(1)
    )
    if admin is None:
        raise ValueError("No active administrator exists in this database.")
    return admin


def create_invitation(email: str, role: str) -> None:
    """Issue and email a six-digit invitation OTP."""
    if role not in _ALLOWED_ROLES:
        raise ValueError(f"Role must be one of: {', '.join(_ALLOWED_ROLES)}.")
    engine = _open_engine()
    try:
        settings = get_settings()
        if not settings.smtp_host or not settings.smtp_from_email:
            raise ValueError("Configure SMTP_HOST and SMTP_FROM_EMAIL before sending invitations.")
        with Session(engine) as session:
            admin = _active_admin(session)
            if session.scalar(select(User.id).where(User.email == email)) is not None:
                raise ValueError(f"An account already exists for {email}.")
            otp, _ = issue_otp(
                session, settings, purpose="invitation", email=email, role=role,
                created_by_user_id=admin.id,
            )
            session.commit()
            try:
                send_authentication_otp(
                    settings, recipient=email, otp=otp, purpose="invitation",
                    expires_minutes=settings.otp_expiry_minutes,
                )
            except EmailDeliveryError as exc:
                session.execute(
                    update(AuthActionToken)
                    .where(AuthActionToken.email == email, AuthActionToken.purpose == "invitation", AuthActionToken.consumed_at.is_(None))
                    .values(revoked_at=datetime.now(UTC))
                )
                session.commit()
                raise ValueError(str(exc)) from exc
            print(f"Invitation verification code sent to {email} for role {role}.")
            print(f"The six-digit code expires in {settings.otp_expiry_minutes} minutes.")
    finally:
        engine.dispose()


def issue_password_reset(email: str) -> None:
    """Issue and email a six-digit password-reset OTP."""
    engine = _open_engine()
    try:
        settings = get_settings()
        if not settings.smtp_host or not settings.smtp_from_email:
            raise ValueError("Configure SMTP_HOST and SMTP_FROM_EMAIL before sending reset codes.")
        with Session(engine) as session:
            admin = _active_admin(session)
            user = session.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
            if user is None:
                raise ValueError(f"No active account exists for {email}.")
            otp, _ = issue_otp(
                session, settings, purpose="password_reset", email=email,
                created_by_user_id=admin.id,
            )
            session.commit()
            try:
                send_authentication_otp(
                    settings, recipient=email, otp=otp, purpose="password_reset",
                    expires_minutes=settings.otp_expiry_minutes,
                )
            except EmailDeliveryError as exc:
                session.execute(
                    update(AuthActionToken)
                    .where(AuthActionToken.email == email, AuthActionToken.purpose == "password_reset", AuthActionToken.consumed_at.is_(None))
                    .values(revoked_at=datetime.now(UTC))
                )
                session.commit()
                raise ValueError(str(exc)) from exc
            print(f"Password reset verification code sent to {email}.")
            print(f"The six-digit code expires in {settings.otp_expiry_minutes} minutes.")
    finally:
        engine.dispose()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local AgentOps-OS account provisioning utility."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-users", help="List account email, role and active status.")

    bootstrap = subparsers.add_parser(
        "bootstrap-admin",
        help="Create the first administrator; only works when the users table is empty.",
    )
    bootstrap.add_argument("--email", required=True, help="Administrator email address.")

    create = subparsers.add_parser(
        "create-user", help="Create a user after an active administrator exists."
    )
    create.add_argument("--email", required=True, help="New account email address.")
    create.add_argument("--role", choices=_ALLOWED_ROLES, default="operator")

    invite = subparsers.add_parser(
        "create-invitation",
        help="Create a single-use registration invitation (administrator required).",
    )
    invite.add_argument("--email", required=True, help="Invitee email address.")
    invite.add_argument("--role", choices=_ALLOWED_ROLES, default="operator")

    issue_reset = subparsers.add_parser(
        "issue-password-reset",
        help="Issue a single-use password reset code (administrator required).",
    )
    issue_reset.add_argument("--email", required=True, help="Existing account email address.")

    reset = subparsers.add_parser(
        "reset-password",
        help="Reset an existing active user's password after explicit confirmation.",
    )
    reset.add_argument("--email", required=True, help="Existing account email address.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "list-users":
            list_users()
            return 0
        email = _normalise_email(args.email)
        if args.command == "bootstrap-admin":
            bootstrap_admin(email)
        elif args.command == "create-user":
            create_user(email, args.role)
        elif args.command == "reset-password":
            reset_password(email)
        elif args.command == "create-invitation":
            create_invitation(email, args.role)
        elif args.command == "issue-password-reset":
            issue_password_reset(email)
        else:  # pragma: no cover - argparse enforces the command choices
            raise ValueError("Unsupported command.")
    except ValueError as exc:
        print(f"Account operation failed: {exc}", file=sys.stderr)
        return 1
    except SQLAlchemyError as exc:
        print(
            "Account operation failed because the database could not complete the request "
            f"({type(exc).__name__}). Confirm PostgreSQL is running, migrations are current, "
            "and DATABASE_URL is configured in the backend environment.",
            file=sys.stderr,
        )
        return 1
    except OSError as exc:
        print(f"Account operation failed ({type(exc).__name__}).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
