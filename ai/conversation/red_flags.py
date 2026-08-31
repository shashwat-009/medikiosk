"""
Deterministic red-flag detection for MediKiosk.

This module detects predefined safety indicators from patient-reported
text. It does not diagnose, prescribe treatment, process audio, or call
external services.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .schemas import RedFlagPriority, RedFlagResult


@dataclass(frozen=True)
class DetectedRedFlag:
    """
    Compatibility result used by the existing red-flag tests.

    The actual project RedFlagResult is validated before this compatibility
    representation is returned.
    """

    detected: bool
    category: str | None = None
    matched_pattern: str | None = None

    flag_id: str | None = None
    priority: RedFlagPriority | None = None
    matched_fields: tuple[str, ...] = ()
    matched_text: str | None = None
    explanation: str | None = None


RED_FLAG_PATTERNS: dict[str, tuple[str, ...]] = {
    "severe_breathing_difficulty": (
        "cannot breathe",
        "can't breathe",
        "difficulty breathing",
        "breathing difficulty",
        "having difficulty breathing",
        "i cannot breathe",
        "i can't breathe",
        "saans nahi aa rahi",
        "saans lene mein dikkat",
        "saans lene me dikkat",
        "saans phool rahi",
    ),
    "loss_of_consciousness": (
        "lost consciousness",
        "passed out",
        "pass out",
        "unconscious",
        "i was unconscious",
        "i became unconscious",
        "behosh ho gaya",
        "behosh ho gayi",
        "behosh ho gaya tha",
        "behosh ho gayi thi",
    ),
    "severe_chest_pain": (
        "severe chest pain",
        "very severe chest pain",
        "chest pain is severe",
        "i have severe chest pain",
        "bahut tez seene ka dard",
        "bahut zyada seene mein dard",
        "bahut zyada seene me dard",
    ),
    "severe_bleeding": (
        "heavy bleeding",
        "bleeding heavily",
        "bleeding a lot",
        "i am bleeding heavily",
        "i am bleeding a lot",
        "bahut zyada khoon",
        "bahut khoon beh raha",
        "khoon bahut beh raha",
    ),
"sudden_weakness_or_paralysis": (
    "sudden weakness",
    "sudden paralysis",
    "one side is weak",
    "one side weakness",
    "suddenly weak",
    "suddenly have weakness on one side",
    "weakness on one side",
    "weak on one side",
    "ek taraf kamzori",
    "ek side kamzor",
    "achanak kamzori",
),
}


def _normalize(text: str) -> str:
    """Normalize case and repeated whitespace."""
    text = text.casefold()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    """Match a complete phrase rather than an arbitrary substring."""
    normalized_text = _normalize(text)
    normalized_phrase = _normalize(phrase)

    if not normalized_text or not normalized_phrase:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(normalized_phrase)
        + r"(?!\w)"
    )

    return re.search(pattern, normalized_text) is not None


def _is_negated_or_contextual(
    text: str,
    phrase: str,
) -> bool:
    """Reject obvious negation and third-person/contextual references."""

    normalized_text = _normalize(text)
    normalized_phrase = _normalize(phrase)

    phrase_index = normalized_text.find(normalized_phrase)

    if phrase_index < 0:
        return False

    before = normalized_text[:phrase_index].strip()

    negation_patterns = (
        r"\bdid not\s*$",
        r"\bdidn't\s*$",
        r"\bdo not\s*$",
        r"\bdon't\s*$",
        r"\bdoes not\s*$",
        r"\bdoesn't\s*$",
        r"\bnot\s*$",
        r"\bno\s*$",
        r"\bnever\s*$",
        r"\bnahi\s*$",
        r"\bnahin\s*$",
    )

    for pattern in negation_patterns:
        if re.search(pattern, before):
            return True

    context = before[-150:]

    contextual_patterns = (
        r"\bsomeone\b",
        r"\bsomebody\b",
        r"\ba person\b",
        r"\banother person\b",
        r"\bin a movie\b",
        r"\bin the movie\b",
        r"\bmovie about\b",
    )

    return any(
        re.search(pattern, context)
        for pattern in contextual_patterns
    )


def _extract_text(answer: Any) -> str:
    """Extract text from a string or existing PatientAnswer-like object."""

    if answer is None:
        return ""

    if isinstance(answer, str):
        return answer

    resolved_text = getattr(answer, "resolved_text", None)

    if callable(resolved_text):
        value = resolved_text()
        if isinstance(value, str):
            return value

    for attribute in (
        "text",
        "answer",
        "transcript",
        "value",
        "content",
    ):
        value = getattr(answer, attribute, None)

        if isinstance(value, str):
            return value

    return ""


class RedFlagDetector:
    """
    Deterministic rule-based red-flag detector.
    """

    def __init__(
        self,
        patterns: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        self.patterns = (
            RED_FLAG_PATTERNS.copy()
            if patterns is None
            else patterns
        )

    def detect(self, answer: Any) -> DetectedRedFlag:
        """Detect the first matching predefined red flag."""

        text = _extract_text(answer)
        normalized_text = _normalize(text)

        if not normalized_text:
            return self._no_flag()

        for flag_id, patterns in self.patterns.items():
            for phrase in patterns:

                if not _contains_phrase(
                    normalized_text,
                    phrase,
                ):
                    continue

                if _is_negated_or_contextual(
                    normalized_text,
                    phrase,
                ):
                    continue

                return self._detected_flag(
                    flag_id=flag_id,
                    matched_phrase=phrase,
                    matched_text=text,
                )

        return self._no_flag()

    def has_red_flag(self, answer: Any) -> bool:
        """Return only whether a red flag was detected."""
        return self.detect(answer).detected

    @staticmethod
    def _no_flag() -> DetectedRedFlag:
        """
        Validate a non-detected result using the real project schema,
        then expose the compatibility result expected by existing tests.
        """

        RedFlagResult(
            detected=False,
            flag_id=None,
            priority=None,
            matched_fields=[],
            matched_text=None,
            explanation=None,
        )

        return DetectedRedFlag(
            detected=False,
            category=None,
            matched_pattern=None,
        )

    @staticmethod
    def _detected_flag(
        flag_id: str,
        matched_phrase: str,
        matched_text: str,
    ) -> DetectedRedFlag:
        """
        Validate the result using the real RedFlagResult schema.

        Then expose category/matched_pattern compatibility properties
        required by the existing tests.
        """

        # Use an existing enum member rather than inventing a priority.
        priority = next(iter(RedFlagPriority))

        validated = RedFlagResult(
            detected=True,
            flag_id=flag_id,
            priority=priority,
            matched_fields=[],
            matched_text=matched_text,
            explanation=(
                f"Predefined red-flag pattern matched: {matched_phrase}"
            ),
        )

        return DetectedRedFlag(
            detected=validated.detected,
            category=validated.flag_id,
            matched_pattern=matched_phrase,
            flag_id=validated.flag_id,
            priority=validated.priority,
            matched_fields=tuple(validated.matched_fields),
            matched_text=validated.matched_text,
            explanation=validated.explanation,
        )


def detect_red_flags(answer: Any) -> DetectedRedFlag:
    """Convenience API for direct red-flag detection."""
    return RedFlagDetector().detect(answer)