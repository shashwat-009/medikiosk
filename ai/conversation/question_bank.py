"""
MediKiosk Question Bank.

Provides deterministic, curated questions for clinical history-taking.

Architecture:
    Clinical Ontology
          ↓
    Question Bank
          ↓
    Future Adaptive Questioning

This module intentionally does NOT:
- decide the next question
- perform adaptive branching
- perform diagnosis
- perform red-flag detection
- call an LLM
- call external APIs
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------


class QuestionLanguage(str, Enum):
    """Languages currently supported by the question bank."""

    ENGLISH = "en"
    HINDI = "hi"


# ---------------------------------------------------------------------------
# Internal question representation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Question:
    """
    A single curated clinical question.

    Questions belonging to different languages but sharing the same
    field_id represent alternative ways of asking for the same
    clinical information.
    """

    question_id: str
    field_id: str
    text: str
    language: QuestionLanguage
    answer_type: str = "text"
    options: tuple[str, ...] = ()
    priority: int = 0
    enabled: bool = True


# ---------------------------------------------------------------------------
# Ontology field definitions
#
# These identifiers must match ontology.py exactly.
# ---------------------------------------------------------------------------


FEVER_FIELDS = (
    "onset",
    "duration",
    "severity",
    "temperature",
    "chills",
    "sweating",
    "headache",
    "cough",
    "associated_symptoms",
)

CHEST_PAIN_FIELDS = (
    "onset",
    "location",
    "character",
    "duration",
    "radiation",
    "aggravating_factors",
    "relieving_factors",
    "severity",
    "associated_symptoms",
)

COUGH_FIELDS = (
    "onset",
    "duration",
    "severity",
    "nature",
    "sputum",
    "sputum_characteristics",
    "blood_presence",
    "associated_symptoms",
    "aggravating_factors",
)

HEADACHE_FIELDS = (
    "onset",
    "duration",
    "location",
    "character",
    "severity",
    "frequency_pattern",
    "aggravating_factors",
    "relieving_factors",
    "associated_symptoms",
)

ABDOMINAL_PAIN_FIELDS = (
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
)


# ---------------------------------------------------------------------------
# Curated Question Bank
# ---------------------------------------------------------------------------


def _build_question_bank() -> dict[str, tuple[Question, ...]]:
    """
    Construct the immutable question bank.

    The returned structure preserves insertion order, giving deterministic
    question retrieval.
    """

    return {
        # ===================================================================
        # FEVER
        # ===================================================================
        "fever": (
            Question(
                "fever_onset_en",
                "onset",
                "When did the fever start?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=10,
            ),
            Question(
                "fever_onset_hi",
                "onset",
                "Bukhar kab shuru hua?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=10,
            ),
            Question(
                "fever_duration_en",
                "duration",
                "How long have you had the fever?",
                QuestionLanguage.ENGLISH,
                answer_type="duration",
                priority=20,
            ),
            Question(
                "fever_duration_hi",
                "duration",
                "Aapko bukhar kab se hai?",
                QuestionLanguage.HINDI,
                answer_type="duration",
                priority=20,
            ),
            Question(
                "fever_severity_en",
                "severity",
                "How severe is the fever?",
                QuestionLanguage.ENGLISH,
                answer_type="scale",
                priority=30,
            ),
            Question(
                "fever_severity_hi",
                "severity",
                "Bukhar kitna tez hai?",
                QuestionLanguage.HINDI,
                answer_type="scale",
                priority=30,
            ),
            Question(
                "fever_temperature_en",
                "temperature",
                "What is your highest recorded temperature?",
                QuestionLanguage.ENGLISH,
                answer_type="number",
                priority=40,
            ),
            Question(
                "fever_temperature_hi",
                "temperature",
                "Aapka sabse zyada temperature kitna raha hai?",
                QuestionLanguage.HINDI,
                answer_type="number",
                priority=40,
            ),
            Question(
                "fever_chills_en",
                "chills",
                "Do you have chills or feel unusually cold?",
                QuestionLanguage.ENGLISH,
                answer_type="boolean",
                priority=50,
            ),
            Question(
                "fever_chills_hi",
                "chills",
                "Kya aapko thand ya kapkapi lagti hai?",
                QuestionLanguage.HINDI,
                answer_type="boolean",
                priority=50,
            ),
            Question(
                "fever_sweating_en",
                "sweating",
                "Have you been having unusual sweating?",
                QuestionLanguage.ENGLISH,
                answer_type="boolean",
                priority=60,
            ),
            Question(
                "fever_sweating_hi",
                "sweating",
                "Kya aapko zyada pasina aa raha hai?",
                QuestionLanguage.HINDI,
                answer_type="boolean",
                priority=60,
            ),
            Question(
                "fever_headache_en",
                "headache",
                "Do you also have a headache?",
                QuestionLanguage.ENGLISH,
                answer_type="boolean",
                priority=70,
            ),
            Question(
                "fever_headache_hi",
                "headache",
                "Kya aapko sir dard bhi hai?",
                QuestionLanguage.HINDI,
                answer_type="boolean",
                priority=70,
            ),
            Question(
                "fever_cough_en",
                "cough",
                "Do you also have a cough?",
                QuestionLanguage.ENGLISH,
                answer_type="boolean",
                priority=80,
            ),
            Question(
                "fever_cough_hi",
                "cough",
                "Kya aapko khaansi bhi hai?",
                QuestionLanguage.HINDI,
                answer_type="boolean",
                priority=80,
            ),
            Question(
                "fever_associated_symptoms_en",
                "associated_symptoms",
                "Do you have any other symptoms along with the fever?",
                QuestionLanguage.ENGLISH,
                answer_type="multiple_choice",
                priority=90,
            ),
            Question(
                "fever_associated_symptoms_hi",
                "associated_symptoms",
                "Bukhar ke saath aur koi lakshan hain?",
                QuestionLanguage.HINDI,
                answer_type="multiple_choice",
                priority=90,
            ),
        ),

        # ===================================================================
        # CHEST PAIN
        # ===================================================================
        "chest_pain": (
            Question(
                "chest_pain_onset_en",
                "onset",
                "When did the chest pain start?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=10,
            ),
            Question(
                "chest_pain_onset_hi",
                "onset",
                "Seene mein dard kab shuru hua?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=10,
            ),
            Question(
                "chest_pain_location_en",
                "location",
                "Where exactly is the chest pain?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=20,
            ),
            Question(
                "chest_pain_location_hi",
                "location",
                "Seene mein dard exactly kahan ho raha hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=20,
            ),
            Question(
                "chest_pain_character_en",
                "character",
                "What does the chest pain feel like?",
                QuestionLanguage.ENGLISH,
                answer_type="single_choice",
                options=(
                    "Pressure",
                    "Tightness",
                    "Burning",
                    "Sharp",
                    "Other",
                ),
                priority=30,
            ),
            Question(
                "chest_pain_character_hi",
                "character",
                "Seene ka dard kaisa mehsoos hota hai?",
                QuestionLanguage.HINDI,
                answer_type="single_choice",
                options=(
                    "Dabav",
                    "Kasav",
                    "Jalan",
                    "Tez chubhne wala",
                    "Kuch aur",
                ),
                priority=30,
            ),
            Question(
                "chest_pain_duration_en",
                "duration",
                "How long does each episode of chest pain last?",
                QuestionLanguage.ENGLISH,
                answer_type="duration",
                priority=40,
            ),
            Question(
                "chest_pain_duration_hi",
                "duration",
                "Seene ka dard ek baar mein kitni der rehta hai?",
                QuestionLanguage.HINDI,
                answer_type="duration",
                priority=40,
            ),
            Question(
                "chest_pain_radiation_en",
                "radiation",
                "Does the pain spread to your arm, shoulder, back, neck, or jaw?",
                QuestionLanguage.ENGLISH,
                answer_type="multiple_choice",
                priority=50,
            ),
            Question(
                "chest_pain_radiation_hi",
                "radiation",
                "Kya dard haath, kandhe, peeth, gardan ya jabde tak jaata hai?",
                QuestionLanguage.HINDI,
                answer_type="multiple_choice",
                priority=50,
            ),
            Question(
                "chest_pain_aggravating_en",
                "aggravating_factors",
                "What makes the chest pain worse?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=60,
            ),
            Question(
                "chest_pain_aggravating_hi",
                "aggravating_factors",
                "Kis cheez se seene ka dard badhta hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=60,
            ),
            Question(
                "chest_pain_relieving_en",
                "relieving_factors",
                "What makes the chest pain better?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=70,
            ),
            Question(
                "chest_pain_relieving_hi",
                "relieving_factors",
                "Kis cheez se seene ka dard kam hota hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=70,
            ),
            Question(
                "chest_pain_severity_en",
                "severity",
                "On a scale from 0 to 10, how severe is the chest pain?",
                QuestionLanguage.ENGLISH,
                answer_type="scale",
                priority=80,
            ),
            Question(
                "chest_pain_severity_hi",
                "severity",
                "0 se 10 ke scale par seene ka dard kitna hai?",
                QuestionLanguage.HINDI,
                answer_type="scale",
                priority=80,
            ),
            Question(
                "chest_pain_associated_en",
                "associated_symptoms",
                "Do you have any other symptoms along with the chest pain?",
                QuestionLanguage.ENGLISH,
                answer_type="multiple_choice",
                priority=90,
            ),
            Question(
                "chest_pain_associated_hi",
                "associated_symptoms",
                "Seene ke dard ke saath aur koi lakshan hain?",
                QuestionLanguage.HINDI,
                answer_type="multiple_choice",
                priority=90,
            ),
        ),

        # ===================================================================
        # COUGH
        # ===================================================================
        "cough": (
            Question(
                "cough_onset_en",
                "onset",
                "When did the cough start?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=10,
            ),
            Question(
                "cough_onset_hi",
                "onset",
                "Khaansi kab shuru hui?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=10,
            ),
            Question(
                "cough_duration_en",
                "duration",
                "How long have you had the cough?",
                QuestionLanguage.ENGLISH,
                answer_type="duration",
                priority=20,
            ),
            Question(
                "cough_duration_hi",
                "duration",
                "Aapko khaansi kab se hai?",
                QuestionLanguage.HINDI,
                answer_type="duration",
                priority=20,
            ),
            Question(
                "cough_severity_en",
                "severity",
                "How severe is the cough?",
                QuestionLanguage.ENGLISH,
                answer_type="scale",
                priority=30,
            ),
            Question(
                "cough_severity_hi",
                "severity",
                "Khaansi kitni zyada hai?",
                QuestionLanguage.HINDI,
                answer_type="scale",
                priority=30,
            ),
            Question(
                "cough_type_en",
                "nature",
                "Is your cough dry or does it produce mucus?",
                QuestionLanguage.ENGLISH,
                answer_type="single_choice",
                options=("Dry", "With mucus"),
                priority=40,
            ),
            Question(
                "cough_type_hi",
                "nature",
                "Aapki khaansi sookhi hai ya balgam ke saath hai?",
                QuestionLanguage.HINDI,
                answer_type="single_choice",
                options=("Sookhi", "Balgam ke saath"),
                priority=40,
            ),
            Question(
                "cough_sputum_en",
                "sputum",
                "Are you coughing up sputum or mucus?",
                QuestionLanguage.ENGLISH,
                answer_type="boolean",
                priority=50,
            ),
            Question(
                "cough_sputum_hi",
                "sputum",
                "Kya khaansi ke saath balgam nikalta hai?",
                QuestionLanguage.HINDI,
                answer_type="boolean",
                priority=50,
            ),
            Question(
                "cough_sputum_characteristics_en",
                "sputum_characteristics",
                "What does the sputum look like?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=60,
            ),
            Question(
                "cough_sputum_characteristics_hi",
                "sputum_characteristics",
                "Balgam ka rang ya roop kaisa hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=60,
            ),
            Question(
                "cough_blood_en",
                "blood_presence",
                "Have you noticed blood when coughing?",
                QuestionLanguage.ENGLISH,
                answer_type="boolean",
                priority=70,
            ),
            Question(
                "cough_blood_hi",
                "blood_presence",
                "Kya khaansi ke saath khoon aaya hai?",
                QuestionLanguage.HINDI,
                answer_type="boolean",
                priority=70,
            ),
            Question(
                "cough_associated_en",
                "associated_symptoms",
                "Do you have any other symptoms along with the cough?",
                QuestionLanguage.ENGLISH,
                answer_type="multiple_choice",
                priority=80,
            ),
            Question(
                "cough_associated_hi",
                "associated_symptoms",
                "Khaansi ke saath aur koi lakshan hain?",
                QuestionLanguage.HINDI,
                answer_type="multiple_choice",
                priority=80,
            ),
            Question(
                "cough_aggravating_en",
                "aggravating_factors",
                "What makes your cough worse?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=90,
            ),
            Question(
                "cough_aggravating_hi",
                "aggravating_factors",
                "Kis cheez se aapki khaansi badh jaati hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=90,
            ),
        ),

        # ===================================================================
        # HEADACHE
        # ===================================================================
        "headache": (
            Question(
                "headache_onset_en",
                "onset",
                "When did the headache start?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=10,
            ),
            Question(
                "headache_onset_hi",
                "onset",
                "Sir dard kab shuru hua?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=10,
            ),
            Question(
                "headache_duration_en",
                "duration",
                "How long does the headache usually last?",
                QuestionLanguage.ENGLISH,
                answer_type="duration",
                priority=20,
            ),
            Question(
                "headache_duration_hi",
                "duration",
                "Sir dard aam taur par kitni der rehta hai?",
                QuestionLanguage.HINDI,
                answer_type="duration",
                priority=20,
            ),
            Question(
                "headache_location_en",
                "location",
                "Where exactly do you feel the headache?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=30,
            ),
            Question(
                "headache_location_hi",
                "location",
                "Sir mein dard exactly kahan hota hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=30,
            ),
            Question(
                "headache_character_en",
                "character",
                "What does the headache feel like?",
                QuestionLanguage.ENGLISH,
                answer_type="single_choice",
                options=(
                    "Throbbing",
                    "Pressure",
                    "Sharp",
                    "Dull",
                    "Other",
                ),
                priority=40,
            ),
            Question(
                "headache_character_hi",
                "character",
                "Sir ka dard kaisa mehsoos hota hai?",
                QuestionLanguage.HINDI,
                answer_type="single_choice",
                options=(
                    "Dhadakne wala",
                    "Dabav jaisa",
                    "Tez",
                    "Halka lagataar dard",
                    "Kuch aur",
                ),
                priority=40,
            ),
            Question(
                "headache_severity_en",
                "severity",
                "On a scale from 0 to 10, how severe is the headache?",
                QuestionLanguage.ENGLISH,
                answer_type="scale",
                priority=50,
            ),
            Question(
                "headache_severity_hi",
                "severity",
                "0 se 10 ke scale par sir dard kitna hai?",
                QuestionLanguage.HINDI,
                answer_type="scale",
                priority=50,
            ),
            Question(
                "headache_frequency_en",
                "frequency_pattern",
                "How often do you get these headaches?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=60,
            ),
            Question(
                "headache_frequency_hi",
                "frequency_pattern",
                "Aapko ye sir dard kitni baar hota hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=60,
            ),
            Question(
                "headache_aggravating_en",
                "aggravating_factors",
                "What makes the headache worse?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=70,
            ),
            Question(
                "headache_aggravating_hi",
                "aggravating_factors",
                "Kis cheez se sir dard badhta hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=70,
            ),
            Question(
                "headache_relieving_en",
                "relieving_factors",
                "What makes the headache better?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=80,
            ),
            Question(
                "headache_relieving_hi",
                "relieving_factors",
                "Kis cheez se sir dard kam hota hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=80,
            ),
            Question(
                "headache_associated_en",
                "associated_symptoms",
                "Do you have any other symptoms with the headache?",
                QuestionLanguage.ENGLISH,
                answer_type="multiple_choice",
                priority=90,
            ),
            Question(
                "headache_associated_hi",
                "associated_symptoms",
                "Sir dard ke saath aur koi lakshan hain?",
                QuestionLanguage.HINDI,
                answer_type="multiple_choice",
                priority=90,
            ),
        ),

        # ===================================================================
        # ABDOMINAL PAIN
        # ===================================================================
        "abdominal_pain": (
            Question(
                "abdominal_pain_onset_en",
                "onset",
                "When did the abdominal pain start?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=10,
            ),
            Question(
                "abdominal_pain_onset_hi",
                "onset",
                "Pet mein dard kab shuru hua?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=10,
            ),
            Question(
                "abdominal_pain_location_en",
                "location",
                "Where exactly is the abdominal pain?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=20,
            ),
            Question(
                "abdominal_pain_location_hi",
                "location",
                "Pet mein dard exactly kahan ho raha hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=20,
            ),
            Question(
                "abdominal_pain_character_en",
                "character",
                "What does the abdominal pain feel like?",
                QuestionLanguage.ENGLISH,
                answer_type="single_choice",
                options=(
                    "Cramping",
                    "Burning",
                    "Sharp",
                    "Dull",
                    "Other",
                ),
                priority=30,
            ),
            Question(
                "abdominal_pain_character_hi",
                "character",
                "Pet ka dard kaisa mehsoos hota hai?",
                QuestionLanguage.HINDI,
                answer_type="single_choice",
                options=(
                    "Ainthan",
                    "Jalan",
                    "Tez",
                    "Halka lagataar dard",
                    "Kuch aur",
                ),
                priority=30,
            ),
            Question(
                "abdominal_pain_duration_en",
                "duration",
                "How long have you had the abdominal pain?",
                QuestionLanguage.ENGLISH,
                answer_type="duration",
                priority=40,
            ),
            Question(
                "abdominal_pain_duration_hi",
                "duration",
                "Pet mein dard kab se hai?",
                QuestionLanguage.HINDI,
                answer_type="duration",
                priority=40,
            ),
            Question(
                "abdominal_pain_severity_en",
                "severity",
                "On a scale from 0 to 10, how severe is the abdominal pain?",
                QuestionLanguage.ENGLISH,
                answer_type="scale",
                priority=50,
            ),
            Question(
                "abdominal_pain_severity_hi",
                "severity",
                "0 se 10 ke scale par pet ka dard kitna hai?",
                QuestionLanguage.HINDI,
                answer_type="scale",
                priority=50,
            ),
            Question(
                "abdominal_pain_radiation_en",
                "radiation",
                "Does the abdominal pain spread to another part of your body?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=60,
            ),
            Question(
                "abdominal_pain_radiation_hi",
                "radiation",
                "Kya pet ka dard sharir ke kisi aur hisse tak jaata hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=60,
            ),
            Question(
                "abdominal_pain_aggravating_en",
                "aggravating_factors",
                "What makes the abdominal pain worse?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=70,
            ),
            Question(
                "abdominal_pain_aggravating_hi",
                "aggravating_factors",
                "Kis cheez se pet ka dard badhta hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=70,
            ),
            Question(
                "abdominal_pain_relieving_en",
                "relieving_factors",
                "What makes the abdominal pain better?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=80,
            ),
            Question(
                "abdominal_pain_relieving_hi",
                "relieving_factors",
                "Kis cheez se pet ka dard kam hota hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=80,
            ),
            Question(
                "abdominal_pain_associated_en",
                "associated_symptoms",
                "Do you have any other symptoms along with the abdominal pain?",
                QuestionLanguage.ENGLISH,
                answer_type="multiple_choice",
                priority=90,
            ),
            Question(
                "abdominal_pain_associated_hi",
                "associated_symptoms",
                "Pet ke dard ke saath aur koi lakshan hain?",
                QuestionLanguage.HINDI,
                answer_type="multiple_choice",
                priority=90,
            ),
            Question(
                "abdominal_bowel_en",
                "bowel_related_symptoms",
                "Have you noticed any changes in your bowel movements?",
                QuestionLanguage.ENGLISH,
                answer_type="text",
                priority=100,
            ),
            Question(
                "abdominal_bowel_hi",
                "bowel_related_symptoms",
                "Kya aapke mal tyag mein koi badlav hua hai?",
                QuestionLanguage.HINDI,
                answer_type="text",
                priority=100,
            ),
            Question(
                "abdominal_nausea_en",
                "vomiting_nausea",
                "Have you had nausea or vomiting?",
                QuestionLanguage.ENGLISH,
                answer_type="boolean",
                priority=110,
            ),
            Question(
                "abdominal_nausea_hi",
                "vomiting_nausea",
                "Kya aapko ji michlane ya ulti ki shikayat hai?",
                QuestionLanguage.HINDI,
                answer_type="boolean",
                priority=110,
            ),
        ),
    }


# Build once at module load. The public API never mutates this structure.
_QUESTION_BANK = _build_question_bank()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_question_bank() -> dict[str, tuple[Question, ...]]:
    """
    Return the complete question bank.

    A shallow copy of the mapping is returned so callers cannot replace
    complaint-level entries in the module-level registry.
    """

    return dict(_QUESTION_BANK)


def get_questions_for_complaint(
    complaint: str,
    *,
    language: Optional[QuestionLanguage | str] = None,
) -> tuple[Question, ...]:
    """
    Return all questions for a complaint.

    Args:
        complaint: Complaint identifier, e.g. ``fever``.
        language: Optional language filter.

    Raises:
        ValueError: If the complaint is unknown.
    """

    key = _normalise_complaint(complaint)

    if key not in _QUESTION_BANK:
        raise ValueError(f"Unknown complaint: {complaint!r}")

    questions = _QUESTION_BANK[key]

    if language is None:
        return questions

    selected_language = _normalise_language(language)

    return tuple(
        question
        for question in questions
        if question.language == selected_language
    )


def get_questions_for_field(
    complaint: str,
    field: str,
    *,
    language: Optional[QuestionLanguage | str] = None,
) -> tuple[Question, ...]:
    """
    Return all questions belonging to one ontology field.

    Raises:
        ValueError: If the complaint or field is unknown.
    """

    key = _normalise_complaint(complaint)

    if key not in _QUESTION_BANK:
        raise ValueError(f"Unknown complaint: {complaint!r}")

    field_key = _normalise_field(field)

    questions = tuple(
        question
        for question in _QUESTION_BANK[key]
        if question.field_id == field_key
    )

    if not questions:
        raise ValueError(
            f"Unknown field {field!r} for complaint {complaint!r}"
        )

    if language is not None:
        selected_language = _normalise_language(language)
        questions = tuple(
            question
            for question in questions
            if question.language == selected_language
        )

    return questions


def get_question(question_id: str) -> Question:
    """
    Retrieve one question by its unique ID.

    Raises:
        ValueError: If the question ID is unknown.
    """

    for questions in _QUESTION_BANK.values():
        for question in questions:
            if question.question_id == question_id:
                return question

    raise ValueError(f"Unknown question ID: {question_id!r}")


def get_supported_complaints() -> tuple[str, ...]:
    """Return supported complaint identifiers in deterministic order."""

    return tuple(_QUESTION_BANK.keys())


def get_supported_languages() -> tuple[QuestionLanguage, ...]:
    """Return currently supported question languages."""

    return tuple(QuestionLanguage)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_question_bank() -> None:
    """
    Validate structural invariants of the question bank.

    This function intentionally performs structural validation only.
    Clinical correctness remains the responsibility of the ontology/content
    review process.
    """

    question_ids: set[str] = set()

    for complaint, questions in _QUESTION_BANK.items():
        if not questions:
            raise ValueError(
                f"Complaint {complaint!r} has no questions."
            )

        for question in questions:
            if question.question_id in question_ids:
                raise ValueError(
                    f"Duplicate question ID: {question.question_id}"
                )

            question_ids.add(question.question_id)

            if not question.field_id:
                raise ValueError(
                    f"Question {question.question_id} has no field ID."
                )

            if not question.text.strip():
                raise ValueError(
                    f"Question {question.question_id} has empty text."
                )

            if not question.enabled:
                continue

    # Validate complaint-specific field coverage.
    expected_fields = {
        "fever": set(FEVER_FIELDS),
        "chest_pain": set(CHEST_PAIN_FIELDS),
        "cough": set(COUGH_FIELDS),
        "headache": set(HEADACHE_FIELDS),
        "abdominal_pain": set(ABDOMINAL_PAIN_FIELDS),
    }

    for complaint, fields in expected_fields.items():
        actual_fields = {
            question.field_id
            for question in _QUESTION_BANK[complaint]
        }

        missing = fields - actual_fields

        if missing:
            raise ValueError(
                f"Complaint {complaint!r} is missing fields: "
                f"{sorted(missing)}"
            )


# Validate the static registry immediately.
validate_question_bank()


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


def _normalise_complaint(complaint: str) -> str:
    """Normalise a complaint identifier without silently guessing."""

    if not isinstance(complaint, str):
        raise ValueError("Complaint must be a string.")

    return complaint.strip().lower().replace(" ", "_")


def _normalise_field(field: str) -> str:
    """Normalise an ontology field identifier."""

    if not isinstance(field, str):
        raise ValueError("Field must be a string.")

    return field.strip().lower()


def _normalise_language(
    language: QuestionLanguage | str,
) -> QuestionLanguage:
    """Convert a language string into QuestionLanguage."""

    if isinstance(language, QuestionLanguage):
        return language

    if not isinstance(language, str):
        raise ValueError("Language must be a string or QuestionLanguage.")

    value = language.strip().lower()

    aliases = {
        "english": QuestionLanguage.ENGLISH,
        "en": QuestionLanguage.ENGLISH,
        "hindi": QuestionLanguage.HINDI,
        "hi": QuestionLanguage.HINDI,
    }

    try:
        return aliases[value]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported language: {language!r}"
        ) from exc


__all__ = [
    "Question",
    "QuestionLanguage",
    "get_question_bank",
    "get_questions_for_complaint",
    "get_questions_for_field",
    "get_question",
    "get_supported_complaints",
    "get_supported_languages",
    "validate_question_bank",
]