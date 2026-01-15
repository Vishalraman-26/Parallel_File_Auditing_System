import re
from typing import Dict, List, Tuple


PatternEntry = Tuple[str, "re.Pattern"]


def _build_sensitive_patterns() -> List[PatternEntry]:
    """
    Build regex patterns used to detect sensitive data.
    """
    patterns: List[PatternEntry] = [
        (
            "email",
            re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                re.IGNORECASE,
            ),
        ),
        (
            "phone",
            re.compile(
                r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{3,4}[-.\s]?){2,3}\d{3,4}\b",
                re.IGNORECASE,
            ),
        ),
        (
            "aadhaar",
            re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
        ),
        (
            "pan",
            re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
        ),
        (
            "url",
            re.compile(
                r"\bhttps?://[^\s]+",
                re.IGNORECASE,
            ),
        ),
        (
            "api_key_generic",
            re.compile(
                r"\b[A-Za-z0-9]{32,}\b",
            ),
        ),
        (
            "password_assignment",
            re.compile(
                r"(?i)\bpassword\s*[:=]\s*['\"].{4,}['\"]",
            ),
        ),
    ]
    return patterns


def _build_forbidden_patterns() -> List[PatternEntry]:
    """
    Build regex patterns for forbidden content.
    """
    forbidden_words = [
        "hack",
        "exploit",
        "bypass security",
        "illegal",
        "banned",
        "blacklisted",
        "classified",
        "top secret",
        "do not distribute",
    ]

    patterns: List[PatternEntry] = []
    for word in forbidden_words:
        safe_word = re.escape(word)
        patterns.append(
            (f"forbidden_{word}", re.compile(rf"(?i)\b{safe_word}\b")),
        )
    return patterns


def _build_policy_patterns() -> List[PatternEntry]:
    """
    Build regex patterns that represent policy violations.
    """
    patterns: List[PatternEntry] = [
        (
            "ssn_like",
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        ),
        (
            "credit_card_like",
            re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
        ),
        (
            "private_key_block",
            re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----"),
        ),
        (
            "aws_access_key",
            re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        ),
        (
            "aws_secret_key",
            re.compile(r"\b[0-9a-zA-Z/+]{40}\b"),
        ),
        (
            "internal_use_only",
            re.compile(r"(?i)internal use only"),
        ),
        (
            "pii_in_logs",
            re.compile(r"(?i)(ssn|dob|date of birth|passport|aadhaar)"),
        ),
        (
            "confidential_in_logs",
            re.compile(r"(?i)confidential|sensitive|proprietary"),
        ),
    ]
    return patterns


SENSITIVE_PATTERNS: List[PatternEntry] = _build_sensitive_patterns()
FORBIDDEN_PATTERNS: List[PatternEntry] = _build_forbidden_patterns()
POLICY_PATTERNS: List[PatternEntry] = _build_policy_patterns()


def get_rules_for_categories(categories: List[str]) -> Dict[str, List[PatternEntry]]:
    """
    Return compiled regex rules for the requested categories.
    """
    rules: Dict[str, List[PatternEntry]] = {}

    if "sensitive" in categories:
        rules["sensitive"] = SENSITIVE_PATTERNS
    if "forbidden" in categories:
        rules["forbidden"] = FORBIDDEN_PATTERNS
    if "policy" in categories:
        rules["policy"] = POLICY_PATTERNS

    return rules

