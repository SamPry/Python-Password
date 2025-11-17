"""Secure password generation utilities."""
from __future__ import annotations

import random
import secrets
from typing import Iterable, List

from .config import get_policy
from . import security


class SecureRandom(random.SystemRandom):
    """`random`-compatible shim backed by secrets for shuffling."""

    def shuffle(self, x: List[str]) -> None:  # type: ignore[override]
        secrets.SystemRandom().shuffle(x)


_secure_random = SecureRandom()


def _pick(characters: str, count: int) -> Iterable[str]:
    for _ in range(count):
        yield secrets.choice(characters)


def generate_password(length: int | None = None) -> str:
    """Generate a password that satisfies the minimal policy rules."""

    policy = get_policy()
    length = length or policy.default_length
    if length < 4:
        raise ValueError("Password length must be at least 4 to satisfy constraints")
    if length > policy.max_length:
        raise ValueError("Requested password length exceeds policy maximum")

    required_chars = [
        secrets.choice(security.UPPERCASE),
        secrets.choice(security.LOWERCASE),
        secrets.choice(security.DIGITS),
        secrets.choice(security.SYMBOLS),
    ]

    if length < len(required_chars):
        raise ValueError("Length insufficient for required character categories")

    remaining_length = length - len(required_chars)
    password_chars = required_chars + list(_pick(security.FULL_SET, remaining_length))
    _secure_random.shuffle(password_chars)
    return "".join(password_chars)
