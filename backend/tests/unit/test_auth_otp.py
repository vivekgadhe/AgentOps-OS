from agentops.services.auth_otp import _otp_digest


def test_otp_digest_is_bound_to_purpose_and_email(settings):
    first = _otp_digest(settings, purpose="password_reset", email="a@example.com", otp="123456")
    assert first != _otp_digest(settings, purpose="invitation", email="a@example.com", otp="123456")
    assert first != _otp_digest(
        settings, purpose="password_reset", email="b@example.com", otp="123456"
    )
    assert first != _otp_digest(
        settings, purpose="password_reset", email="a@example.com", otp="654321"
    )
    assert len(first) == 64
