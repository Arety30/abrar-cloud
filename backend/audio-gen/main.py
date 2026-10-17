import os
import wave
import math
import struct
import requests
from pathlib import Path
from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from backend.config import settings

router = APIRouter()
app = FastAPI(title="Audio Generator Service")

USER_FILES_DIR = Path("~/AbrarCloud/userfiles")
USER_FILES_DIR.mkdir(parents=True, exist_ok=True)

class GenerateAudioRequest(BaseModel):
    text: str
    voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
    filename: str = "generated_speech.wav"

def generate_local_synthetic_speech(text: str, filepath: Path):
    """
    Generate a local synthetic WAV file. Synthesizes a pitch-modulated 
    sound wave where frequencies are mapped to the character values of the text.
    Uses 0MB external RAM and standard library modules.
    """
    sample_rate = 8000
    num_channels = 1
    sampwidth = 2  # 16-bit
    
    # Calculate duration based on text length (approx 10 chars per second, bound 1-8s)
    duration = max(1.0, min(8.0, len(text) * 0.08))
    num_samples = int(sample_rate * duration)
    
    with wave.open(str(filepath), 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            # Calculate index in text to fetch active character
            char_idx = int((i / num_samples) * len(text))
            char_idx = min(char_idx, len(text) - 1) if text else 0
            char_val = ord(text[char_idx]) if text else 100
            
            # Map character value to frequency (between 150Hz and 550Hz)
            frequency = 150 + (char_val % 400)
            
            # Smooth frequency transitioning / simple vibrato
            t = i / sample_rate
            value = int(16384 * math.sin(2 * math.pi * frequency * t))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

def generate_openai_tts(text: str, voice: str, filepath: Path) -> bool:
    """Generate speech via OpenAI TTS API."""
    if not (OPENAI_AVAILABLE and settings.OPENAI_API_KEY):
        return False
        
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        # Write response content (MP3/WAV) to file
        response.write_to_file(filepath)
        return True
    except Exception:
        return False

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "audio-gen"}

@router.post("/generate")
def generate_audio(payload: GenerateAudioRequest):
    """Generate audio speech from text. Saves audio file to user workspace."""
    filepath = USER_FILES_DIR / payload.filename
    
    # Attempt OpenAI TTS, fallback to local synthetic speech
    success = generate_openai_tts(payload.text, payload.voice, filepath)
    
    generator_source = "OpenAI TTS API"
    if not success:
        generate_local_synthetic_speech(payload.text, filepath)
        generator_source = "Local Pitch-Modulated Synthesizer"
        
    return {
        "status": "success",
        "text": payload.text,
        "filename": payload.filename,
        "filepath": str(filepath),
        "generator": generator_source
    }

app.include_router(router)
