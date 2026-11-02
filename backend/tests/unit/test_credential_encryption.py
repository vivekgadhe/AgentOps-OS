"""Credential encryption uses authenticated encryption and never stores plaintext."""

import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr

from agentops.core.config import Settings
from agentops.core.encryption import CredentialCipher, CredentialEncryptionError


def test_credential_cipher_round_trips_without_plaintext_storage() -> None:
    key = Fernet.generate_key().decode("ascii")
    settings = Settings(
        _env_file=None,
        ai_credential_encryption_key=SecretStr(key),
    )
    cipher = CredentialCipher(settings)

    encrypted = cipher.encrypt("test-provider-secret")

    assert encrypted != "test-provider-secret"
    assert "test-provider-secret" not in encrypted
    assert cipher.decrypt(encrypted) == "test-provider-secret"


def test_credential_cipher_requires_a_configured_key() -> None:
    settings = Settings(_env_file=None)
    with pytest.raises(CredentialEncryptionError, match="must be configured"):
        CredentialCipher(settings)


def test_credential_cipher_rejects_invalid_key() -> None:
    settings = Settings(
        _env_file=None,
        ai_credential_encryption_key=SecretStr("not-a-valid-fernet-key"),
    )
    with pytest.raises(CredentialEncryptionError, match="valid Fernet key"):
        CredentialCipher(settings)
