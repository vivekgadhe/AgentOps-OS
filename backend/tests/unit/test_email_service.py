from unittest.mock import MagicMock, patch

from pydantic import SecretStr

from agentops.services.email import send_authentication_otp


def _smtp_settings(settings):
    return settings.model_copy(
        update={
            "smtp_host": "smtp.example.test",
            "smtp_port": 587,
            "smtp_username": "sender@example.test",
            "smtp_password": SecretStr("test-app-password"),
            "smtp_from_email": "sender@example.test",
            "smtp_from_name": "AgentOps-OS",
            "smtp_starttls": True,
        }
    )


def test_smtp_email_contains_otp_and_uses_starttls(settings):
    smtp = MagicMock()
    with patch("agentops.services.email.smtplib.SMTP") as smtp_factory:
        smtp_factory.return_value.__enter__.return_value = smtp
        send_authentication_otp(
            _smtp_settings(settings),
            recipient="user@example.test",
            otp="123456",
            purpose="password_reset",
            expires_minutes=10,
        )
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once_with("sender@example.test", "test-app-password")
    sent = smtp.send_message.call_args.args[0]
    assert sent["To"] == "user@example.test"
    assert "123456" in sent.get_body(preferencelist=("plain",)).get_content()


def test_registration_email_uses_account_verification_copy(settings):
    smtp = MagicMock()
    with patch("agentops.services.email.smtplib.SMTP") as smtp_factory:
        smtp_factory.return_value.__enter__.return_value = smtp
        send_authentication_otp(
            _smtp_settings(settings),
            recipient="new-user@example.test",
            otp="654321",
            purpose="registration",
            expires_minutes=10,
        )
    sent = smtp.send_message.call_args.args[0]
    assert "email verification" in sent["Subject"].lower()
    assert "654321" in sent.get_body(preferencelist=("plain",)).get_content()
    assert (
        "creating your AgentOps-OS account"
        in sent.get_body(preferencelist=("plain",)).get_content()
    )
