"""
AYUSH-specific history-taking layer for MediKiosk.

This module is intentionally a thin domain layer over the existing
conversation engine.

Responsibilities:
    - Identify AYUSH mode.
    - Define AYUSH history-taking sections.
    - Provide deterministic AYUSH question specifications.
    - Track AYUSH-specific collected information.
    - Report deterministic progress/completion.
    - Validate AYUSH field identifiers.

Non-responsibilities:
    - ASR
    - OCR
    - LLM calls
    - diagnosis
    - treatment recommendations
    - red-flag detection
    - independent dialogue management
    - adaptive question selection

The existing conversation engine should remain responsible for:
    - DialogueState
    - adaptive questioning
    - conversation history
    - red flags
    - structured clinical output
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Final, Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AyushSection(StrEnum):
    """Sections of AYUSH history collection."""

    DASHAVIDHA_PARIKSHA = "dashavidha_pariksha"
    AHARA = "ahara"
    VIHARA = "vihara"
    GENERAL_HISTORY = "general_history"


class DashavidhaField(StrEnum):
    """The ten components of Dashavidha Pariksha."""

    PRAKRITI = "prakriti"
    VIKRITI = "vikriti"
    SARA = "sara"
    SAMHANANA = "samhanana"
    PRAMANA = "pramana"
    SATMYA = "satmya"
    SATTVA = "sattva"
    AHARA_SHAKTI = "ahara_shakti"
    VYAYAMA_SHAKTI = "vyayama_shakti"
    VAYA = "vaya"


class AyushField(StrEnum):
    """All AYUSH-specific structured history fields."""

    PRAKRITI = "prakriti"
    VIKRITI = "vikriti"
    SARA = "sara"
    SAMHANANA = "samhanana"
    PRAMANA = "pramana"
    SATMYA = "satmya"
    SATTVA = "sattva"
    AHARA_SHAKTI = "ahara_shakti"
    VYAYAMA_SHAKTI = "vyayama_shakti"
    VAYA = "vaya"

    AHARA_PATTERN = "ahara_pattern"
    AHARA_TIMING = "ahara_timing"
    AHARA_APPETITE = "ahara_appetite"
    AHARA_TOLERANCE = "ahara_tolerance"
    AHARA_PREFERENCES = "ahara_preferences"

    VIHARA_SLEEP = "vihara_sleep"
    VIHARA_ACTIVITY = "vihara_activity"
    VIHARA_EXERCISE = "vihara_exercise"
    VIHARA_DAILY_ROUTINE = "vihara_daily_routine"
    VIHARA_STRESS = "vihara_stress"

    GENERAL_CHIEF_COMPLAINT = "general_chief_complaint"
    GENERAL_DURATION = "general_duration"
    GENERAL_MEDICAL_HISTORY = "general_medical_history"
    GENERAL_MEDICATIONS = "general_medications"
    GENERAL_ALLERGIES = "general_allergies"


class AyushQuestion(BaseModel):
    """
    Deterministic question specification consumed by the existing
    question/adaptive-questioning layer.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    field_id: str
    section: AyushSection
    text: str
    required: bool = True
    order: int = Field(ge=0)

    @field_validator("id", "field_id", "text")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question values cannot be empty.")
        return value


class AyushFieldValue(BaseModel):
    """A collected AYUSH history value."""

    model_config = ConfigDict(extra="forbid")

    field_id: str
    value: Any

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field_id cannot be empty.")
        return value


