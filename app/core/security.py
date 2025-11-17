"""Security-related helpers and constants."""
from __future__ import annotations

import string

UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = string.punctuation

# Full alphabet used for password generation once minimums satisfied.
FULL_SET = UPPERCASE + LOWERCASE + DIGITS + SYMBOLS
