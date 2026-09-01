"""Tests for the MediKiosk Question Bank."""

import pytest

from ai.conversation.question_bank import (
    Question,
    QuestionLanguage,
    get_question,
    get_question_bank,
    get_questions_for_complaint,
    get_questions_for_field,
    get_supported_complaints,
    get_supported_languages,
    validate_question_bank,
)


SUPPORTED_COMPLAINTS = (
    "fever",
    "chest_pain",
    "cough",
    "headache",
    "abdominal_pain",
)


EXPECTED_FIELDS = {
    "fever": {
        "onset",
        "duration",
        "severity",
        "temperature",
        "chills",
        "sweating",
        "headache",
        "cough",
        "associated_symptoms",
    },
    "chest_pain": {
        "onset",
        "location",
        "character",
        "duration",
        "radiation",
        "aggravating_factors",
        "relieving_factors",
        "severity",
        "associated_symptoms",
    },
    "cough": {
        "onset",
        "duration",
        "severity",
        "nature",
        "sputum",
        "sputum_characteristics",
        "blood_presence",
        "associated_symptoms",
        "aggravating_factors",
    },
    "headache": {
        "onset",
        "duration",
        "location",
        "character",
        "severity",
        "frequency_pattern",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    },
    "abdominal_pain": {
        "onset",
        "location",
        "character",
        "duration",
        "severity",
        "radiation",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
        "bowel_related_symptoms",
        "vomiting_nausea",
    },
}


def test_question_bank_imports_successfully():
    bank = get_question_bank()

    assert isinstance(bank, dict)
    assert bank


def test_all_supported_complaints_have_questions():
    bank = get_question_bank()

    assert set(SUPPORTED_COMPLAINTS).issubset(bank.keys())

    for complaint in SUPPORTED_COMPLAINTS:
        assert bank[complaint]


@pytest.mark.parametrize("complaint", SUPPORTED_COMPLAINTS)
def test_complaint_has_questions_for_expected_ontology_fields(complaint):
    questions = get_questions_for_complaint(complaint)

    actual_fields = {question.field_id for question in questions}

    assert EXPECTED_FIELDS[complaint].issubset(actual_fields)


@pytest.mark.parametrize("complaint", SUPPORTED_COMPLAINTS)
def test_no_question_references_nonexistent_expected_field(complaint):
    questions = get_questions_for_complaint(complaint)

    actual_fields = {question.field_id for question in questions}

    assert actual_fields.issubset(EXPECTED_FIELDS[complaint])


@pytest.mark.parametrize("complaint", SUPPORTED_COMPLAINTS)
def test_english_questions_are_available(complaint):
    questions = get_questions_for_complaint(
        complaint,
        language=QuestionLanguage.ENGLISH,
    )

    assert questions
    assert all(
        question.language == QuestionLanguage.ENGLISH
        for question in questions
    )


@pytest.mark.parametrize("complaint", SUPPORTED_COMPLAINTS)
def test_hindi_questions_are_available(complaint):
    questions = get_questions_for_complaint(
        complaint,
        language=QuestionLanguage.HINDI,
    )

    assert questions
    assert all(
        question.language == QuestionLanguage.HINDI
        for question in questions
    )


def test_multiple_language_versions_map_to_same_field():
    questions = get_questions_for_field(
        "fever",
        "duration",
    )

    fields = {question.field_id for question in questions}
    languages = {question.language for question in questions}

    assert fields == {"duration"}
    assert QuestionLanguage.ENGLISH in languages
    assert QuestionLanguage.HINDI in languages


def test_multiple_questions_can_exist_for_one_field():
    questions = get_questions_for_field(
        "fever",
        "duration",
    )

    assert len(questions) >= 2


def test_question_ids_are_unique():
    questions = [
        question
        for complaint in get_supported_complaints()
        for question in get_questions_for_complaint(complaint)
    ]

    question_ids = [question.question_id for question in questions]

    assert len(question_ids) == len(set(question_ids))


def test_question_ids_can_retrieve_questions():
    questions = get_questions_for_complaint("fever")

    for question in questions:
        retrieved = get_question(question.question_id)

        assert retrieved == question


def test_retrieval_is_deterministic():
    first = get_questions_for_complaint("fever")
    second = get_questions_for_complaint("fever")

    assert first == second


def test_field_retrieval_is_deterministic():
    first = get_questions_for_field("chest_pain", "severity")
    second = get_questions_for_field("chest_pain", "severity")

    assert first == second


def test_question_order_follows_priority():
    questions = get_questions_for_complaint("fever")

    priorities = [question.priority for question in questions]

    assert priorities == sorted(priorities)


def test_unknown_complaint_is_explicitly_rejected():
    with pytest.raises(ValueError, match="Unknown complaint"):
        get_questions_for_complaint("unknown_complaint")


def test_unknown_field_is_explicitly_rejected():
    with pytest.raises(ValueError, match="Unknown field"):
        get_questions_for_field(
            "fever",
            "does_not_exist",
        )


def test_unknown_question_id_is_explicitly_rejected():
    with pytest.raises(ValueError, match="Unknown question ID"):
        get_question("does_not_exist")


def test_language_filter_does_not_mix_languages():
    english = get_questions_for_complaint(
        "fever",
        language="en",
    )

    hindi = get_questions_for_complaint(
        "fever",
        language="hi",
    )

    assert english
    assert hindi

    assert all(
        question.language == QuestionLanguage.ENGLISH
        for question in english
    )

    assert all(
        question.language == QuestionLanguage.HINDI
        for question in hindi
    )


def test_question_objects_have_required_structure():
    questions = get_questions_for_complaint("fever")

    for question in questions:
        assert isinstance(question, Question)
        assert question.question_id
        assert question.field_id
        assert question.text
        assert question.language
        assert question.answer_type


def test_supported_complaints_are_deterministic():
    first = get_supported_complaints()
    second = get_supported_complaints()

    assert first == second
    assert set(first) == set(SUPPORTED_COMPLAINTS)


def test_supported_languages_include_english_and_hindi():
    languages = get_supported_languages()

    assert QuestionLanguage.ENGLISH in languages
    assert QuestionLanguage.HINDI in languages


def test_question_bank_validation_passes():
    # Should raise nothing.
    validate_question_bank()


def test_no_network_dependency():
    """
    Structural smoke test ensuring the Question Bank can be used directly
    without any provider/API setup.
    """

    questions = get_questions_for_complaint("headache")

    assert questions