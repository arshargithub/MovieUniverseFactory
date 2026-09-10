"""Deny-by-default compiler for the qualified 3D-01 revision vocabulary."""
from __future__ import annotations

import re
from typing import Any

from .plans import canonical_revision


COMPILER_VERSION = "3d01-supported-revisions-v1"
_AMBIGUOUS = re.compile(r"\b(?:about|approximately|roughly|maybe|perhaps|somewhat|try|or)\b")
_MOVE = re.compile(
    r"\bmove\s+(?:only\s+)?(?:the\s+)?coffee[ -]table\s+(?:exactly\s+)?"
    r"(?:40\s*(?:cm|centimet(?:er|re)s?)|0[.]4\s*(?:m|met(?:er|re)s?))\s+"
    r"toward(?:s)?\s+(?:the\s+)?sofa\b"
)
_COLOR = re.compile(
    r"\b(?:make|change)\s+(?:only\s+)?(?:the\s+)?helmet(?:\s+shell)?"
    r"(?:\s+(?:from\s+red\s+)?to)?\s+(?:dark[ -]green|#163d2a)\b"
)
_PROTECTION = re.compile(
    r"\bdo\s+not\s+change\s+(?:the\s+)?cameras?,?\s+(?:the\s+)?sofa,?\s+"
    r"(?:the\s+)?room\s+geometry,?\s+(?:the\s+)?lighting,?\s+(?:or\s+)?(?:the\s+)?composition\b"
)


def compile_supported_revision(instruction: str) -> dict[str, Any]:
    """Compile only the exact qualified intent; escalate every ambiguity or extra clause."""
    if not isinstance(instruction, str) or not instruction.strip():
        return {"status": "escalate", "reason": "empty_instruction", "compiler_version": COMPILER_VERSION}
    normalized = " ".join(instruction.lower().replace("\u2011", "-").replace("\u2013", "-").split())
    ambiguity_scope = _PROTECTION.sub(" ", normalized)
    if _AMBIGUOUS.search(ambiguity_scope):
        return {"status": "escalate", "reason": "ambiguous_language", "compiler_version": COMPILER_VERSION}
    move = list(_MOVE.finditer(normalized))
    color = list(_COLOR.finditer(normalized))
    if len(move) != 1 or len(color) != 1:
        return {"status": "escalate", "reason": "unsupported_or_incomplete_intent", "compiler_version": COMPILER_VERSION}
    remainder = normalized
    spans = sorted([move[0].span(), color[0].span(), *[item.span() for item in _PROTECTION.finditer(normalized)]], reverse=True)
    for start, end in spans:
        remainder = remainder[:start] + " " + remainder[end:]
    remainder = re.sub(r"[.,;:]", " ", remainder)
    remainder = re.sub(r"\b(?:and|then|also|please)\b", " ", remainder)
    if remainder.strip():
        return {"status": "escalate", "reason": "unrecognized_clause", "compiler_version": COMPILER_VERSION}
    return {
        "status": "compiled",
        "reason": "supported_unambiguous_revision",
        "compiler_version": COMPILER_VERSION,
        "operations": canonical_revision(),
    }
