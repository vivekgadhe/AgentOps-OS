"""Response models for health endpoints."""

from typing import Literal

from pydantic import BaseModel


class LiveResponse(BaseModel):
    status: Literal["ok"]


class ReadyResponse(BaseModel):
    status: Literal["ok", "unavailable"]
    db: Literal["up", "down"]
