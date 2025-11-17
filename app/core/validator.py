"""Password validation utilities."""
from __future__ import annotations

from dataclasses import dataclass

from .config import get_policy
from . import security


@dataclass(frozen=True)
class ValidationResult:
    """Structured result for password validation."""

    length_ok: bool
    upper_ok: bool
    lower_ok: bool
    digit_ok: bool
    symbol_ok: bool

    @property
    def overall_result(self) -> bool:
        return all(
            (
                self.length_ok,
                self.upper_ok,
                self.lower_ok,
                self.digit_ok,
                self.symbol_ok,
            )
        )


def check_length(password: str) -> bool:
    policy = get_policy()
    return policy.min_length <= len(password) <= policy.max_length


def check_upper(password: str) -> bool:
    return any(ch in security.UPPERCASE for ch in password)


def check_lower(password: str) -> bool:
    return any(ch in security.LOWERCASE for ch in password)


def check_digit(password: str) -> bool:
    return any(ch in security.DIGITS for ch in password)


def check_symbol(password: str) -> bool:
    return any(ch in security.SYMBOLS for ch in password)


def validate_password(password: str) -> ValidationResult:
    """Run all password validation checks and return a result object."""

    return ValidationResult(
        length_ok=check_length(password),
        upper_ok=check_upper(password),
        lower_ok=check_lower(password),
        digit_ok=check_digit(password),
        symbol_ok=check_symbol(password),
    )
