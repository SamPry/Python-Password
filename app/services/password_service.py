"""Business logic orchestrating password operations."""
from __future__ import annotations

from ..core.generator import generate_password
from ..core.scoring import StrengthResult, score
from ..core.validator import ValidationResult, validate_password


def validate_flow(password: str) -> ValidationResult:
    return validate_password(password)


def generate_flow(length: int | None = None) -> str:
    return generate_password(length)


def strength_flow(password: str) -> StrengthResult:
    return score(password)


def full_flow(*, password: str | None = None, length: int | None = None) -> tuple[str, ValidationResult, StrengthResult]:
    pwd = password or generate_password(length)
    validation = validate_password(pwd)
    strength = score(pwd)
    return pwd, validation, strength
