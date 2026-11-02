"""Authenticated encryption for provider credentials stored in the database."""

from cryptography.fernet import Fernet, InvalidToken

from agentops.core.config import Settings


class CredentialEncryptionError(RuntimeError):
    """Raised when credential encryption/decryption is not safely configured."""


class CredentialCipher:
    """Encrypt provider API keys with a deployment-managed Fernet key."""

    def __init__(self, settings: Settings) -> None:
        configured_key = settings.ai_credential_encryption_key
        if configured_key is None or not configured_key.get_secret_value().strip():
            raise CredentialEncryptionError(
                "AI_CREDENTIAL_ENCRYPTION_KEY must be configured before "
                "storing hosted provider keys."
            )
        try:
            self._fernet = Fernet(configured_key.get_secret_value().encode("ascii"))
        except (ValueError, UnicodeEncodeError) as exc:
            raise CredentialEncryptionError(
                "AI_CREDENTIAL_ENCRYPTION_KEY must be a valid Fernet key."
            ) from exc

    def encrypt(self, plaintext: str) -> str:
        if not plaintext.strip():
            raise ValueError("Provider API key cannot be blank.")
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("ascii")

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode("ascii")).decode("utf-8")
        except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError) as exc:
            raise CredentialEncryptionError(
                "Stored provider credentials cannot be decrypted with the configured key."
            ) from exc
