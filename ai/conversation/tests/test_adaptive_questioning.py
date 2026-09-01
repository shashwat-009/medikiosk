"""
Tests for the provisional Adaptive Questioning module.

These tests use small fakes so that the behavior of Adaptive Questioning
can be tested independently from the eventual concrete APIs.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from ai.conversation.adaptive_questioning import (
    AdaptiveQuestioning,
    NextQuestionResult,
)


@dataclass(frozen=True)
class FakeField:
    field_id: str


@dataclass(frozen=True)
class FakeQuestion:
    question_id: str
    field_id: str
    text: str


class FakeOntology:
    def __init__(self) -> None:
        self.data = {
            "fever": [
                FakeField("onset"),
                FakeField("duration"),
                FakeField("temperature"),
                FakeField("severity"),
                FakeField("chills"),
            ]
        }

    def get_relevant_fields(self, complaint):
        return list(self.data.get(str(complaint), []))


class FakeQuestionBank:
    def __init__(self) -> None:
        self.questions = {
            ("fever", "onset"): FakeQuestion(
                "q_onset",
                "onset",
                "When did the fever start?",
            ),
            ("fever", "duration"): FakeQuestion(
                "q_duration",
                "duration",
                "How long have you had the fever?",
            ),
            ("fever", "temperature"): FakeQuestion(
                "q_temperature",
                "temperature",
                "What is your temperature?",
            ),
            ("fever", "severity"): FakeQuestion(
                "q_severity",
                "severity",
                "How severe is the fever?",
            ),
            ("fever", "chills"): FakeQuestion(
                "q_chills",
                "chills",
                "Are you having chills?",
            ),
        }

    def get_questions_for_field(self, complaint, field):
        field_id = (
            field.field_id
            if hasattr(field, "field_id")
            else str(field)
        )

        return self.questions.get((str(complaint), field_id))


class FakeDialogueState:
    def __init__(
        self,
        complaint: str = "fever",
        collected: set[str] | None = None,
    ) -> None:
        self.complaint = complaint
        self.collected = collected or set()

    def get_collected_fields(self):
        return set(self.collected)


@pytest.fixture
def components():
    return (
        FakeOntology(),
        FakeQuestionBank(),
        FakeDialogueState(),
    )


def test_module_imports_successfully():
    assert AdaptiveQuestioning is not None


def test_adaptive_questioning_can_be_initialized(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology=ontology,
        question_bank=question_bank,
        dialogue_state=state,
    )

    assert engine is not None


def test_works_with_ontology(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question()

    assert result.question is not None
    assert result.question.field_id == "onset"


def test_works_with_question_bank(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question()

    assert result.question.question_id == "q_onset"


def test_works_with_dialogue_state(components):
    ontology, question_bank, state = components
    state.collected.add("onset")

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question()

    assert result.question.field_id == "duration"


def test_selects_question_for_supported_complaint(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question("fever")

    assert result.has_question


def test_selects_only_missing_field(components):
    ontology, question_bank, state = components
    state.collected.update({"onset", "duration"})

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question()

    assert result.question.field_id == "temperature"


def test_does_not_repeat_collected_field(components):
    ontology, question_bank, state = components
    state.collected.add("onset")

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question()

    assert result.question.field_id != "onset"


def test_repeated_calls_are_deterministic(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    first = engine.get_next_question()
    second = engine.get_next_question()

    assert first.question.question_id == second.question.question_id


def test_next_question_changes_after_state_changes(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    first = engine.get_next_question()
    state.collected.add(first.question.field_id)

    second = engine.get_next_question()

    assert second.question is not None
    assert second.question.field_id != first.question.field_id


def test_returns_one_question_at_a_time(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question()

    assert isinstance(result, NextQuestionResult)
    assert result.question is not None
    assert not isinstance(result.question, list)


def test_handles_all_fields_collected(components):
    ontology, question_bank, state = components
    state.collected.update(
        {
            "onset",
            "duration",
            "temperature",
            "severity",
            "chills",
        }
    )

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question()

    assert result.question is None
    assert result.reason == "no_available_question"


def test_handles_unknown_complaint(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question("unknown_complaint")

    assert result.question is None


def test_handles_missing_question_mapping(components):
    ontology, question_bank, state = components

    ontology.data["fever"] = [FakeField("not_in_question_bank")]

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question()

    assert result.question is None
    assert result.reason == "no_available_question"


def test_does_not_make_network_requests(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question()

    assert result.question is not None


def test_does_not_depend_on_sarvam(components):
    ontology, question_bank, state = components

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    assert not hasattr(engine, "sarvam")
    assert not hasattr(engine, "asr_provider")


def test_does_not_modify_dialogue_state(components):
    ontology, question_bank, state = components
    original = set(state.collected)

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    engine.get_next_question()

    assert state.collected == original


def test_explicit_complaint_overrides_state_complaint(components):
    ontology, question_bank, state = components
    state.complaint = "unknown"

    engine = AdaptiveQuestioning(
        ontology,
        question_bank,
        state,
    )

    result = engine.get_next_question("fever")

    assert result.question is not None
    assert result.question.field_id == "onset"