"""Authenticated per-user AI provider configuration and health checks."""

from typing import cast
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentops.api.deps import get_current_user, get_db
from agentops.core.config import Settings
from agentops.core.encryption import CredentialCipher, CredentialEncryptionError
from agentops.db.models.ai_provider import AIProviderConfig
from agentops.db.models.user import User
from agentops.schemas.ai_providers import (
    AIProviderName,
    AIProviderResponse,
    AIProviderTestResponse,
    AIProviderUpsert,
)
from agentops.services.providers.base import ProviderError
from agentops.services.providers.provider_manager import build_provider_manager

router = APIRouter(prefix="/ai-providers", tags=["AI providers"])


class _ProviderHealthOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ok: bool = Field(description="Must be true when provider generation works.")
    provider: str


def _settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def _require_provider_admin(user: User) -> None:
    if user.role not in {"admin", "operator"}:
        raise HTTPException(status_code=403, detail="An admin or operator role is required.")


def _response(row: AIProviderConfig) -> AIProviderResponse:
    return AIProviderResponse(
        id=str(row.id),
        provider=AIProviderName(row.provider),
        model_name=row.model_name,
        api_key_configured=bool(row.api_key_ciphertext),
        base_url=row.base_url,
        priority=row.priority,
        enabled=row.enabled,
    )


def _validate_ollama_url(value: str | None) -> str | None:
    if value is None:
        return None
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    allowed_hosts = {"localhost", "127.0.0.1", "::1", "host.docker.internal"}
    if (
        parsed.scheme not in {"http", "https"}
        or host not in allowed_hosts
        or parsed.username is not None
        or parsed.password is not None
        or bool(parsed.query)
        or bool(parsed.fragment)
    ):
        raise HTTPException(
            status_code=422,
            detail="Ollama base URL must target localhost or host.docker.internal.",
        )
    return value


@router.get("", response_model=list[AIProviderResponse])
def list_ai_providers(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[AIProviderResponse]:
    """List the authenticated user's provider settings without exposing secrets."""
    rows = db.scalars(
        select(AIProviderConfig)
        .where(AIProviderConfig.owner_user_id == user.id)
        .order_by(AIProviderConfig.priority, AIProviderConfig.provider)
    ).all()
    return [_response(row) for row in rows]


@router.put("/{provider_name}", response_model=AIProviderResponse)
def upsert_ai_provider(
    provider_name: AIProviderName,
    payload: AIProviderUpsert,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AIProviderResponse:
    """Create or update one provider; API keys are encrypted before persistence."""
    _require_provider_admin(user)
    settings = _settings(request)
    base_url = payload.base_url
    if provider_name == AIProviderName.OLLAMA:
        base_url = _validate_ollama_url(base_url) or settings.ollama_base_url
    elif base_url is not None:
        raise HTTPException(
            status_code=422,
            detail="Custom base URLs are only supported for Ollama.",
        )

    row = db.scalar(
        select(AIProviderConfig)
        .where(
            AIProviderConfig.owner_user_id == user.id,
            AIProviderConfig.provider == provider_name.value,
        )
        .with_for_update()
    )

    encrypted_key: str | None = row.api_key_ciphertext if row is not None else None
    if provider_name != AIProviderName.OLLAMA:
        if payload.api_key is not None:
            try:
                encrypted_key = CredentialCipher(settings).encrypt(
                    payload.api_key.get_secret_value().strip()
                )
            except (CredentialEncryptionError, ValueError) as exc:
                raise HTTPException(status_code=503, detail=str(exc)) from exc
        if encrypted_key is None:
            raise HTTPException(
                status_code=422,
                detail="An API key is required when configuring OpenAI or Groq.",
            )
    else:
        encrypted_key = None

    if row is None:
        row = AIProviderConfig(
            owner_user_id=user.id,
            provider=provider_name.value,
            model_name=payload.model_name,
            api_key_ciphertext=encrypted_key,
            base_url=base_url,
            priority=payload.priority,
            enabled=payload.enabled,
        )
        db.add(row)
    else:
        row.model_name = payload.model_name
        row.api_key_ciphertext = encrypted_key
        row.base_url = base_url
        row.priority = payload.priority
        row.enabled = payload.enabled

    db.commit()
    db.refresh(row)
    return _response(row)


@router.delete("/{provider_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_provider(
    provider_name: AIProviderName,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    _require_provider_admin(user)
    row = db.scalar(
        select(AIProviderConfig).where(
            AIProviderConfig.owner_user_id == user.id,
            AIProviderConfig.provider == provider_name.value,
        )
    )
    if row is not None:
        db.delete(row)
        db.commit()


@router.post("/test", response_model=AIProviderTestResponse)
def test_ai_provider(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AIProviderTestResponse:
    """Exercise the configured fallback chain with a tiny validated response."""
    _require_provider_admin(user)
    settings = _settings(request)
    try:
        with build_provider_manager(db, user.id, settings) as manager:
            result = manager.generate_structured(
                "Return ok=true and provider='configured-provider'.",
                output_model=_ProviderHealthOutput,
                instructions="Return only the requested structured health response.",
            )
            provider = manager.last_provider or "unknown"
            model_name = manager.last_model or settings.ollama_chat_model
            return AIProviderTestResponse(
                provider=AIProviderName(provider),
                model_name=model_name,
                success=result.ok,
                message=(
                    "Provider generated a valid structured response."
                    if result.ok
                    else "Provider returned an invalid health response."
                ),
            )
    except (ProviderError, CredentialEncryptionError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail="No configured AI provider completed the health check.",
        ) from exc
