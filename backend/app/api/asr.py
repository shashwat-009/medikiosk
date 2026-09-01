from pathlib import Path
from tempfile import NamedTemporaryFile
import os

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings

from ai.asr.audio import validate_audio_file
from ai.asr.sarvam_asr import SarvamASRProvider


router = APIRouter(
    prefix="/asr",
    tags=["ASR"],
)


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):
    if not settings.sarvam_api_key:
        raise HTTPException(
            status_code=500,
            detail="SARVAM_API_KEY is not configured",
        )

    os.environ["SARVAM_API_KEY"] = settings.sarvam_api_key

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio file is required",
        )

    suffix = Path(file.filename).suffix.lower()

    if not suffix:
        raise HTTPException(
            status_code=400,
            detail="Audio file must have an extension",
        )

    temporary_path = None

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temporary_file:

            temporary_path = Path(
                temporary_file.name
            )

            content = await file.read()

            temporary_file.write(content)

        validate_audio_file(temporary_path)

        provider = SarvamASRProvider()

        result = provider.transcribe(
            temporary_path
        )

        return result.model_dump()

    except FileNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="Audio file could not be processed",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:
        if (
            temporary_path
            and temporary_path.exists()
        ):
            temporary_path.unlink()