class AyushProgress(BaseModel):
    """Deterministic AYUSH collection progress."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_fields: int = Field(ge=0)
    collected_fields: int = Field(ge=0)
    remaining_fields: int = Field(ge=0)
    percentage: float = Field(ge=0.0, le=100.0)
    completed: bool


class AyushModeState(BaseModel):
    """Serializable AYUSH-specific state."""

    model_config = ConfigDict(extra="forbid")

    mode: str = "ayush"
    values: dict[str, Any] = Field(default_factory=dict)

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        if value != "ayush":
            raise ValueError("AyushModeState mode must be 'ayush'.")
        return value


# ---------------------------------------------------------------------------
# Deterministic domain definitions
# ---------------------------------------------------------------------------

DASHAVIDHA_FIELDS: Final[tuple[str, ...]] = tuple(
    field.value for field in DashavidhaField
)

AHARA_FIELDS: Final[tuple[str, ...]] = (
    AyushField.AHARA_PATTERN.value,
    AyushField.AHARA_TIMING.value,
    AyushField.AHARA_APPETITE.value,
    AyushField.AHARA_TOLERANCE.value,
    AyushField.AHARA_PREFERENCES.value,
)

VIHARA_FIELDS: Final[tuple[str, ...]] = (
    AyushField.VIHARA_SLEEP.value,
    AyushField.VIHARA_ACTIVITY.value,
    AyushField.VIHARA_EXERCISE.value,
    AyushField.VIHARA_DAILY_ROUTINE.value,
    AyushField.VIHARA_STRESS.value,
)

GENERAL_FIELDS: Final[tuple[str, ...]] = (
    AyushField.GENERAL_CHIEF_COMPLAINT.value,
    AyushField.GENERAL_DURATION.value,
    AyushField.GENERAL_MEDICAL_HISTORY.value,
    AyushField.GENERAL_MEDICATIONS.value,
    AyushField.GENERAL_ALLERGIES.value,
)

AYUSH_FIELDS: Final[tuple[str, ...]] = (
    DASHAVIDHA_FIELDS + AHARA_FIELDS + VIHARA_FIELDS
)


def _question(
    number: int,
    field_id: str,
    section: AyushSection,
    text: str,
) -> AyushQuestion:
    """Create a deterministic question specification."""
    return AyushQuestion(
        id=f"ayush.{section.value}.{number}",
        field_id=field_id,
        section=section,
        text=text,
        order=number,
    )


# The questions deliberately ask for history rather than making clinical
# interpretations. The existing adaptive-questioning module decides when
# an available question should actually be presented.
AYUSH_QUESTIONS: Final[tuple[AyushQuestion, ...]] = (
    _question(
        1,
        AyushField.PRAKRITI.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "Please describe the person's usual body constitution or Prakriti, "
        "if this has previously been assessed.",
    ),
    _question(
        2,
        AyushField.VIKRITI.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "Please describe any current changes from the person's usual state "
        "that have been observed or previously assessed.",
    ),
    _question(
        3,
        AyushField.SARA.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "Please provide the available assessment of Sara or tissue quality, "
        "if previously assessed.",
    ),
    _question(
        4,
        AyushField.SAMHANANA.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "Please provide the available assessment of Samhanana or body "
        "compactness, if previously assessed.",
    ),
    _question(
        5,
        AyushField.PRAMANA.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "Please provide the available Pramana or body measurement "
        "information, if previously assessed.",
    ),
    _question(
        6,
        AyushField.SATMYA.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "Please describe Satmya, including substances, foods, or routines "
        "that the person is accustomed to or tolerates well.",
    ),
    _question(
        7,
        AyushField.SATTVA.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "Please describe the available assessment of Sattva or mental "
        "strength, if previously assessed.",
    ),
    _question(
        8,
        AyushField.AHARA_SHAKTI.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "Please describe the person's usual Ahara Shakti or capacity "
        "related to food intake and digestion, based on history.",
    ),
    _question(
        9,
        AyushField.VYAYAMA_SHAKTI.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "Please describe the person's usual Vyayama Shakti or exercise "
        "capacity.",
    ),
    _question(
        10,
        AyushField.VAYA.value,
        AyushSection.DASHAVIDHA_PARIKSHA,
        "What is the person's age or Vaya?",
    ),
    _question(
        11,
        AyushField.AHARA_PATTERN.value,
        AyushSection.AHARA,
        "Please describe the person's usual food and eating pattern.",
    ),
    _question(
        12,
        AyushField.AHARA_TIMING.value,
        AyushSection.AHARA,
        "What is the usual timing and regularity of meals?",
    ),
    _question(
        13,
        AyushField.AHARA_APPETITE.value,
        AyushSection.AHARA,
        "How would you describe the person's usual appetite?",
    ),
    _question(
        14,
        AyushField.AHARA_TOLERANCE.value,
        AyushSection.AHARA,
        "Are there foods that the person does not tolerate or that commonly "
        "cause discomfort?",
    ),
    _question(
        15,
        AyushField.AHARA_PREFERENCES.value,
        AyushSection.AHARA,
        "Are there any important dietary preferences, restrictions, or "
        "usual food choices to record?",
    ),
    _question(
        16,
        AyushField.VIHARA_SLEEP.value,
        AyushSection.VIHARA,
        "Please describe the person's usual sleep pattern and sleep quality.",
    ),
    _question(
        17,
        AyushField.VIHARA_ACTIVITY.value,
        AyushSection.VIHARA,
        "Please describe the person's usual daily physical activity.",
    ),
    _question(
        18,
        AyushField.VIHARA_EXERCISE.value,
        AyushSection.VIHARA,
        "Please describe the person's usual exercise or physical activity "
        "routine.",
    ),
    _question(
        19,
        AyushField.VIHARA_DAILY_ROUTINE.value,
        AyushSection.VIHARA,
        "Please describe the person's usual daily routine.",
    ),
    _question(
        20,
        AyushField.VIHARA_STRESS.value,
        AyushSection.VIHARA,
        "Please describe any relevant stress, workload, or routine-related "
        "factors.",
    ),
)


class AyushMode:
    """
    Thin AYUSH domain adapter for the existing conversation system.

    This class does not own dialogue management. It exposes AYUSH fields
    and deterministic question specifications so that the existing
    Question Bank, Dialogue State, and Adaptive Questioning components
    can continue to own conversation behavior.
    """

    mode: Final[str] = "ayush"

    def __init__(
        self,
        *,
        include_general_history: bool = True,
    ) -> None:
        self.include_general_history = include_general_history
        self._values: dict[str, Any] = {}

    @property
    def fields(self) -> tuple[str, ...]:
        """Return the AYUSH fields collected by this mode."""
        fields = AYUSH_FIELDS

        if self.include_general_history:
            return fields + GENERAL_FIELDS

        return fields

    @property
    def dashavidha_fields(self) -> tuple[str, ...]:
        """Return the ten Dashavidha Pariksha fields."""
        return DASHAVIDHA_FIELDS

    @property
    def ahara_fields(self) -> tuple[str, ...]:
        """Return AYUSH Ahara fields."""
        return AHARA_FIELDS

    @property
    def vihara_fields(self) -> tuple[str, ...]:
        """Return AYUSH Vihara fields."""
        return VIHARA_FIELDS

    @property
    def general_history_fields(self) -> tuple[str, ...]:
        """Return general history fields included in AYUSH mode."""
        return GENERAL_FIELDS if self.include_general_history else ()

    def is_ayush(self) -> bool:
        """Return True when this mode represents AYUSH consultation."""
        return self.mode == "ayush"

    def questions(
        self,
        *,
        section: AyushSection | None = None,
    ) -> tuple[AyushQuestion, ...]:
        """
        Return deterministic AYUSH question specifications.

        This does not select the next question. The existing adaptive
        questioning component should perform that responsibility.
        """
        questions = AYUSH_QUESTIONS

        if section is None:
            return questions

        return tuple(
            question
            for question in questions
            if question.section == section
        )

    def get_question(self, question_id: str) -> AyushQuestion:
        """Return a question by ID or raise ValueError."""
        for question in AYUSH_QUESTIONS:
            if question.id == question_id:
                return question

        raise ValueError(f"Unknown AYUSH question: {question_id!r}")

    def validate_field(self, field_id: str) -> str:
        """
        Validate and return an AYUSH field identifier.

        Raises:
            ValueError: if the field is not part of this mode.
        """
        if field_id not in self.fields:
            raise ValueError(f"Unknown AYUSH field: {field_id!r}")

        return field_id

    def update_field(self, field_id: str, value: Any) -> None:
        """
        Store a structured AYUSH field value.

        The latest valid structured value replaces the previous value.
        No inference is performed.
        """
        self.validate_field(field_id)

        if value is None:
            raise ValueError("AYUSH field value cannot be None.")

        if isinstance(value, str) and not value.strip():
            raise ValueError("AYUSH field value cannot be empty.")

        self._values[field_id] = value

    def update(self, field: AyushFieldValue) -> None:
        """Update state using a validated AYUSH field-value object."""
        self.update_field(field.field_id, field.value)

    def get_field(self, field_id: str) -> Any | None:
        """Return a collected field value, or None when not collected."""
        self.validate_field(field_id)
        return self._values.get(field_id)

    def has_field(self, field_id: str) -> bool:
        """Return whether a valid field has been collected."""
        self.validate_field(field_id)
        return field_id in self._values

    def collected_fields(self) -> tuple[str, ...]:
        """Return collected field IDs in deterministic schema order."""
        return tuple(
            field_id
            for field_id in self.fields
            if field_id in self._values
        )

    def missing_fields(self) -> tuple[str, ...]:
        """Return missing field IDs in deterministic schema order."""
        return tuple(
            field_id
            for field_id in self.fields
            if field_id not in self._values
        )

    def progress(self) -> AyushProgress:
        """Calculate deterministic AYUSH collection progress."""
        total = len(self.fields)
        collected = len(self.collected_fields())
        remaining = total - collected

        percentage = 0.0 if total == 0 else (collected / total) * 100.0

        return AyushProgress(
            total_fields=total,
            collected_fields=collected,
            remaining_fields=remaining,
            percentage=round(percentage, 2),
            completed=remaining == 0,
        )

    def is_complete(self) -> bool:
        """Return True when every configured field has been collected."""
        return self.progress().completed

    def state(self) -> AyushModeState:
        """Return a serializable snapshot of the AYUSH state."""
        return AyushModeState(
            mode=self.mode,
            values=dict(self._values),
        )

    def collected_information(self) -> Mapping[str, Any]:
        """Return collected information without exposing mutable state."""
        return dict(self._values)

    def reset(self) -> None:
        """Clear collected AYUSH information."""
        self._values.clear()


def create_ayush_mode(
    *,
    include_general_history: bool = True,
) -> AyushMode:
    """
    Create an AYUSH mode instance.

    Backend integration can use this as the explicit mode factory:

        mode = create_ayush_mode()

    The returned object is then passed through the existing conversation
    infrastructure.
    """
    return AyushMode(
        include_general_history=include_general_history,
    )


def is_ayush_mode(mode: str) -> bool:
    """Return True when a backend mode value requests AYUSH."""
    return mode.strip().lower() == "ayush"