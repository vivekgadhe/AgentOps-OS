"""Authentication and email OTP request/response schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RegistrationStartRequest(BaseModel):
    email: EmailStr


class RegistrationRequest(BaseModel):
    email: EmailStr
    # ``invitation_token`` remains accepted as a legacy input alias.
    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^[0-9]{6}$",
        validation_alias=AliasChoices("otp", "invitation_token"),
    )
    password: str = Field(min_length=12, max_length=128)


class PasswordResetRequest(BaseModel):
    email: EmailStr
    token: str = Field(min_length=6, max_length=6, pattern=r"^[0-9]{6}$")
    new_password: str = Field(min_length=12, max_length=128)


class PasswordResetStartRequest(BaseModel):
    email: EmailStr


class InvitationCreateRequest(BaseModel):
    email: EmailStr
    role: Literal["admin", "operator", "viewer"] = "operator"


class InvitationCreateResponse(BaseModel):
    message: str
    email: EmailStr
    expires_at: datetime


class PasswordResetIssueRequest(BaseModel):
    email: EmailStr


class PasswordResetIssueResponse(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    is_active: bool
