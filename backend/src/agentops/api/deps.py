"""Reusable FastAPI dependencies."""

from collections.abc import Generator
from typing import cast
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from agentops.core.config import Settings
from agentops.core.security import TokenError, decode_access_token
from agentops.db.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_engine(request: Request) -> Engine:
    """Retrieve the SQLAlchemy engine from application state."""
    return cast(Engine, request.app.state.engine)


def get_db(request: Request) -> Generator[Session, None, None]:
    """Provide a database session for one request."""
    with Session(get_engine(request)) as session:
        yield session


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated, active user from the database."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings: Settings = request.app.state.settings

    try:
        claims = decode_access_token(
            credentials.credentials,
            settings.jwt_secret.get_secret_value(),
        )
        user_id = UUID(claims["sub"])
    except (TokenError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = db.scalar(select(User).where(User.id == user_id))

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
