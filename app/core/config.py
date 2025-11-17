"""Configuration and policy definitions for password operations."""
from __future__ import annotations

from functools import lru_cache
from pydantic import BaseModel, Field


class PasswordPolicy(BaseModel):
    """Central place to define password policy constraints."""

    min_length: int = Field(default=12, ge=4)
    max_length: int = Field(default=128, ge=32)
    default_length: int = Field(default=16, ge=8)

    class Config:
        frozen = True


@lru_cache(maxsize=1)
def get_policy() -> PasswordPolicy:
    """Return the singleton password policy instance."""

    return PasswordPolicy()
