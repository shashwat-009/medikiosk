from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai.conversation.dialogue_manager import DialogueManager
from ai.conversation.question_bank import QuestionLanguage


router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"],
)


# ---------------------------------------------------------------------------
# In-memory conversation store
# ---------------------------------------------------------------------------
#
# This is intentionally an MVP implementation.
#
# The actual persistent responses continue to be stored through /responses.
# The DialogueManager contains temporary runtime state for the active
# interview.
#
# Later this can move to Redis/database/session storage.
# ---------------------------------------------------------------------------

_managers: dict[int, DialogueManager] = {}


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class ConversationStartRequest(BaseModel):
    session_id: int
    complaint: str
    language: str = "en"


class ConversationAnswerRequest(BaseModel):
    session_id: int
    field_id: str
    answer: Any
    question_id: str | None = None
    input_type: str = "touch"


# ---------------------------------------------------------------------------
# Complaint resolver
# ---------------------------------------------------------------------------


_COMPLAINT_KEYWORDS = {
    # ================================================================
    # FEVER
    # ================================================================
    "fever": (
        # English
        "fever",
        "temperature",
        "high temperature",

        # Hindi / Hinglish
        "bukhar",
        "बुखार",

        # Bengali
        "জ্বর",
        "বুকার",

        # Marathi
        "ताप",
        "अंगात ताप",
    ),

    # ================================================================
    # CHEST PAIN
    # ================================================================
    "chest_pain": (
        # English
        "chest pain",
        "pain in chest",
        "chest discomfort",

        # Hindi / Hinglish
        "seene mein dard",
        "seene ka dard",
        "सीने में दर्द",
        "सीने का दर्द",

        # Bengali
        "বুকে ব্যথা",
        "বুকে ব্যাথা",
        "বুকের ব্যথা",

        # Marathi
        "छातीत दुखणे",
        "छातीत दुखत",
        "छाती दुखणे",
    ),

    # ================================================================
    # COUGH
    # ================================================================
    "cough": (
        # English
        "cough",

        # Hindi / Hinglish
        "khansi",
        "khaansi",
        "खांसी",
        "खाँसी",

        # Bengali
        "কাশি",

        # Marathi
        "खोकला",
    ),

    # ================================================================
    # HEADACHE
    # ================================================================
    "headache": (
        # English
        "headache",
        "head ache",

        # Hindi / Hinglish
        "sir dard",
        "sar dard",
        "सिर दर्द",
        "सर दर्द",

        # Bengali
        "মাথাব্যথা",
        "মাথা ব্যথা",

        # Marathi
        "डोकेदुखी",
        "डोके दुखणे",
    ),

    # ================================================================
    # ABDOMINAL PAIN
    # ================================================================
    "abdominal_pain": (
        # English
        "abdominal pain",
        "stomach pain",
        "belly pain",
        "stomach ache",

        # Hindi / Hinglish
        "pet pain",
        "pet dard",
        "पेट दर्द",
        "पेट में दर्द",

        # Bengali
        "পেট ব্যথা",
        "পেটে ব্যথা",
        "পেটের ব্যথা",

        # Marathi
        "पोटदुखी",
        "पोटात दुखणे",
        "पोटात दुखत",
    ),
}


def resolve_complaint(text: str) -> str | None:
    """
    Resolve a patient's chief-complaint text to a supported ontology
    complaint.

    This is deliberately deterministic.

    It does NOT diagnose the patient.
    It only maps obvious complaint phrases to the five supported
    conversation categories.
    """

    normalized = text.strip().lower()

    if not normalized:
        return None

    # Exact supported complaint first.
    supported = {
        "fever",
        "chest_pain",
        "cough",
        "headache",
        "abdominal_pain",
    }

    if normalized in supported:
        return normalized

    for complaint, keywords in _COMPLAINT_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return complaint

    return None


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def serialize_question(question):
    if question is None:
        return None

    return {
        "id": question.question_id,
        "field_id": question.field_id,
        "question": question.text,
        "language": question.language.value,
        "answer_type": question.answer_type,
        "options": list(question.options),
        "priority": question.priority,
    }


def serialize_result(result):
    return {
        "next_question": serialize_question(result.next_question),
        "completed": result.completed,
        "red_flag": (
    {
        "detected": result.red_flag.detected,
        "category": result.red_flag.category,
        "matched_pattern": result.red_flag.matched_pattern,
        "flag_id": result.red_flag.flag_id,
        "priority": (
            result.red_flag.priority.value
            if result.red_flag.priority is not None
            else None
        ),
        "matched_fields": list(
            result.red_flag.matched_fields
        ),
        "matched_text": result.red_flag.matched_text,
        "explanation": result.red_flag.explanation,
    }
    if result.red_flag is not None
    else None
),
    }


# ---------------------------------------------------------------------------
# Start conversation
# ---------------------------------------------------------------------------


@router.post("/start")
def start_conversation(
    request: ConversationStartRequest,
):
    complaint = resolve_complaint(request.complaint)

    if complaint is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Chief complaint could not be mapped to a supported "
                "complaint. Supported complaints are: fever, chest pain, "
                "cough, headache, and abdominal pain."
            ),
        )

    try:
        language = QuestionLanguage(request.language)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported conversation language: {request.language}",
        )

    manager = DialogueManager.create(
        complaint,
        language=language,
    )

    _managers[request.session_id] = manager

    question = manager.start()

    return {
        "session_id": request.session_id,
        "complaint": complaint,
        "question": serialize_question(question),
        "completed": question is None,
    }


# ---------------------------------------------------------------------------
# Process answer
# ---------------------------------------------------------------------------


@router.post("/answer")
def answer_conversation(
    request: ConversationAnswerRequest,
):
    manager = _managers.get(request.session_id)

    if manager is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No active conversation found for this session. "
                "Start the conversation first."
            ),
        )

    if not request.answer:
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty.",
        )

    try:
        if request.input_type == "voice":
            result = manager.process_voice_answer(
                field_id=request.field_id,
                transcript=str(request.answer),
                question_id=request.question_id,
            )

        else:
            result = manager.process_text_answer(
                field_id=request.field_id,
                text=str(request.answer),
                question_id=request.question_id,
            )

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return serialize_result(result)


# ---------------------------------------------------------------------------
# Get current question
# ---------------------------------------------------------------------------


@router.get("/{session_id}/next")
def get_next_question(session_id: int):
    manager = _managers.get(session_id)

    if manager is None:
        raise HTTPException(
            status_code=404,
            detail="No active conversation found for this session.",
        )

    question = manager.get_next_question()

    return {
        "question": serialize_question(question),
        "completed": question is None,
    }