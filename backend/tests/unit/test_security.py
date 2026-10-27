from datetime import UTC, datetime, timedelta

import pytest

from agentops.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    password_needs_rehash,
    verify_password,
)

TEST_SECRET = "test-secret-for-agentops-security-0123456789"
TEST_PASSWORD = "correct horse battery"


def test_password_hash_and_verification() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert password_hash.startswith("$argon2id$")
    assert TEST_PASSWORD not in password_hash
    assert verify_password(TEST_PASSWORD, password_hash)
    assert not verify_password("incorrect password", password_hash)


def test_same_password_produces_different_hashes() -> None:
    assert hash_password(TEST_PASSWORD) != hash_password(TEST_PASSWORD)


def test_invalid_password_lengths_are_rejected() -> None:
    for password in ("", "short", "x" * 129):
        with pytest.raises(ValueError):
            hash_password(password)


def test_invalid_hash_does_not_raise() -> None:
    assert not verify_password(TEST_PASSWORD, "not-a-valid-hash")


def test_new_password_hash_does_not_need_rehash() -> None:
    assert not password_needs_rehash(hash_password(TEST_PASSWORD))


def test_access_token_round_trip() -> None:
    token = create_access_token(
        subject="user-123",
        role="operator",
        secret=TEST_SECRET,
        expires_in=timedelta(minutes=15),
    )

    claims = decode_access_token(token, TEST_SECRET)

    assert claims["sub"] == "user-123"
    assert claims["role"] == "operator"
    assert claims["iss"] == "agentops-os"


def test_expired_token_is_rejected() -> None:
    token = create_access_token(
        subject="user-123",
        secret=TEST_SECRET,
        expires_in=timedelta(minutes=5),
        now=datetime.now(UTC) - timedelta(hours=1),
    )

    with pytest.raises(TokenError):
        decode_access_token(token, TEST_SECRET)


def test_wrong_secret_is_rejected() -> None:
    token = create_access_token(
        subject="user-123",
        secret=TEST_SECRET,
        expires_in=timedelta(minutes=5),
    )

    with pytest.raises(TokenError):
        decode_access_token(
            token,
            "another-test-secret-for-agentops-0123456789",
        )


def test_empty_subject_is_rejected() -> None:
    with pytest.raises(ValueError):
        create_access_token(
            subject=" ",
            secret=TEST_SECRET,
            expires_in=timedelta(minutes=5),
        )
