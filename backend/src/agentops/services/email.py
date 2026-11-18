"""SMTP email delivery for authentication one-time passcodes."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from html import escape

from agentops.core.config import Settings


class EmailDeliveryError(RuntimeError):
    """Raised when the configured SMTP server cannot deliver an email."""


def send_authentication_otp(
    settings: Settings, *, recipient: str, otp: str, purpose: str, expires_minutes: int
) -> None:
    """Send a one-time code without logging or returning the code."""
    if not settings.smtp_host or not settings.smtp_from_email:
        raise EmailDeliveryError("SMTP email delivery is not configured.")

    if purpose == "invitation":
        subject = "Your AgentOps-OS account verification code"
        heading = "Verify your email address"
        explanation = "Use this code to complete your invited AgentOps-OS account registration."
    elif purpose == "registration":
        subject = "Your AgentOps-OS email verification code"
        heading = "Verify your email address"
        explanation = "Use this code to finish creating your AgentOps-OS account."
    elif purpose == "password_reset":
        subject = "Your AgentOps-OS password reset code"
        heading = "Reset your password"
        explanation = "Use this code to continue resetting your AgentOps-OS password."
    else:
        raise EmailDeliveryError("Unsupported authentication email purpose.")

    safe_heading = escape(heading)
    safe_explanation = escape(explanation)
    safe_name = escape(settings.smtp_from_name)
    text_body = (
        f"{heading}\n\n{explanation}\n\n"
        f"Your one-time verification code is: {otp}\n\n"
        f"This code expires in {expires_minutes} minutes and can only be used once. "
        "Do not share this code with anyone. If you did not request it, ignore this email.\n\n"
        f"{settings.smtp_from_name} Security Team"
    )
    html_body = (
        "<!doctype html><html><body "
        'style="margin:0;background:#f3f5fb;padding:32px;'
        'font-family:Arial,sans-serif;color:#17233d">'
        '<table role="presentation" '
        'style="max-width:560px;margin:auto;background:#fff;'
        'border-radius:16px;padding:36px;width:100%"><tr><td>'
        '<div style="font-size:13px;font-weight:700;letter-spacing:2px;'
        'color:#6745ed">AGENTOPS-OS</div>'
        f'<h1 style="font-size:25px;margin:24px 0 12px">{safe_heading}</h1>'
        '<p style="font-size:15px;line-height:1.6;color:#596780">'
        f"{safe_explanation}</p>"
        '<div style="margin:28px 0;padding:20px;text-align:center;'
        "background:#f2efff;border-radius:12px;font-size:32px;"
        'font-weight:700;letter-spacing:9px;color:#5735df">'
        f"{otp}</div>"
        '<p style="font-size:14px;line-height:1.6;color:#596780">'
        f"This code expires in <strong>{expires_minutes} minutes</strong>, "
        "can only be used once, and must not be shared.</p>"
        '<p style="font-size:12px;color:#8792a7;margin-top:32px">'
        "If you did not request this code, you can safely ignore this message.</p>"
        '<p style="font-size:12px;color:#8792a7">'
        f"{safe_name} Security Team</p></td></tr></table></body></html>"
    )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = recipient
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    password = (
        settings.smtp_password.get_secret_value() if settings.smtp_password is not None else None
    )
    try:
        with smtplib.SMTP(
            settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout_s
        ) as server:
            server.ehlo()
            if settings.smtp_starttls:
                server.starttls()
                server.ehlo()
            if settings.smtp_username and password:
                server.login(settings.smtp_username, password)
            server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError("Unable to deliver the authentication email.") from exc
