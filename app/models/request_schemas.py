"""Request schemas for FastAPI endpoints."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PasswordRequest(BaseModel):
    password: str = Field(..., min_length=1)


class GenerateRequest(BaseModel):
    length: int | None = Field(default=None, ge=4, le=256)


class FullRequest(BaseModel):
    password: str | None = Field(default=None)
    length: int | None = Field(default=None, ge=4, le=256)

    model_config = {
        "extra": "forbid",
    }

    def model_post_init(self, __context: dict) -> None:
        if not self.password and not self.length:
            raise ValueError("Provide either a password or a length for full analysis")
