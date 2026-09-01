"""
Deterministic adaptive questioning for the MediKiosk conversation layer.

Responsibility:
    Given a complaint, ontology, question bank, dialogue state, and
    requested language, select exactly one unanswered question.

This module deliberately:
    - does not call an LLM
    - does not call ASR/Sarvam
    - does not perform diagnosis
    - does not perform red-flag detection
    - does not maintain conversation history
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ai.conversation.question_bank import QuestionLanguage


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

    Ontology, Question Bank, and Dialogue State objects are injected so
    this module does not duplicate their responsibilities.
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_next_question(
        self,
        complaint: Any | None = None,
        language: QuestionLanguage | str | None = None,
    ) -> NextQuestionResult:
        """
        Return exactly one unanswered question.

        Selection order:
            1. Resolve complaint.
            2. Resolve requested language.
            3. Retrieve ontology fields.
            4. Determine collected fields from Dialogue State.
            5. Preserve ontology/question-bank ordering.
            6. Select the first field that is not collected.
            7. Select the first question for that field in the
               requested language.

        If no language is supplied, the Dialogue State is checked.
        English is the final backwards-compatible fallback.
        """

        complaint = self._resolve_complaint(complaint)

        if complaint is None:
            return NextQuestionResult(
                question=None,
                reason="unknown_or_missing_complaint",
            )

        selected_language = self._resolve_language(language)

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
                language=selected_language,
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

    def next_question(
        self,
        complaint: Any | None = None,
        language: QuestionLanguage | str | None = None,
    ) -> Any | None:
        """
        Convenience API returning only the next question.

        Returns None when no suitable question exists.
        """
        return self.get_next_question(
            complaint=complaint,
            language=language,
        ).question

    # ------------------------------------------------------------------
    # Language
    # ------------------------------------------------------------------

    def _resolve_language(
        self,
        language: QuestionLanguage | str | None,
    ) -> QuestionLanguage:
        """
        Resolve the requested question language.

        Explicit language takes priority.

        If no language is supplied, try Dialogue State.

        English is used as the final fallback for backwards compatibility.
        """

        if language is not None:
            return self._normalise_language(language)

        state = self.dialogue_state

        # Try common state attributes.
        for attribute in (
            "language",
            "preferred_language",
            "current_language",
        ):
            value = getattr(state, attribute, None)

            if value is not None:
                try:
                    return self._normalise_language(value)
                except ValueError:
                    pass

        # Try common state methods.
        for method_name in (
            "get_language",
            "get_preferred_language",
            "get_current_language",
        ):
            method = getattr(state, method_name, None)

            if callable(method):
                value = method()

                if value is not None:
                    try:
                        return self._normalise_language(value)
                    except ValueError:
                        pass

        return QuestionLanguage.ENGLISH

    @staticmethod
    def _normalise_language(
        language: QuestionLanguage | str,
    ) -> QuestionLanguage:
        """Convert a language value into QuestionLanguage."""

        if isinstance(language, QuestionLanguage):
            return language

        if not isinstance(language, str):
            raise ValueError(
                "Language must be a string or QuestionLanguage."
            )

        value = language.strip().lower()

        aliases = {
            # English
            "en": QuestionLanguage.ENGLISH,
            "english": QuestionLanguage.ENGLISH,

            # Hindi
            "hi": QuestionLanguage.HINDI,
            "hindi": QuestionLanguage.HINDI,

            # Bengali
            "bn": QuestionLanguage.BENGALI,
            "bengali": QuestionLanguage.BENGALI,

            # Marathi
            "mr": QuestionLanguage.MARATHI,
            "marathi": QuestionLanguage.MARATHI,
        }

        try:
            return aliases[value]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported language: {language!r}"
            ) from exc

    # ------------------------------------------------------------------
    # Complaint
    # ------------------------------------------------------------------

    def _resolve_complaint(
        self,
        complaint: Any | None,
    ) -> Any | None:
        """Resolve complaint from the argument or Dialogue State."""

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

    def _get_relevant_fields(
        self,
        complaint: Any,
    ) -> list[Any]:
        """Retrieve ontology fields using the existing ontology APIs."""

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

        # Complaint may itself expose fields.
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
    def _field_id(
        field: Any,
    ) -> str | None:
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

        return str(field)

    # ------------------------------------------------------------------
    # Dialogue State
    # ------------------------------------------------------------------

    def _get_collected_fields(self) -> set[str]:
        """Obtain collected field IDs through the Dialogue State API."""

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

    def _normalise_field_ids(
        self,
        fields: Any,
    ) -> set[str]:
        """Normalise a collection of field identifiers."""

        if fields is None:
            return set()

        if isinstance(fields, dict):
            result: set[str] = set()

            for key, value in fields.items():
                if value is None:
                    continue

                field_id = self._field_id(key)

                if field_id is not None:
                    result.add(field_id)

            return result

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
        language: QuestionLanguage,
    ) -> Any | None:
        """
        Retrieve the first question for a field in the requested language.

        Supports:
            - the real multilingual Question Bank
            - legacy/simple Question Bank implementations
            - test doubles that do not expose a language attribute
        """

        question_bank = self.question_bank
        field_id = self._field_id(field)

        if field_id is None:
            return None

        # --------------------------------------------------------------
        # Preferred API
        # --------------------------------------------------------------

        method = getattr(
            question_bank,
            "get_questions_for_field",
            None,
        )

        if callable(method):
            result = None

            try:
                result = method(
                    complaint,
                    field_id,
                    language=language,
                )
            except TypeError:
                try:
                    result = method(
                        complaint,
                        field_id,
                        language,
                    )
                except TypeError:
                    result = method(
                        complaint,
                        field_id,
                    )

            if result is not None:
                if isinstance(result, (list, tuple)):
                    selected = self._select_language_question(
                        result,
                        language,
                    )

                    if selected is not None:
                        return selected

                    # Backwards compatibility:
                    # older question objects may not have language metadata.
                    if result:
                        return result[0]

                else:
                    question_language = self._question_language(result)

                    # Legacy question without language metadata.
                    if question_language is None:
                        return result

                    if question_language == language:
                        return result

        # --------------------------------------------------------------
        # Singular API
        # --------------------------------------------------------------

        method = getattr(
            question_bank,
            "get_question_for_field",
            None,
        )

        if callable(method):
            result = None

            try:
                result = method(
                    complaint,
                    field_id,
                    language=language,
                )
            except TypeError:
                try:
                    result = method(
                        complaint,
                        field_id,
                        language,
                    )
                except TypeError:
                    try:
                        result = method(
                            complaint,
                            field_id,
                        )
                    except (TypeError, ValueError):
                        result = None

            if result is not None:
                if isinstance(result, (list, tuple)):
                    selected = self._select_language_question(
                        result,
                        language,
                    )

                    if selected is not None:
                        return selected

                    # Legacy question objects without language metadata.
                    if result:
                        return result[0]

                else:
                    question_language = self._question_language(result)

                    if question_language is None:
                        return result

                    if question_language == language:
                        return result

        # --------------------------------------------------------------
        # Fallback: retrieve complaint questions
        # --------------------------------------------------------------

        for method_name in (
            "get_questions_for_complaint",
            "get_questions",
        ):
            method = getattr(
                question_bank,
                method_name,
                None,
            )

            if not callable(method):
                continue

            try:
                questions = method(
                    complaint,
                    language=language,
                ) or []
            except TypeError:
                questions = method(complaint) or []

            matching = [
                question
                for question in questions
                if self._question_field_id(question) == field_id
            ]

            if not matching:
                continue

            selected = self._select_language_question(
                matching,
                language,
            )

            if selected is not None:
                return selected

            # Legacy questions may not expose language.
            for question in matching:
                if self._question_language(question) is None:
                    return question

        return None

    # ------------------------------------------------------------------
    # Question helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _question_language(
        question: Any,
    ) -> QuestionLanguage | None:
        """Extract the QuestionLanguage from a question."""

        if question is None:
            return None

        value = getattr(
            question,
            "language",
            None,
        )

        if isinstance(value, QuestionLanguage):
            return value

        if isinstance(value, str):
            aliases = {
                "en": QuestionLanguage.ENGLISH,
                "english": QuestionLanguage.ENGLISH,
                "hi": QuestionLanguage.HINDI,
                "hindi": QuestionLanguage.HINDI,
                "bn": QuestionLanguage.BENGALI,
                "bengali": QuestionLanguage.BENGALI,
                "mr": QuestionLanguage.MARATHI,
                "marathi": QuestionLanguage.MARATHI,
            }

            return aliases.get(
                value.strip().lower()
            )

        return None

    @classmethod
    def _select_language_question(
        cls,
        questions: Iterable[Any],
        language: QuestionLanguage,
    ) -> Any | None:
        """
        Select the first question matching the requested language.

        Returns None when no question contains matching language metadata.
        """

        for question in questions:
            if cls._question_language(question) == language:
                return question

        return None

    @staticmethod
    def _question_field_id(
        question: Any,
    ) -> str | None:
        """Extract the ontology field ID from a question."""

        if question is None:
            return None

        for attribute in (
            "field_id",
            "clinical_field",
            "ontology_field",
            "field",
        ):
            value = getattr(
                question,
                attribute,
                None,
            )

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
                nested = getattr(
                    value,
                    nested_attribute,
                    None,
                )

                if nested is not None:
                    return str(nested)

            return str(value)

        return None
    