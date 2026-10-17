import os
import shutil
from typing import Dict, Any
from pathlib import Path
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

# Audio processing library imports with robust fallbacks
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from backend.config import settings

router = APIRouter()
app = FastAPI(title="Audio Parser Service")

USER_FILES_DIR = Path("~/AbrarCloud/userfiles")
USER_FILES_DIR.mkdir(parents=True, exist_ok=True)

class WorkspaceAudioRequest(BaseModel):
    filename: str

def extract_audio_metadata(filepath: Path) -> Dict[str, Any]:
    """Read audio properties using soundfile, librosa, or basic file size fallback."""
    metadata = {
        "filename": filepath.name,
        "size_bytes": filepath.stat().st_size,
        "duration_seconds": 0.0,
        "sample_rate": 0,
        "channels": 0
    }
    
    if SOUNDFILE_AVAILABLE:
        try:
            info = sf.info(str(filepath))
            metadata["duration_seconds"] = float(info.duration)
            metadata["sample_rate"] = int(info.samplerate)
            metadata["channels"] = int(info.channels)
            return metadata
        except Exception:
            pass
            
    if LIBROSA_AVAILABLE:
        try:
            y, sr = librosa.load(str(filepath), sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            metadata["duration_seconds"] = float(duration)
            metadata["sample_rate"] = int(sr)
            metadata["channels"] = 1  # Librosa mono by default unless specified
            return metadata
        except Exception:
            pass
            
    # Mock / Fallback if no libraries can read it
    metadata["duration_seconds"] = round(filepath.stat().st_size / 32000.0, 2)  # Rough estimate (16kHz 16-bit mono wav is 32KB/sec)
    metadata["sample_rate"] = 16000
    metadata["channels"] = 1
    return metadata

def transcribe_audio(filepath: Path) -> str:
    """Send audio to OpenAI Whisper API, or return fallback transcription."""
    if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            with open(filepath, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcription.text
        except Exception as e:
            return f"[Transcription API Error: {str(e)}]. Fallback description: Audio content processed."
            
    # Mock transcription text fallback
    metadata = extract_audio_metadata(filepath)
    return f"Mock Transcription: Standard spoken English content parsed from {filepath.name}. " \
           f"Length: {metadata['duration_seconds']} seconds. (Whisper API key not configured)."

def process_audio(filepath: Path) -> Dict[str, Any]:
    """Parse audio metadata and transcribe speech."""
    metadata = extract_audio_metadata(filepath)
    transcription = transcribe_audio(filepath)
    return {
        "filename": filepath.name,
        "metadata": metadata,
        "transcription": transcription
    }

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "audio-parser"}

@router.post("/parse/workspace")
def parse_workspace_audio(payload: WorkspaceAudioRequest):
    """Parse audio and transcribe from the user's workspace directory."""
    filepath = USER_FILES_DIR / payload.filename
    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file '{payload.filename}' not found in user workspace."
        )
    return process_audio(filepath)

@router.post("/parse/upload")
async def parse_uploaded_audio(file: UploadFile = File(...)):
    """Upload an audio file and parse its metadata and transcription."""
    temp_path = USER_FILES_DIR / f"temp_{file.filename}"
    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = process_audio(temp_path)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio parsing error: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path.exists():
            os.remove(temp_path)

app.include_router(router)
