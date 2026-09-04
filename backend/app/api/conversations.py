from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai.conversation.ayush_mode import AyushMode
from ai.conversation.dialogue_manager import DialogueManager
from ai.conversation.question_bank import QuestionLanguage


router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"],
)


# ---------------------------------------------------------------------------
# In-memory conversation store
# ---------------------------------------------------------------------------

_managers: dict[int, DialogueManager] = {}


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class ConversationStartRequest(BaseModel):
    session_id: int
    complaint: str
    language: str = "en"
    mode: str = "allopathy"


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
    "fever": (
        "fever",
        "temperature",
        "high temperature",
        "bukhar",
        "बुखार",
        "জ্বর",
        "বুকার",
        "ताप",
        "अंगात ताप",
    ),
    "chest_pain": (
        "chest pain",
        "pain in chest",
        "chest discomfort",
        "seene mein dard",
        "seene ka dard",
        "सीने में दर्द",
        "सीने का दर्द",
        "বুকে ব্যথা",
        "বুকে ব্যাথা",
        "বুকের ব্যথা",
        "छातीत दुखणे",
        "छातीत दुखत",
        "छाती दुखणे",
    ),
    "cough": (
        "cough",
        "khansi",
        "khaansi",
        "खांसी",
        "खाँसी",
        "কাশি",
        "खोकला",
    ),
    "headache": (
        "headache",
        "head ache",
        "sir dard",
        "sar dard",
        "सिर दर्द",
        "सर दर्द",
        "মাথাব্যথা",
        "মাথা ব্যথা",
        "डोकेदुखी",
        "डोके दुखणे",
    ),
    "abdominal_pain": (
        "abdominal pain",
        "stomach pain",
        "belly pain",
        "stomach ache",
        "pet pain",
        "pet dard",
        "पेट दर्द",
        "पेट में दर्द",
        "পেট ব্যথা",
        "পেটে ব্যথা",
        "পেটের ব্যথা",
        "पोटदुखी",
        "पोटात दुखणे",
        "पोटात दुखत",
    ),
}


def resolve_complaint(text: str) -> str | None:
    """
    Resolve a patient's chief complaint to a supported complaint category.

    This is deterministic and does not diagnose the patient.
    """

    normalized = text.strip().lower()

    if not normalized:
        return None

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


def serialize_question(
    question,
    language: str = "en",
):
    """
    Convert an internal question object into the API response format.

    Allopathy questions already contain their configured language.

    AYUSH questions contain translations and use text_for(language)
    so the patient's selected language is preserved.
    """

    if question is None:
        return None

    # Standard Allopathy question
    if hasattr(question, "question_id"):
        return {
            "id": question.question_id,
            "field_id": question.field_id,
            "question": question.text,
            "language": question.language.value,
            "answer_type": question.answer_type,
            "options": list(question.options),
            "priority": question.priority,
        }

    # AYUSH question
    return {
        "id": question.id,
        "field_id": question.field_id,
        "question": question.text_for(language),
        "language": language,
        "answer_type": "text",
        "options": [],
        "priority": None,
    }


def serialize_result(
    result,
    language: str = "en",
):
    """
    Serialize a conversation result while preserving the active language.
    """

    return {
        "next_question": serialize_question(
            result.next_question,
            language,
        ),
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
    # ---------------------------------------------------------------
    # Validate mode
    # ---------------------------------------------------------------

    if request.mode not in {"allopathy", "ayush"}:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported conversation mode. "
                "Use 'allopathy' or 'ayush'."
            ),
        )

    # ---------------------------------------------------------------
    # Resolve chief complaint
    # ---------------------------------------------------------------

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

    # ---------------------------------------------------------------
    # Validate language
    # ---------------------------------------------------------------

    try:
        language = QuestionLanguage(request.language)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported conversation language: "
                f"{request.language}"
            ),
        )

    # ---------------------------------------------------------------
    # Create AYUSH mode when requested
    # ---------------------------------------------------------------

    ayush_mode = (
        AyushMode()
        if request.mode == "ayush"
        else None
    )

    # ---------------------------------------------------------------
    # Create dialogue manager
    # ---------------------------------------------------------------

    manager = DialogueManager.create(
        complaint,
        language=language,
        ayush_mode=ayush_mode,
    )

    # Store active manager against the existing session
    _managers[request.session_id] = manager

    # ---------------------------------------------------------------
    # Start interview
    # ---------------------------------------------------------------

    question = manager.start()

    return {
        "session_id": request.session_id,
        "complaint": complaint,
        "mode": request.mode,
        "question": serialize_question(
            question,
            language.value,
        ),
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

    return serialize_result(
        result,
        manager.language.value,
    )


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
        "question": serialize_question(
            question,
            manager.language.value,
        ),
        "completed": question is None,
    }