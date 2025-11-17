"""Password strength scoring utilities."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

from . import security
from .validator import validate_password


@dataclass(frozen=True)
class StrengthResult:
    score: int
    label: str


_LABELS = {
    range(0, 4): "weak",
    range(4, 7): "medium",
    range(7, 11): "strong",
}


def _label_from_score(score: int) -> str:
    for score_range, label in _LABELS.items():
        if score in score_range:
            return label
    return "unknown"


def _character_set_size(password: str) -> int:
    size = 0
    for charset in (security.UPPERCASE, security.LOWERCASE, security.DIGITS, security.SYMBOLS):
        if any(ch in charset for ch in password):
            size += len(charset)
    return max(size, len(security.LOWERCASE))  # fallback for unexpected input


def _entropy(password: str) -> float:
    charset_size = _character_set_size(password)
    return math.log2(charset_size ** len(password)) if password else 0.0


def score(password: str) -> StrengthResult:
    validation = validate_password(password)

    # base points: length contributions
    base = min(len(password), 20) / 2  # up to 10 points

    # diversity bonus
    diversity = sum(
        (
            validation.upper_ok,
            validation.lower_ok,
            validation.digit_ok,
            validation.symbol_ok,
        )
    )

    entropy_score = min(_entropy(password) / 10, 4)  # normalized

    repetition_penalty = -2 if any(password.count(ch) > len(password) / 2 for ch in set(password)) else 0

    raw_score = base * 0.4 + diversity * 1.5 + entropy_score + repetition_penalty
    bounded_score = max(0, min(10, round(raw_score)))
    return StrengthResult(score=bounded_score, label=_label_from_score(bounded_score))
