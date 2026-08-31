"""
Deterministic adaptive questioning for the MediKiosk conversation layer.

This is a provisional implementation.

Responsibility:
    Given a complaint, ontology, question bank, and dialogue state,
    select exactly one unanswered question.

This module deliberately:
    - does not call an LLM
    - does not call ASR/Sarvam
    - does not perform diagnosis
    - does not perform red-flag detection
    - does not maintain conversation history
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class NextQuestionResult:
    """Result returned by AdaptiveQuestioning."""

    question: Any | None
    reason: str

    @property
    def has_question(self) -> bool:
        """Return True when a question is available."""
        return self.question is not None


class AdaptiveQuestioning:
    """
    Select the next appropriate question deterministically.

    The implementation is intentionally dependency-light. Ontology,
    Question Bank, and Dialogue State objects are injected so this
    module does not duplicate their responsibilities.
    """

    def __init__(
        self,
        ontology: Any,
        question_bank: Any,
        dialogue_state: Any,
    ) -> None:
        self.ontology = ontology
        self.question_bank = question_bank
        self.dialogue_state = dialogue_state

    def get_next_question(
        self,
        complaint: Any | None = None,
    ) -> NextQuestionResult:
        """
        Return exactly one question for the current state.

        Selection order:
            1. Resolve complaint.
            2. Retrieve ontology fields.
            3. Determine collected fields from Dialogue State.
            4. Preserve ontology/question-bank ordering.
            5. Select the first field that is not collected.
            6. Select the first available question for that field.

        No question is generated dynamically.
        """
        complaint = self._resolve_complaint(complaint)

        if complaint is None:
            return NextQuestionResult(
                question=None,
                reason="unknown_or_missing_complaint",
            )

        fields = self._get_relevant_fields(complaint)

        if not fields:
            return NextQuestionResult(
                question=None,
                reason="no_applicable_ontology_fields",
            )

        collected = self._get_collected_fields()

        for field in fields:
            field_id = self._field_id(field)

            if field_id is None:
                continue

            if field_id in collected:
                continue

            question = self._get_question_for_field(
                complaint=complaint,
                field=field,
            )

            if question is not None:
                return NextQuestionResult(
                    question=question,
                    reason="next_missing_field",
                )

        return NextQuestionResult(
            question=None,
            reason="no_available_question",
        )

    def next_question(self, complaint: Any | None = None) -> Any | None:
        """
        Convenience API returning only the question.

        Returns None when no suitable question exists.
        """
        return self.get_next_question(complaint).question

    # ------------------------------------------------------------------
    # Complaint
    # ------------------------------------------------------------------

    def _resolve_complaint(self, complaint: Any | None) -> Any | None:
        if complaint is not None:
            return complaint

        state = self.dialogue_state

        for attribute in (
            "complaint",
            "chief_complaint",
            "current_complaint",
        ):
            value = getattr(state, attribute, None)

            if value is not None:
                return value

        for method_name in (
            "get_complaint",
            "get_chief_complaint",
            "get_current_complaint",
        ):
            method = getattr(state, method_name, None)

            if callable(method):
                value = method()
                if value is not None:
                    return value

        return None

    # ------------------------------------------------------------------
    # Ontology
    # ------------------------------------------------------------------

    def _get_relevant_fields(self, complaint: Any) -> list[Any]:
        """
        Retrieve ontology fields while supporting common ontology APIs.

        This compatibility layer is provisional and should be simplified
        after the real ontology interface is inspected.
        """
        ontology = self.ontology

        for method_name in (
            "get_fields",
            "get_relevant_fields",
            "get_fields_for_complaint",
        ):
            method = getattr(ontology, method_name, None)

            if callable(method):
                result = method(complaint)
                return list(result or [])

        # Registry-style ontology API.
        for method_name in (
            "get_ontology",
            "get",
        ):
            method = getattr(ontology, method_name, None)

            if callable(method):
                result = method(complaint)

                if result is None:
                    return []

                for attribute in (
                    "fields",
                    "relevant_fields",
                    "clinical_fields",
                ):
                    fields = getattr(result, attribute, None)

                    if fields is not None:
                        return list(fields)

        # Complaint may itself expose its fields.
        for attribute in (
            "fields",
            "relevant_fields",
            "clinical_fields",
        ):
            fields = getattr(complaint, attribute, None)

            if fields is not None:
                return list(fields)

        return []

    @staticmethod
    def _field_id(field: Any) -> str | None:
        """Extract a stable field identifier."""
        if field is None:
            return None

        if isinstance(field, str):
            return field

        for attribute in (
            "field_id",
            "id",
            "identifier",
            "name",
            "value",
        ):
            value = getattr(field, attribute, None)

            if value is not None:
                return str(value)

        return str(field) if field is not None else None

    # ------------------------------------------------------------------
    # Dialogue State
    # ------------------------------------------------------------------

    def _get_collected_fields(self) -> set[str]:
        """
        Obtain collected field IDs through the Dialogue State API.

        Public APIs are preferred. Common representations are supported
        provisionally because the real implementation has not yet been
        inspected.
        """
        state = self.dialogue_state

        for method_name in (
            "get_collected_fields",
            "collected_fields",
        ):
            value = getattr(state, method_name, None)

            if callable(value):
                result = value()
                return self._normalise_field_ids(result)

            if value is not None:
                return self._normalise_field_ids(value)

        for method_name in (
            "get_known_fields",
            "get_known_field_ids",
        ):
            method = getattr(state, method_name, None)

            if callable(method):
                return self._normalise_field_ids(method())

        for attribute in (
            "collected",
            "known_fields",
            "clinical_fields",
            "values",
        ):
            value = getattr(state, attribute, None)

            if value is not None:
                return self._normalise_field_ids(value)

        return set()

    def _normalise_field_ids(self, fields: Any) -> set[str]:
        if fields is None:
            return set()

        if isinstance(fields, dict):
            return {
                self._field_id(key)
                for key, value in fields.items()
                if value is not None and self._field_id(key) is not None
            }

        if isinstance(fields, str):
            return {fields}

        try:
            values: Iterable[Any] = fields
        except TypeError:
            return set()

        result: set[str] = set()

        for field in values:
            field_id = self._field_id(field)

            if field_id is not None:
                result.add(field_id)

        return result

    # ------------------------------------------------------------------
    # Question Bank
    # ------------------------------------------------------------------

    def _get_question_for_field(
        self,
        complaint: Any,
        field: Any,
    ) -> Any | None:
        question_bank = self.question_bank
        field_id = self._field_id(field)

        if field_id is None:
            return None

        # Preferred API.
        for method_name in (
            "get_questions_for_field",
            "get_question_for_field",
        ):
            method = getattr(question_bank, method_name, None)

            if callable(method):
                try:
                    result = method(complaint, field)
                except TypeError:
                    result = method(complaint, field_id)

                if result is None:
                    return None

                if isinstance(result, (list, tuple)):
                    return result[0] if result else None

                return result

        # Fallback: retrieve complaint questions and filter by field.
        for method_name in (
            "get_questions_for_complaint",
            "get_questions",
        ):
            method = getattr(question_bank, method_name, None)

            if not callable(method):
                continue

            questions = method(complaint) or []

            for question in questions:
                question_field = self._question_field_id(question)

                if question_field == field_id:
                    return question

        return None

    @staticmethod
    def _question_field_id(question: Any) -> str | None:
        if question is None:
            return None

        for attribute in (
            "field_id",
            "clinical_field",
            "ontology_field",
            "field",
        ):
            value = getattr(question, attribute, None)

            if value is None:
                continue

            if isinstance(value, str):
                return value

            for nested_attribute in (
                "field_id",
                "id",
                "identifier",
                "name",
                "value",
            ):
                nested = getattr(value, nested_attribute, None)

                if nested is not None:
                    return str(nested)

            return str(value)

        return None