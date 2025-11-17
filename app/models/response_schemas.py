"""Response schemas for API endpoints."""
from __future__ import annotations

from pydantic import BaseModel


class ValidationResponse(BaseModel):
    length_ok: bool
    upper_ok: bool
    lower_ok: bool
    digit_ok: bool
    symbol_ok: bool
    overall_result: bool


class GeneratedPasswordResponse(BaseModel):
    password: str


class StrengthResponse(BaseModel):
    score: int
    label: str


class FullResponse(BaseModel):
    validation: ValidationResponse
    strength: StrengthResponse
    password: str | None = None
