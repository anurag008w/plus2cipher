"""
core/cipher.py

The +2 Cipher engine.

Deterministic Caesar-style alphabet shift. Completely independent of any UI
framework so it can be imported and unit tested without launching Kivy.

Encoding shifts every alphabetic character forward by `shift` positions
(default 2), wrapping from Z back to A. Decoding shifts backward by the same
amount. Case is preserved. Every non-alphabetic character (spaces, tabs,
newlines, digits, punctuation, symbols, unicode text, emoji, etc.) passes
through completely unchanged.

This is a simple substitution/shift utility, NOT secure encryption. It
provides no real confidentiality and must never be described as such in the
UI (see about screen copy).
"""

from __future__ import annotations

ALPHABET_SIZE = 26
DEFAULT_SHIFT = 2


def _shift_char(char: str, shift: int) -> str:
    """Shift a single character by `shift` positions if it is A-Z or a-z."""
    code = ord(char)

    # Uppercase A-Z (65-90)
    if 65 <= code <= 90:
        return chr((code - 65 + shift) % ALPHABET_SIZE + 65)

    # Lowercase a-z (97-122)
    if 97 <= code <= 122:
        return chr((code - 97 + shift) % ALPHABET_SIZE + 97)

    # Everything else (spaces, digits, punctuation, unicode, ...) untouched.
    return char


def transform(text: str, shift: int) -> str:
    """Shift every alphabetic character in `text` by `shift` positions.

    Positive shift = encode direction, negative shift = decode direction.
    Non-alphabetic characters are preserved exactly, including their
    position, so string length is always preserved.
    """
    if text is None:
        return ""
    return "".join(_shift_char(c, shift) for c in text)


def encode(text: str, shift: int = DEFAULT_SHIFT) -> str:
    """Encode `text` by shifting letters forward by `shift` (default +2)."""
    return transform(text, shift)


def decode(text: str, shift: int = DEFAULT_SHIFT) -> str:
    """Decode `text` by shifting letters backward by `shift` (default -2)."""
    return transform(text, -shift)


def apply_mode(text: str, mode: str, shift: int = DEFAULT_SHIFT) -> str:
    """Convenience helper: mode is either 'encode' or 'decode'."""
    if mode not in ("encode", "decode"):
        raise ValueError(f"Unknown mode: {mode!r}. Expected 'encode' or 'decode'.")
    return encode(text, shift) if mode == "encode" else decode(text, shift)


def preview_mapping(shift: int = DEFAULT_SHIFT) -> list[tuple[str, str]]:
    """Return the a->? mapping table used on the About screen, e.g. ('a','c')."""
    import string

    pairs = []
    for letter in string.ascii_lowercase:
        pairs.append((letter, _shift_char(letter, shift)))
    return pairs
