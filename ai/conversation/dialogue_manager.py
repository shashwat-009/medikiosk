"""
MediKiosk Conversation Orchestrator.

Coordinates:
    DialogueState
    Ontology
    Question Bank
    AdaptiveQuestioning
    RedFlagDetector

This module does not:
    - perform diagnosis
    - call an LLM
    - call Sarvam/ASR
    - access the database
    - make network requests
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai.conversation.adaptive_questioning import (
    AdaptiveQuestioning,
    NextQuestionResult,
)
from ai.conversation.dialogue_state import (
    DialogueState,
    DialogueStateSnapshot,
    DialogueTurn,
    PatientAnswer,
)
from ai.conversation.ontology import OntologyRegistry
from ai.conversation.question_bank import (
    Question,
    QuestionLanguage,
    get_questions_for_field,
)
from ai.conversation.red_flags import (
    DetectedRedFlag,
    RedFlagDetector,
)


class _QuestionBankAdapter:
    """Adapter exposing the question-bank API expected by AdaptiveQuestioning."""

    @staticmethod
    def get_questions_for_field(
        complaint: Any,
        field: Any,
    ) -> tuple[Question, ...]:
        field_id = getattr(field, "identifier", field)

        return get_questions_for_field(
            complaint,
            str(field_id),
        )


@dataclass(frozen=True)
class ConversationResult:
    """Result after processing one patient answer."""

    next_question: Question | None
    red_flag: DetectedRedFlag | None
    completed: bool


class DialogueManager:
    """
    Orchestrates one deterministic clinical interview.

    The manager owns the runtime state and delegates question selection
    and red-flag detection to their dedicated components.
    """

    def __init__(
        self,
        state: DialogueState,
        *,
        language: QuestionLanguage | str = QuestionLanguage.ENGLISH,
        red_flag_detector: RedFlagDetector | None = None,
    ) -> None:
        if not isinstance(state, DialogueState):
            raise TypeError(
                "state must be a DialogueState instance."
            )

        self.state = state

        self.language = (
            language
            if isinstance(language, QuestionLanguage)
            else QuestionLanguage(language)
        )

        self.red_flag_detector = (
            red_flag_detector
            if red_flag_detector is not None
            else RedFlagDetector()
        )

        self._questioning = AdaptiveQuestioning(
            ontology=OntologyRegistry,
            question_bank=_QuestionBankAdapter(),
            dialogue_state=self.state,
        )

    @classmethod
    def create(
        cls,
        complaint: str,
        *,
        language: QuestionLanguage | str = QuestionLanguage.ENGLISH,
        red_flag_detector: RedFlagDetector | None = None,
    ) -> "DialogueManager":
        """Create a new conversation for a supported complaint."""

        state = DialogueState.create(complaint)

        return cls(
            state,
            language=language,
            red_flag_detector=red_flag_detector,
        )

    # ------------------------------------------------------------------
    # Question flow
    # ------------------------------------------------------------------

    def start(self) -> Question | None:
        """Start the interview and return the first question."""

        return self.get_next_question()

    def get_next_question(self) -> Question | None:
        """
        Get the next question in the configured language.

        AdaptiveQuestioning chooses the clinical field.
        QuestionBank supplies the actual localized question.
        """

        result: NextQuestionResult = (
            self._questioning.get_next_question()
        )

        if result.question is None:
            return None

        question = result.question

        if not isinstance(question, Question):
            raise TypeError(
                "AdaptiveQuestioning returned an invalid Question."
            )

        if question.language == self.language:
            self.state.set_current_question(
                question.question_id
            )
            return question

        localized_questions = get_questions_for_field(
            self.state.complaint,
            question.field_id,
            language=self.language,
        )

        if not localized_questions:
            return None

        localized_question = localized_questions[0]

        self.state.set_current_question(
            localized_question.question_id
        )

        return localized_question

    def get_next_question_result(self) -> NextQuestionResult:
        """Return the complete AdaptiveQuestioning result."""

        return self._questioning.get_next_question()

    # ------------------------------------------------------------------
    # Answer flow
    # ------------------------------------------------------------------

    def record_answer(
        self,
        field_id: str,
        value: Any,
        *,
        question_id: str | None = None,
        source: str | None = None,
        text_for_red_flags: str | None = None,
    ) -> ConversationResult:
        """
        Record one patient answer.

        The answer is stored by DialogueState.
        RedFlagDetector receives only the patient's text.
        """

        resolved_question_id = (
            question_id
            if question_id is not None
            else self.state.current_question_id
        )

        answer = PatientAnswer(
            field_id=field_id,
            value=value,
            question_id=resolved_question_id,
            source=source,
        )

        self.state.record_answer(answer)

        if text_for_red_flags is None and isinstance(value, str):
            text_for_red_flags = value

        red_flag = None

        if text_for_red_flags:
            detected = self.red_flag_detector.detect(
                text_for_red_flags
            )

            if detected.detected:
                red_flag = detected

        self._record_patient_turn(
            field_id=field_id,
            value=value,
            question_id=resolved_question_id,
        )

        next_question = self.get_next_question()

        return ConversationResult(
            next_question=next_question,
            red_flag=red_flag,
            completed=next_question is None,
        )

    def process_voice_answer(
        self,
        field_id: str,
        transcript: str,
        *,
        question_id: str | None = None,
    ) -> ConversationResult:
        """Process an already-transcribed ASR response."""

        if not isinstance(transcript, str):
            raise TypeError(
                "transcript must be a string."
            )

        transcript = transcript.strip()

        if not transcript:
            raise ValueError(
                "transcript cannot be empty."
            )

        return self.record_answer(
            field_id=field_id,
            value=transcript,
            question_id=question_id,
            source="voice",
            text_for_red_flags=transcript,
        )

    def process_text_answer(
        self,
        field_id: str,
        text: str,
        *,
        question_id: str | None = None,
    ) -> ConversationResult:
        """Process a typed patient response."""

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "text cannot be empty."
            )

        return self.record_answer(
            field_id=field_id,
            value=text,
            question_id=question_id,
            source="text",
            text_for_red_flags=text,
        )

    # ------------------------------------------------------------------
    # Interview state
    # ------------------------------------------------------------------

    def is_complete(self) -> bool:
        """Return True when there is no remaining question."""

        return self.get_next_question() is None

    def get_snapshot(self) -> DialogueStateSnapshot:
        """Return an immutable snapshot of the interview state."""

        return self.state.snapshot()

    @property
    def complaint(self) -> str:
        """Current chief complaint."""

        return self.state.complaint

    @property
    def progress(self) -> float:
        """Ontology-field completion ratio."""

        return self.state.completion_ratio

    @property
    def collected_fields(self) -> tuple[str, ...]:
        """Fields already collected."""

        return self.state.collected_fields()

    @property
    def missing_fields(self) -> tuple[str, ...]:
        """Fields not yet collected."""

        return self.state.missing_fields()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _record_patient_turn(
        self,
        *,
        field_id: str,
        value: Any,
        question_id: str | None,
    ) -> None:
        """Record the patient's response in conversation history."""

        text = (
            value
            if isinstance(value, str)
            else str(value)
        )

        turn_number = len(self.state.turns) + 1

        self.state.record_turn(
            DialogueTurn(
                turn_id=f"patient-{turn_number}",
                role="patient",
                text=text,
                question_id=question_id,
                field_id=field_id,
            )
        )


__all__ = [
    "ConversationResult",
    "DialogueManager",
]