"""PostgreSQL integration tests for self-service registration and password recovery OTPs."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from agentops.core.security import hash_password
from agentops.db.models.auth_action_token import AuthActionToken
from agentops.db.models.user import User
from agentops.db.session import create_db_engine
from agentops.main import create_app

pytestmark = pytest.mark.integration


@pytest.fixture
def auth_flow_context(integration_settings, monkeypatch):
    from agentops.api.v1 import auth as auth_api
    from agentops.services import auth_otp

    monkeypatch.setattr(auth_api, "send_authentication_otp", lambda *args, **kwargs: None)
    monkeypatch.setattr(auth_otp.secrets, "randbelow", lambda _limit: 123456)
    test_settings = integration_settings.model_copy(
        update={"smtp_host": "smtp.test", "smtp_from_email": "noreply@example.com"}
    )
    engine = create_db_engine(test_settings)
    suffix = uuid4().hex
    admin_email = f"auth-admin-{suffix}@example.com"
    invitee_email = f"auth-invitee-{suffix}@example.com"
    admin_password = "Auth-Admin-Password-123!"
    with Session(engine) as session:
        admin = User(
            email=admin_email,
            password_hash=hash_password(admin_password),
            role="admin",
            is_active=True,
        )
        session.add(admin)
        session.commit()
        admin_id = admin.id
    try:
        with TestClient(create_app(test_settings)) as client:
            yield {
                "client": client,
                "engine": engine,
                "admin_email": admin_email,
                "admin_password": admin_password,
                "admin_id": admin_id,
                "invitee_email": invitee_email,
            }
    finally:
        with Session(engine) as session:
            session.execute(
                delete(AuthActionToken).where(
                    AuthActionToken.email.in_((admin_email, invitee_email))
                )
            )
            session.execute(delete(User).where(User.email.in_((admin_email, invitee_email))))
            session.commit()
        engine.dispose()


def _admin_headers(context):
    response = context["client"].post(
        "/api/v1/auth/login",
        json={"email": context["admin_email"], "password": context["admin_password"]},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _latest_otp(context, email: str, purpose: str) -> str:
    from agentops.services.auth_otp import _otp_digest

    otp = "123456"
    settings = context["client"].app.state.settings
    with Session(context["engine"]) as session:
        record = session.scalar(
            select(AuthActionToken)
            .where(AuthActionToken.email == email, AuthActionToken.purpose == purpose)
            .order_by(AuthActionToken.created_at.desc())
        )
        assert record is not None
        record.token_hash = _otp_digest(settings, purpose=purpose, email=email, otp=otp)
        session.commit()
    return otp


def test_public_registration_sends_otp_and_creates_operator_session(auth_flow_context):
    context = auth_flow_context
    client = context["client"]
    request_code = client.post(
        "/api/v1/auth/register/request", json={"email": context["invitee_email"]}
    )
    assert request_code.status_code == 200
    assert "verification code" in request_code.json()["message"].lower()

    otp = _latest_otp(context, context["invitee_email"], "registration")
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "email": context["invitee_email"],
            "otp": otp,
            "password": "New-Operator-Password-123!",
        },
    )
    assert registration.status_code == 201
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {registration.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["role"] == "operator"
    assert me.json()["email"] == context["invitee_email"]

    replay = client.post(
        "/api/v1/auth/register",
        json={
            "email": context["invitee_email"],
            "otp": otp,
            "password": "Another-Password-123!",
        },
    )
    assert replay.status_code == 409


def test_registered_email_registration_request_returns_conflict(auth_flow_context):
    context = auth_flow_context
    with Session(context["engine"]) as session:
        session.add(
            User(
                email=context["invitee_email"],
                password_hash=hash_password("Existing-Password-123!"),
                role="operator",
                is_active=True,
            )
        )
        session.commit()
    response = context["client"].post(
        "/api/v1/auth/register/request", json={"email": context["invitee_email"]}
    )
    assert response.status_code == 409
    assert "account already exists" in response.json()["detail"].lower()
    with Session(context["engine"]) as session:
        record = session.scalar(
            select(AuthActionToken).where(
                AuthActionToken.email == context["invitee_email"],
                AuthActionToken.purpose == "registration",
            )
        )
        assert record is None


def test_public_registration_request_returns_429_during_resend_cooldown(auth_flow_context):
    context = auth_flow_context
    client = context["client"]
    email = context["invitee_email"]

    first_request = client.post("/api/v1/auth/register/request", json={"email": email})
    assert first_request.status_code == 200

    second_request = client.post("/api/v1/auth/register/request", json={"email": email})
    assert second_request.status_code == 429
    assert "wait" in second_request.json()["detail"].lower()


def test_legacy_admin_invitation_still_registers_with_assigned_role(auth_flow_context):
    context = auth_flow_context
    client = context["client"]
    invite = client.post(
        "/api/v1/auth/invitations",
        headers=_admin_headers(context),
        json={"email": context["invitee_email"], "role": "viewer"},
    )
    assert invite.status_code == 201
    otp = _latest_otp(context, context["invitee_email"], "invitation")
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "email": context["invitee_email"],
            "invitation_token": otp,
            "password": "New-Viewer-Password-123!",
        },
    )
    assert registration.status_code == 201
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {registration.json()['access_token']}"},
    )
    assert me.status_code == 200 and me.json()["role"] == "viewer"


def test_password_reset_email_otp_is_single_use(auth_flow_context):
    context = auth_flow_context
    client = context["client"]
    with Session(context["engine"]) as session:
        session.add(
            User(
                email=context["invitee_email"],
                password_hash=hash_password("Old-Password-123!"),
                role="viewer",
                is_active=True,
            )
        )
        session.commit()
    start = client.post(
        "/api/v1/auth/password-reset/request", json={"email": context["invitee_email"]}
    )
    assert start.status_code == 200
    otp = _latest_otp(context, context["invitee_email"], "password_reset")
    reset = client.post(
        "/api/v1/auth/password-reset",
        json={
            "email": context["invitee_email"],
            "token": otp,
            "new_password": "New-Password-123!",
        },
    )
    assert reset.status_code == 200
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": context["invitee_email"], "password": "New-Password-123!"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/auth/password-reset",
            json={
                "email": context["invitee_email"],
                "token": otp,
                "new_password": "Third-Password-123!",
            },
        ).status_code
        == 400
    )


def test_unknown_password_reset_email_returns_generic_response(auth_flow_context):
    response = auth_flow_context["client"].post(
        "/api/v1/auth/password-reset/request", json={"email": "unknown@example.com"}
    )
    assert response.status_code == 200
    assert "If an active account exists" in response.json()["message"]


def test_invalid_otp_attempts_are_counted_and_code_is_revoked(auth_flow_context):
    context = auth_flow_context
    client = context["client"]
    with Session(context["engine"]) as session:
        session.add(
            User(
                email=context["invitee_email"],
                password_hash=hash_password("Old-Password-123!"),
                role="viewer",
                is_active=True,
            )
        )
        session.commit()
    assert (
        client.post(
            "/api/v1/auth/password-reset/request", json={"email": context["invitee_email"]}
        ).status_code
        == 200
    )
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/password-reset",
            json={
                "email": context["invitee_email"],
                "token": "000000",
                "new_password": "New-Password-123!",
            },
        )
        assert response.status_code == 400
    with Session(context["engine"]) as session:
        record = session.scalar(
            select(AuthActionToken).where(
                AuthActionToken.email == context["invitee_email"],
                AuthActionToken.purpose == "password_reset",
            )
        )
        assert record is not None and record.attempts == 5 and record.revoked_at is not None
