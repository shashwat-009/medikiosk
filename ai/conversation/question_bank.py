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
    BENGALI = "bn"
    MARATHI = "mr"


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
    # -------------------------------------------------------------------
    # ONSET
    # -------------------------------------------------------------------
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
        "बुखार कब शुरू हुआ?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "fever_onset_bn",
        "onset",
        "জ্বর কখন শুরু হয়েছে?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "fever_onset_mr",
        "onset",
        "ताप कधी सुरू झाला?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=10,
    ),

    # -------------------------------------------------------------------
    # DURATION
    # -------------------------------------------------------------------
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
        "आपको बुखार कब से है?",
        QuestionLanguage.HINDI,
        answer_type="duration",
        priority=20,
    ),
    Question(
        "fever_duration_bn",
        "duration",
        "আপনার কতদিন ধরে জ্বর আছে?",
        QuestionLanguage.BENGALI,
        answer_type="duration",
        priority=20,
    ),
    Question(
        "fever_duration_mr",
        "duration",
        "तुम्हाला किती दिवसांपासून ताप आहे?",
        QuestionLanguage.MARATHI,
        answer_type="duration",
        priority=20,
    ),

    # -------------------------------------------------------------------
    # SEVERITY
    # -------------------------------------------------------------------
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
        "बुखार कितना तेज़ है?",
        QuestionLanguage.HINDI,
        answer_type="scale",
        priority=30,
    ),
    Question(
        "fever_severity_bn",
        "severity",
        "জ্বর কতটা বেশি?",
        QuestionLanguage.BENGALI,
        answer_type="scale",
        priority=30,
    ),
    Question(
        "fever_severity_mr",
        "severity",
        "ताप किती जास्त आहे?",
        QuestionLanguage.MARATHI,
        answer_type="scale",
        priority=30,
    ),

    # -------------------------------------------------------------------
    # TEMPERATURE
    # -------------------------------------------------------------------
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
        "आपका सबसे ज़्यादा तापमान कितना रहा है?",
        QuestionLanguage.HINDI,
        answer_type="number",
        priority=40,
    ),
    Question(
        "fever_temperature_bn",
        "temperature",
        "আপনার সর্বোচ্চ তাপমাত্রা কত ছিল?",
        QuestionLanguage.BENGALI,
        answer_type="number",
        priority=40,
    ),
    Question(
        "fever_temperature_mr",
        "temperature",
        "तुमचे सर्वाधिक तापमान किती होते?",
        QuestionLanguage.MARATHI,
        answer_type="number",
        priority=40,
    ),

    # -------------------------------------------------------------------
    # CHILLS
    # -------------------------------------------------------------------
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
        "क्या आपको ठंड या कंपकंपी लगती है?",
        QuestionLanguage.HINDI,
        answer_type="boolean",
        priority=50,
    ),
    Question(
        "fever_chills_bn",
        "chills",
        "আপনার কি ঠান্ডা লাগা বা কাঁপুনি হয়?",
        QuestionLanguage.BENGALI,
        answer_type="boolean",
        priority=50,
    ),
    Question(
        "fever_chills_mr",
        "chills",
        "तुम्हाला थंडी वाजते किंवा कापरे भरतात का?",
        QuestionLanguage.MARATHI,
        answer_type="boolean",
        priority=50,
    ),

    # -------------------------------------------------------------------
    # SWEATING
    # -------------------------------------------------------------------
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
        "क्या आपको ज़्यादा या असामान्य पसीना आ रहा है?",
        QuestionLanguage.HINDI,
        answer_type="boolean",
        priority=60,
    ),
    Question(
        "fever_sweating_bn",
        "sweating",
        "আপনার কি অস্বাভাবিকভাবে বেশি ঘাম হচ্ছে?",
        QuestionLanguage.BENGALI,
        answer_type="boolean",
        priority=60,
    ),
    Question(
        "fever_sweating_mr",
        "sweating",
        "तुम्हाला नेहमीपेक्षा जास्त घाम येत आहे का?",
        QuestionLanguage.MARATHI,
        answer_type="boolean",
        priority=60,
    ),

    # -------------------------------------------------------------------
    # HEADACHE
    # -------------------------------------------------------------------
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
        "क्या आपको सिरदर्द भी है?",
        QuestionLanguage.HINDI,
        answer_type="boolean",
        priority=70,
    ),
    Question(
        "fever_headache_bn",
        "headache",
        "আপনার কি মাথাব্যথাও আছে?",
        QuestionLanguage.BENGALI,
        answer_type="boolean",
        priority=70,
    ),
    Question(
        "fever_headache_mr",
        "headache",
        "तुम्हाला डोकेदुखीही आहे का?",
        QuestionLanguage.MARATHI,
        answer_type="boolean",
        priority=70,
    ),

    # -------------------------------------------------------------------
    # COUGH
    # -------------------------------------------------------------------
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
        "क्या आपको खाँसी भी है?",
        QuestionLanguage.HINDI,
        answer_type="boolean",
        priority=80,
    ),
    Question(
        "fever_cough_bn",
        "cough",
        "আপনার কি কাশিও আছে?",
        QuestionLanguage.BENGALI,
        answer_type="boolean",
        priority=80,
    ),
    Question(
        "fever_cough_mr",
        "cough",
        "तुम्हाला खोकलाही आहे का?",
        QuestionLanguage.MARATHI,
        answer_type="boolean",
        priority=80,
    ),

    # -------------------------------------------------------------------
    # ASSOCIATED SYMPTOMS
    # -------------------------------------------------------------------
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
        "बुखार के साथ और कोई लक्षण हैं?",
        QuestionLanguage.HINDI,
        answer_type="multiple_choice",
        priority=90,
    ),
    Question(
        "fever_associated_symptoms_bn",
        "associated_symptoms",
        "জ্বরের সঙ্গে কি অন্য কোনো উপসর্গ আছে?",
        QuestionLanguage.BENGALI,
        answer_type="multiple_choice",
        priority=90,
    ),
    Question(
        "fever_associated_symptoms_mr",
        "associated_symptoms",
        "तापासोबत आणखी काही लक्षणे आहेत का?",
        QuestionLanguage.MARATHI,
        answer_type="multiple_choice",
        priority=90,
    ),
),

        # ===================================================================
        # CHEST PAIN
        # ===================================================================
        "chest_pain": (
    # ===================================================================
    # ONSET
    # ===================================================================
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
        "सीने में दर्द कब शुरू हुआ?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "chest_pain_onset_bn",
        "onset",
        "বুকে ব্যথা কখন শুরু হয়েছে?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "chest_pain_onset_mr",
        "onset",
        "छातीत दुखणे कधी सुरू झाले?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=10,
    ),

    # ===================================================================
    # LOCATION
    # ===================================================================
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
        "सीने में दर्द ठीक कहाँ हो रहा है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=20,
    ),
    Question(
        "chest_pain_location_bn",
        "location",
        "বুকের ঠিক কোথায় ব্যথা হচ্ছে?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=20,
    ),
    Question(
        "chest_pain_location_mr",
        "location",
        "छातीत नेमक्या कुठे दुखत आहे?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=20,
    ),

    # ===================================================================
    # CHARACTER
    # ===================================================================
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
        "सीने का दर्द कैसा महसूस होता है?",
        QuestionLanguage.HINDI,
        answer_type="single_choice",
        options=(
            "दबाव",
            "कसाव",
            "जलन",
            "तेज़ चुभने वाला",
            "कुछ और",
        ),
        priority=30,
    ),
    Question(
        "chest_pain_character_bn",
        "character",
        "বুকের ব্যথা কেমন অনুভূত হয়?",
        QuestionLanguage.BENGALI,
        answer_type="single_choice",
        options=(
            "চাপ",
            "টান বা আঁটসাঁট অনুভূতি",
            "জ্বালাপোড়া",
            "তীব্র ব্যথা",
            "অন্য কিছু",
        ),
        priority=30,
    ),
    Question(
        "chest_pain_character_mr",
        "character",
        "छातीतले दुखणे कसे जाणवते?",
        QuestionLanguage.MARATHI,
        answer_type="single_choice",
        options=(
            "दाब",
            "आवळल्यासारखे",
            "जळजळ",
            "तीक्ष्ण वेदना",
            "इतर",
        ),
        priority=30,
    ),

    # ===================================================================
    # DURATION
    # ===================================================================
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
        "सीने का दर्द एक बार में कितनी देर रहता है?",
        QuestionLanguage.HINDI,
        answer_type="duration",
        priority=40,
    ),
    Question(
        "chest_pain_duration_bn",
        "duration",
        "প্রতিবার বুকের ব্যথা কতক্ষণ থাকে?",
        QuestionLanguage.BENGALI,
        answer_type="duration",
        priority=40,
    ),
    Question(
        "chest_pain_duration_mr",
        "duration",
        "छातीतले दुखणे प्रत्येक वेळी किती वेळ टिकते?",
        QuestionLanguage.MARATHI,
        answer_type="duration",
        priority=40,
    ),

    # ===================================================================
    # RADIATION
    # ===================================================================
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
        "क्या दर्द हाथ, कंधे, पीठ, गर्दन या जबड़े तक जाता है?",
        QuestionLanguage.HINDI,
        answer_type="multiple_choice",
        priority=50,
    ),
    Question(
        "chest_pain_radiation_bn",
        "radiation",
        "ব্যথা কি হাত, কাঁধ, পিঠ, ঘাড় বা চোয়ালে ছড়িয়ে পড়ে?",
        QuestionLanguage.BENGALI,
        answer_type="multiple_choice",
        priority=50,
    ),
    Question(
        "chest_pain_radiation_mr",
        "radiation",
        "दुखणे हात, खांदा, पाठ, मान किंवा जबड्यापर्यंत पसरते का?",
        QuestionLanguage.MARATHI,
        answer_type="multiple_choice",
        priority=50,
    ),

    # ===================================================================
    # AGGRAVATING FACTORS
    # ===================================================================
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
        "किस चीज़ से सीने का दर्द बढ़ता है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=60,
    ),
    Question(
        "chest_pain_aggravating_bn",
        "aggravating_factors",
        "কোন কোন কারণে বুকের ব্যথা বেড়ে যায়?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=60,
    ),
    Question(
        "chest_pain_aggravating_mr",
        "aggravating_factors",
        "कशामुळे छातीतले दुखणे वाढते?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=60,
    ),

    # ===================================================================
    # RELIEVING FACTORS
    # ===================================================================
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
        "किस चीज़ से सीने का दर्द कम होता है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=70,
    ),
    Question(
        "chest_pain_relieving_bn",
        "relieving_factors",
        "কী করলে বুকের ব্যথা কমে যায়?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=70,
    ),
    Question(
        "chest_pain_relieving_mr",
        "relieving_factors",
        "कशामुळे छातीतले दुखणे कमी होते?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=70,
    ),

    # ===================================================================
    # SEVERITY
    # ===================================================================
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
        "0 से 10 के स्केल पर सीने का दर्द कितना है?",
        QuestionLanguage.HINDI,
        answer_type="scale",
        priority=80,
    ),
    Question(
        "chest_pain_severity_bn",
        "severity",
        "০ থেকে ১০-এর স্কেলে বুকের ব্যথা কতটা তীব্র?",
        QuestionLanguage.BENGALI,
        answer_type="scale",
        priority=80,
    ),
    Question(
        "chest_pain_severity_mr",
        "severity",
        "० ते १० या मोजपट्टीवर छातीतले दुखणे किती तीव्र आहे?",
        QuestionLanguage.MARATHI,
        answer_type="scale",
        priority=80,
    ),

    # ===================================================================
    # ASSOCIATED SYMPTOMS
    # ===================================================================
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
        "सीने के दर्द के साथ और कोई लक्षण हैं?",
        QuestionLanguage.HINDI,
        answer_type="multiple_choice",
        priority=90,
    ),
    Question(
        "chest_pain_associated_bn",
        "associated_symptoms",
        "বুকের ব্যথার সঙ্গে কি অন্য কোনো উপসর্গ আছে?",
        QuestionLanguage.BENGALI,
        answer_type="multiple_choice",
        priority=90,
    ),
    Question(
        "chest_pain_associated_mr",
        "associated_symptoms",
        "छातीतल्या दुखण्यासोबत आणखी काही लक्षणे आहेत का?",
        QuestionLanguage.MARATHI,
        answer_type="multiple_choice",
        priority=90,
    ),
),
        # ===================================================================
        # COUGH
        # ===================================================================
       "cough": (
    # ===================================================================
    # ONSET
    # ===================================================================
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
        "खाँसी कब शुरू हुई?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "cough_onset_bn",
        "onset",
        "কাশি কখন শুরু হয়েছে?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "cough_onset_mr",
        "onset",
        "खोकला कधी सुरू झाला?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=10,
    ),

    # ===================================================================
    # DURATION
    # ===================================================================
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
        "आपको खाँसी कब से है?",
        QuestionLanguage.HINDI,
        answer_type="duration",
        priority=20,
    ),
    Question(
        "cough_duration_bn",
        "duration",
        "আপনার কতদিন ধরে কাশি আছে?",
        QuestionLanguage.BENGALI,
        answer_type="duration",
        priority=20,
    ),
    Question(
        "cough_duration_mr",
        "duration",
        "तुम्हाला किती दिवसांपासून खोकला आहे?",
        QuestionLanguage.MARATHI,
        answer_type="duration",
        priority=20,
    ),

    # ===================================================================
    # SEVERITY
    # ===================================================================
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
        "खाँसी कितनी ज़्यादा है?",
        QuestionLanguage.HINDI,
        answer_type="scale",
        priority=30,
    ),
    Question(
        "cough_severity_bn",
        "severity",
        "কাশি কতটা বেশি?",
        QuestionLanguage.BENGALI,
        answer_type="scale",
        priority=30,
    ),
    Question(
        "cough_severity_mr",
        "severity",
        "खोकला किती जास्त आहे?",
        QuestionLanguage.MARATHI,
        answer_type="scale",
        priority=30,
    ),

    # ===================================================================
    # NATURE
    # ===================================================================
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
        "आपकी खाँसी सूखी है या बलगम के साथ है?",
        QuestionLanguage.HINDI,
        answer_type="single_choice",
        options=("सूखी", "बलगम के साथ"),
        priority=40,
    ),
    Question(
        "cough_type_bn",
        "nature",
        "আপনার কাশি কি শুকনো, নাকি কফ বের হয়?",
        QuestionLanguage.BENGALI,
        answer_type="single_choice",
        options=("শুকনো", "কফসহ"),
        priority=40,
    ),
    Question(
        "cough_type_mr",
        "nature",
        "तुमचा खोकला कोरडा आहे की कफासह आहे?",
        QuestionLanguage.MARATHI,
        answer_type="single_choice",
        options=("कोरडा", "कफासह"),
        priority=40,
    ),

    # ===================================================================
    # SPUTUM
    # ===================================================================
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
        "क्या खाँसी के साथ बलगम निकलता है?",
        QuestionLanguage.HINDI,
        answer_type="boolean",
        priority=50,
    ),
    Question(
        "cough_sputum_bn",
        "sputum",
        "কাশির সঙ্গে কি কফ বের হয়?",
        QuestionLanguage.BENGALI,
        answer_type="boolean",
        priority=50,
    ),
    Question(
        "cough_sputum_mr",
        "sputum",
        "खोकल्यासोबत कफ निघतो का?",
        QuestionLanguage.MARATHI,
        answer_type="boolean",
        priority=50,
    ),

    # ===================================================================
    # SPUTUM CHARACTERISTICS
    # ===================================================================
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
        "बलगम का रंग या रूप कैसा है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=60,
    ),
    Question(
        "cough_sputum_characteristics_bn",
        "sputum_characteristics",
        "কফের রং বা দেখতে কেমন?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=60,
    ),
    Question(
        "cough_sputum_characteristics_mr",
        "sputum_characteristics",
        "कफाचा रंग किंवा स्वरूप कसे आहे?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=60,
    ),

    # ===================================================================
    # BLOOD PRESENCE
    # ===================================================================
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
        "क्या खाँसी के साथ खून आया है?",
        QuestionLanguage.HINDI,
        answer_type="boolean",
        priority=70,
    ),
    Question(
        "cough_blood_bn",
        "blood_presence",
        "কাশির সঙ্গে কি রক্ত এসেছে?",
        QuestionLanguage.BENGALI,
        answer_type="boolean",
        priority=70,
    ),
    Question(
        "cough_blood_mr",
        "blood_presence",
        "खोकताना रक्त आले आहे का?",
        QuestionLanguage.MARATHI,
        answer_type="boolean",
        priority=70,
    ),

    # ===================================================================
    # ASSOCIATED SYMPTOMS
    # ===================================================================
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
        "खाँसी के साथ और कोई लक्षण हैं?",
        QuestionLanguage.HINDI,
        answer_type="multiple_choice",
        priority=80,
    ),
    Question(
        "cough_associated_bn",
        "associated_symptoms",
        "কাশির সঙ্গে কি অন্য কোনো উপসর্গ আছে?",
        QuestionLanguage.BENGALI,
        answer_type="multiple_choice",
        priority=80,
    ),
    Question(
        "cough_associated_mr",
        "associated_symptoms",
        "खोकल्यासोबत आणखी काही लक्षणे आहेत का?",
        QuestionLanguage.MARATHI,
        answer_type="multiple_choice",
        priority=80,
    ),

    # ===================================================================
    # AGGRAVATING FACTORS
    # ===================================================================
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
        "किस चीज़ से आपकी खाँसी बढ़ जाती है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=90,
    ),
    Question(
        "cough_aggravating_bn",
        "aggravating_factors",
        "কী কারণে আপনার কাশি বেড়ে যায়?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=90,
    ),
    Question(
        "cough_aggravating_mr",
        "aggravating_factors",
        "कशामुळे तुमचा खोकला वाढतो?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=90,
    ),
),

        # ===================================================================
        # HEADACHE
        # ===================================================================
        "headache": (
    # ===================================================================
    # ONSET
    # ===================================================================
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
        "सिरदर्द कब शुरू हुआ?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "headache_onset_bn",
        "onset",
        "মাথাব্যথা কখন শুরু হয়েছে?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "headache_onset_mr",
        "onset",
        "डोकेदुखी कधी सुरू झाली?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=10,
    ),

    # ===================================================================
    # DURATION
    # ===================================================================
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
        "सिरदर्द आम तौर पर कितनी देर रहता है?",
        QuestionLanguage.HINDI,
        answer_type="duration",
        priority=20,
    ),
    Question(
        "headache_duration_bn",
        "duration",
        "মাথাব্যথা সাধারণত কতক্ষণ থাকে?",
        QuestionLanguage.BENGALI,
        answer_type="duration",
        priority=20,
    ),
    Question(
        "headache_duration_mr",
        "duration",
        "डोकेदुखी साधारणपणे किती वेळ टिकते?",
        QuestionLanguage.MARATHI,
        answer_type="duration",
        priority=20,
    ),

    # ===================================================================
    # LOCATION
    # ===================================================================
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
        "सिर में दर्द ठीक कहाँ होता है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=30,
    ),
    Question(
        "headache_location_bn",
        "location",
        "মাথার ঠিক কোথায় ব্যথা হয়?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=30,
    ),
    Question(
        "headache_location_mr",
        "location",
        "डोक्यात नेमक्या कुठे दुखते?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=30,
    ),

    # ===================================================================
    # CHARACTER
    # ===================================================================
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
        "सिर का दर्द कैसा महसूस होता है?",
        QuestionLanguage.HINDI,
        answer_type="single_choice",
        options=(
            "धड़कने वाला",
            "दबाव जैसा",
            "तेज़",
            "हल्का लगातार दर्द",
            "कुछ और",
        ),
        priority=40,
    ),
    Question(
        "headache_character_bn",
        "character",
        "মাথাব্যথা কেমন অনুভূত হয়?",
        QuestionLanguage.BENGALI,
        answer_type="single_choice",
        options=(
            "ধকধকে",
            "চাপের মতো",
            "তীব্র",
            "মৃদু একটানা ব্যথা",
            "অন্য কিছু",
        ),
        priority=40,
    ),
    Question(
        "headache_character_mr",
        "character",
        "डोकेदुखी कशी जाणवते?",
        QuestionLanguage.MARATHI,
        answer_type="single_choice",
        options=(
            "ठणकणारी",
            "दाबल्यासारखी",
            "तीक्ष्ण",
            "मंद सतत वेदना",
            "इतर",
        ),
        priority=40,
    ),

    # ===================================================================
    # SEVERITY
    # ===================================================================
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
        "0 से 10 के स्केल पर सिरदर्द कितना है?",
        QuestionLanguage.HINDI,
        answer_type="scale",
        priority=50,
    ),
    Question(
        "headache_severity_bn",
        "severity",
        "০ থেকে ১০-এর স্কেলে মাথাব্যথা কতটা তীব্র?",
        QuestionLanguage.BENGALI,
        answer_type="scale",
        priority=50,
    ),
    Question(
        "headache_severity_mr",
        "severity",
        "० ते १० या मोजपट्टीवर डोकेदुखी किती तीव्र आहे?",
        QuestionLanguage.MARATHI,
        answer_type="scale",
        priority=50,
    ),

    # ===================================================================
    # FREQUENCY / PATTERN
    # ===================================================================
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
        "आपको ये सिरदर्द कितनी बार होता है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=60,
    ),
    Question(
        "headache_frequency_bn",
        "frequency_pattern",
        "আপনার এই মাথাব্যথা কত ঘন ঘন হয়?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=60,
    ),
    Question(
        "headache_frequency_mr",
        "frequency_pattern",
        "तुम्हाला ही डोकेदुखी किती वेळा होते?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=60,
    ),

    # ===================================================================
    # AGGRAVATING FACTORS
    # ===================================================================
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
        "किस चीज़ से सिरदर्द बढ़ता है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=70,
    ),
    Question(
        "headache_aggravating_bn",
        "aggravating_factors",
        "কী কারণে মাথাব্যথা বেড়ে যায়?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=70,
    ),
    Question(
        "headache_aggravating_mr",
        "aggravating_factors",
        "कशामुळे डोकेदुखी वाढते?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=70,
    ),

    # ===================================================================
    # RELIEVING FACTORS
    # ===================================================================
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
        "किस चीज़ से सिरदर्द कम होता है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=80,
    ),
    Question(
        "headache_relieving_bn",
        "relieving_factors",
        "কী করলে মাথাব্যথা কমে যায়?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=80,
    ),
    Question(
        "headache_relieving_mr",
        "relieving_factors",
        "कशामुळे डोकेदुखी कमी होते?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=80,
    ),

    # ===================================================================
    # ASSOCIATED SYMPTOMS
    # ===================================================================
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
        "सिरदर्द के साथ और कोई लक्षण हैं?",
        QuestionLanguage.HINDI,
        answer_type="multiple_choice",
        priority=90,
    ),
    Question(
        "headache_associated_bn",
        "associated_symptoms",
        "মাথাব্যথার সঙ্গে কি অন্য কোনো উপসর্গ আছে?",
        QuestionLanguage.BENGALI,
        answer_type="multiple_choice",
        priority=90,
    ),
    Question(
        "headache_associated_mr",
        "associated_symptoms",
        "डोकेदुखीसोबत आणखी काही लक्षणे आहेत का?",
        QuestionLanguage.MARATHI,
        answer_type="multiple_choice",
        priority=90,
    ),
),

        # ===================================================================
        # ABDOMINAL PAIN
        # ===================================================================
       "abdominal_pain": (
    # ===================================================================
    # ONSET
    # ===================================================================
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
        "पेट में दर्द कब शुरू हुआ?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "abdominal_pain_onset_bn",
        "onset",
        "পেটে ব্যথা কখন শুরু হয়েছে?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=10,
    ),
    Question(
        "abdominal_pain_onset_mr",
        "onset",
        "पोटदुखी कधी सुरू झाली?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=10,
    ),

    # ===================================================================
    # LOCATION
    # ===================================================================
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
        "पेट में दर्द ठीक कहाँ हो रहा है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=20,
    ),
    Question(
        "abdominal_pain_location_bn",
        "location",
        "পেটের ঠিক কোথায় ব্যথা হচ্ছে?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=20,
    ),
    Question(
        "abdominal_pain_location_mr",
        "location",
        "पोटात नेमक्या कुठे दुखत आहे?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=20,
    ),

    # ===================================================================
    # CHARACTER
    # ===================================================================
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
        "पेट का दर्द कैसा महसूस होता है?",
        QuestionLanguage.HINDI,
        answer_type="single_choice",
        options=(
            "ऐंठन",
            "जलन",
            "तेज़",
            "हल्का लगातार दर्द",
            "कुछ और",
        ),
        priority=30,
    ),
    Question(
        "abdominal_pain_character_bn",
        "character",
        "পেটের ব্যথা কেমন অনুভূত হয়?",
        QuestionLanguage.BENGALI,
        answer_type="single_choice",
        options=(
            "মোচড় বা খিঁচুনি",
            "জ্বালাপোড়া",
            "তীব্র ব্যথা",
            "মৃদু একটানা ব্যথা",
            "অন্য কিছু",
        ),
        priority=30,
    ),
    Question(
        "abdominal_pain_character_mr",
        "character",
        "पोटातील दुखणे कसे जाणवते?",
        QuestionLanguage.MARATHI,
        answer_type="single_choice",
        options=(
            "कळ येणे",
            "जळजळ",
            "तीक्ष्ण वेदना",
            "मंद सतत वेदना",
            "इतर",
        ),
        priority=30,
    ),

    # ===================================================================
    # DURATION
    # ===================================================================
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
        "पेट में दर्द कब से है?",
        QuestionLanguage.HINDI,
        answer_type="duration",
        priority=40,
    ),
    Question(
        "abdominal_pain_duration_bn",
        "duration",
        "কতদিন ধরে পেটে ব্যথা হচ্ছে?",
        QuestionLanguage.BENGALI,
        answer_type="duration",
        priority=40,
    ),
    Question(
        "abdominal_pain_duration_mr",
        "duration",
        "पोटात किती दिवसांपासून दुखत आहे?",
        QuestionLanguage.MARATHI,
        answer_type="duration",
        priority=40,
    ),

    # ===================================================================
    # SEVERITY
    # ===================================================================
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
        "0 से 10 के स्केल पर पेट का दर्द कितना है?",
        QuestionLanguage.HINDI,
        answer_type="scale",
        priority=50,
    ),
    Question(
        "abdominal_pain_severity_bn",
        "severity",
        "০ থেকে ১০-এর স্কেলে পেটের ব্যথা কতটা তীব্র?",
        QuestionLanguage.BENGALI,
        answer_type="scale",
        priority=50,
    ),
    Question(
        "abdominal_pain_severity_mr",
        "severity",
        "० ते १० या मोजपट्टीवर पोटातील दुखणे किती तीव्र आहे?",
        QuestionLanguage.MARATHI,
        answer_type="scale",
        priority=50,
    ),

    # ===================================================================
    # RADIATION
    # ===================================================================
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
        "क्या पेट का दर्द शरीर के किसी और हिस्से तक जाता है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=60,
    ),
    Question(
        "abdominal_pain_radiation_bn",
        "radiation",
        "পেটের ব্যথা কি শরীরের অন্য কোনো অংশে ছড়িয়ে পড়ে?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=60,
    ),
    Question(
        "abdominal_pain_radiation_mr",
        "radiation",
        "पोटातील दुखणे शरीराच्या इतर कोणत्याही भागात पसरते का?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=60,
    ),

    # ===================================================================
    # AGGRAVATING FACTORS
    # ===================================================================
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
        "किस चीज़ से पेट का दर्द बढ़ता है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=70,
    ),
    Question(
        "abdominal_pain_aggravating_bn",
        "aggravating_factors",
        "কী কারণে পেটের ব্যথা বেড়ে যায়?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=70,
    ),
    Question(
        "abdominal_pain_aggravating_mr",
        "aggravating_factors",
        "कशामुळे पोटातील दुखणे वाढते?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=70,
    ),

    # ===================================================================
    # RELIEVING FACTORS
    # ===================================================================
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
        "किस चीज़ से पेट का दर्द कम होता है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=80,
    ),
    Question(
        "abdominal_pain_relieving_bn",
        "relieving_factors",
        "কী করলে পেটের ব্যথা কমে যায়?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=80,
    ),
    Question(
        "abdominal_pain_relieving_mr",
        "relieving_factors",
        "कशामुळे पोटातील दुखणे कमी होते?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=80,
    ),

    # ===================================================================
    # ASSOCIATED SYMPTOMS
    # ===================================================================
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
        "पेट के दर्द के साथ और कोई लक्षण हैं?",
        QuestionLanguage.HINDI,
        answer_type="multiple_choice",
        priority=90,
    ),
    Question(
        "abdominal_pain_associated_bn",
        "associated_symptoms",
        "পেটের ব্যথার সঙ্গে কি অন্য কোনো উপসর্গ আছে?",
        QuestionLanguage.BENGALI,
        answer_type="multiple_choice",
        priority=90,
    ),
    Question(
        "abdominal_pain_associated_mr",
        "associated_symptoms",
        "पोटदुखीसोबत आणखी काही लक्षणे आहेत का?",
        QuestionLanguage.MARATHI,
        answer_type="multiple_choice",
        priority=90,
    ),

    # ===================================================================
    # BOWEL RELATED SYMPTOMS
    # ===================================================================
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
        "क्या आपके मल त्याग में कोई बदलाव हुआ है?",
        QuestionLanguage.HINDI,
        answer_type="text",
        priority=100,
    ),
    Question(
        "abdominal_bowel_bn",
        "bowel_related_symptoms",
        "আপনার মলত্যাগে কি কোনো পরিবর্তন হয়েছে?",
        QuestionLanguage.BENGALI,
        answer_type="text",
        priority=100,
    ),
    Question(
        "abdominal_bowel_mr",
        "bowel_related_symptoms",
        "तुमच्या मलविसर्जनात काही बदल झाला आहे का?",
        QuestionLanguage.MARATHI,
        answer_type="text",
        priority=100,
    ),

    # ===================================================================
    # NAUSEA / VOMITING
    # ===================================================================
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
        "क्या आपको जी मिचलाने या उल्टी की शिकायत है?",
        QuestionLanguage.HINDI,
        answer_type="boolean",
        priority=110,
    ),
    Question(
        "abdominal_nausea_bn",
        "vomiting_nausea",
        "আপনার কি বমি বমি ভাব বা বমি হয়েছে?",
        QuestionLanguage.BENGALI,
        answer_type="boolean",
        priority=110,
    ),
    Question(
        "abdominal_nausea_mr",
        "vomiting_nausea",
        "तुम्हाला मळमळ किंवा उलटी झाली आहे का?",
        QuestionLanguage.MARATHI,
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

    "bengali": QuestionLanguage.BENGALI,
    "bangla": QuestionLanguage.BENGALI,
    "bn": QuestionLanguage.BENGALI,

    "marathi": QuestionLanguage.MARATHI,
    "mr": QuestionLanguage.MARATHI,
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