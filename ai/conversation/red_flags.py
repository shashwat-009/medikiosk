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
    # ==================================================================
    # SEVERE BREATHING DIFFICULTY
    # ==================================================================
    "severe_breathing_difficulty": (
        # English
        "cannot breathe",
        "can't breathe",
        "difficulty breathing",
        "breathing difficulty",
        "having difficulty breathing",
        "i cannot breathe",
        "i can't breathe",
        "i am having difficulty breathing",
        "i am having severe difficulty breathing",
        "severe difficulty breathing",
        "shortness of breath",
        "severe shortness of breath",

        # Hindi - Hinglish
        "saans nahi aa rahi",
        "saans lene mein dikkat",
        "saans lene me dikkat",
        "saans lene mein bahut dikkat",
        "saans lene me bahut dikkat",
        "saans phool rahi",
        "saans phool rahi hai",
        "bahut saans phool rahi hai",

        # Hindi - Devanagari
        "सांस नहीं आ रही",
        "साँस नहीं आ रही",
        "सांस लेने में दिक्कत",
        "साँस लेने में दिक्कत",
        "सांस लेने में बहुत दिक्कत",
        "साँस लेने में बहुत दिक्कत",
        "सांस फूल रही है",
        "साँस फूल रही है",

        # Bengali
        "শ্বাস নিতে পারছি না",
        "শ্বাস নিতে কষ্ট হচ্ছে",
        "শ্বাস নিতে খুব কষ্ট হচ্ছে",
        "শ্বাসকষ্ট হচ্ছে",
        "খুব শ্বাসকষ্ট হচ্ছে",

        # Marathi
        "श्वास घेता येत नाही",
        "श्वास घेण्यास त्रास होत आहे",
        "श्वास घेण्यास खूप त्रास होत आहे",
        "श्वास घेण्यास अडचण होत आहे",
        "खूप श्वास घेण्यास त्रास होत आहे",
    ),

    # ==================================================================
    # LOSS OF CONSCIOUSNESS
    # ==================================================================
    "loss_of_consciousness": (
        # English
        "lost consciousness",
        "passed out",
        "pass out",
        "unconscious",
        "i was unconscious",
        "i became unconscious",
        "i fainted",
        "fainted",

        # Hindi - Hinglish
        "behosh ho gaya",
        "behosh ho gayi",
        "behosh ho gaya tha",
        "behosh ho gayi thi",
        "main behosh ho gaya",
        "main behosh ho gayi",
        "hosh kho diya",

        # Hindi - Devanagari
        "बेहोश हो गया",
        "बेहोश हो गई",
        "बेहोश हो गया था",
        "बेहोश हो गई थी",
        "मैं बेहोश हो गया",
        "मैं बेहोश हो गई",
        "होश खो दिया",

        # Bengali
        "অজ্ঞান হয়ে গিয়েছিলাম",
        "অজ্ঞান হয়ে গিয়েছিলাম",
        "আমি অজ্ঞান হয়ে গিয়েছিলাম",
        "জ্ঞান হারিয়েছিলাম",
        "জ্ঞান হারিয়ে ফেলেছিলাম",

        # Marathi
        "बेशुद्ध झालो",
        "बेशुद्ध झाले",
        "बेशुद्ध झालो होतो",
        "बेशुद्ध झाले होते",
        "मी बेशुद्ध झालो",
        "मी बेशुद्ध झाले",
        "शुद्ध हरपली",
    ),

    # ==================================================================
    # SEVERE CHEST PAIN
    # ==================================================================
    "severe_chest_pain": (
        # English
        "severe chest pain",
        "very severe chest pain",
        "chest pain is severe",
        "i have severe chest pain",
        "extreme chest pain",
        "very bad chest pain",
        "unbearable chest pain",

        # Hindi - Hinglish
        "bahut tez seene ka dard",
        "bahut zyada seene mein dard",
        "bahut zyada seene me dard",
        "seene mein bahut tez dard",
        "seene me bahut tez dard",
        "seene ka bahut zyada dard",

        # Hindi - Devanagari
        "बहुत तेज सीने का दर्द",
        "बहुत ज्यादा सीने में दर्द",
        "सीने में बहुत तेज दर्द",
        "सीने में बहुत ज्यादा दर्द",
        "सीने का बहुत ज्यादा दर्द",

        # Bengali
        "বুকে খুব তীব্র ব্যথা",
        "বুকে প্রচণ্ড ব্যথা",
        "বুকে খুব বেশি ব্যথা",
        "বুকে অসহ্য ব্যথা",
        "তীব্র বুকে ব্যথা",

        # Marathi
        "छातीत खूप तीव्र वेदना",
        "छातीत खूप जास्त वेदना",
        "छातीत तीव्र वेदना",
        "छातीत असह्य वेदना",
        "छातीत खूप दुखत आहे",
    ),

    # ==================================================================
    # SEVERE BLEEDING
    # ==================================================================
    "severe_bleeding": (
        # English
        "heavy bleeding",
        "bleeding heavily",
        "bleeding a lot",
        "i am bleeding heavily",
        "i am bleeding a lot",
        "severe bleeding",
        "blood is pouring",

        # Hindi - Hinglish
        "bahut zyada khoon",
        "bahut khoon beh raha",
        "khoon bahut beh raha",
        "bahut zyada khoon beh raha",
        "bahut khoon nikal raha",

        # Hindi - Devanagari
        "बहुत ज्यादा खून",
        "बहुत खून बह रहा",
        "खून बहुत बह रहा",
        "बहुत ज्यादा खून बह रहा",
        "बहुत खून निकल रहा",

        # Bengali
        "অনেক রক্তপাত হচ্ছে",
        "খুব বেশি রক্তপাত হচ্ছে",
        "অনেক রক্ত বের হচ্ছে",
        "খুব বেশি রক্ত বের হচ্ছে",
        "প্রচুর রক্তপাত হচ্ছে",

        # Marathi
        "खूप रक्तस्राव होत आहे",
        "खूप जास्त रक्तस्राव होत आहे",
        "खूप रक्त वाहत आहे",
        "खूप जास्त रक्त वाहत आहे",
        "प्रचंड रक्तस्राव होत आहे",
    ),

    # ==================================================================
    # SUDDEN WEAKNESS / PARALYSIS
    # ==================================================================
    "sudden_weakness_or_paralysis": (
        # English
        "sudden weakness",
        "sudden paralysis",
        "one side is weak",
        "one side weakness",
        "suddenly weak",
        "suddenly have weakness on one side",
        "weakness on one side",
        "weak on one side",
        "sudden numbness",
        "one side is numb",
        "one side numbness",

        # Hindi - Hinglish
        "ek taraf kamzori",
        "ek side kamzor",
        "achanak kamzori",
        "ek taraf achanak kamzori",
        "ek side achanak kamzor",
        "ek taraf sunn",
        "ek side sunn",
        "haath pair mein achanak kamzori",

        # Hindi - Devanagari
        "एक तरफ कमजोरी",
        "एक तरफ़ कमजोरी",
        "एक साइड कमजोर",
        "अचानक कमजोरी",
        "एक तरफ अचानक कमजोरी",
        "एक तरफ सुन्न",
        "एक साइड सुन्न",
        "हाथ पैर में अचानक कमजोरी",

        # Bengali
        "হঠাৎ দুর্বলতা",
        "হঠাৎ এক পাশ দুর্বল",
        "শরীরের এক পাশ দুর্বল",
        "এক পাশ অবশ",
        "হঠাৎ পক্ষাঘাত",
        "এক পাশে হঠাৎ দুর্বলতা",

        # Marathi
        "अचानक अशक्तपणा",
        "अचानक कमजोरी",
        "शरीराची एक बाजू कमजोर",
        "एक बाजू सुन्न",
        "अचानक पक्षाघात",
        "एका बाजूला अचानक कमजोरी",
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