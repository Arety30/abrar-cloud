# Plan: Audio Parser Module

This document outlines the blueprint and step-by-step logic for the `/backend/audio-parser/` module.

---

## 1. Goal & Requirements
- **Purpose**: Parse audio files (WAV, MP3, OGG, M4A) to extract technical metadata (duration, sample rate, channels) and transcribe speech to text.
- **Library Requirements**: 
  - Audio Metadata: Use **soundfile** and/or **librosa** to read audio file details (sample rate, duration).
  - Transcription: Use **OpenAI Whisper** (via standard `openai` library / LangChain tools) to transcribe speech.
  - Fallback logic: If no OpenAI API Key is provided, extract metadata and return a mock text transcription (speech simulation) to ensure the service remains fully testable.

---

## 2. API Endpoints (FastAPI)
The module will run as an isolated FastAPI app in `/backend/audio-parser/main.py` exposing:
1. `POST /parse/upload`: Accept a multipart audio file upload, save temporarily, extract metadata (duration, channels, sample rate), call transcription service, and return results.
2. `POST /parse/workspace`: Locate a file in `~/AbrarCloud/userfiles/`, process it, and return metadata/transcription.
3. `GET /health`: Healthcheck.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize FastAPI App
Create `main.py` with FastAPI and path routes.

### Step 2: Implement Audio Metadata Extraction
Use `soundfile` or `librosa` to load the audio header and compute:
- Sample Rate (Hz)
- Number of Channels
- Duration in Seconds

### Step 3: Implement Transcription Service
Connect to the OpenAI Whisper API. If API keys are missing, return a deterministic simulation transcription referencing the file duration.

### Step 4: Implement Endpoints
Expose `/parse/upload` and `/parse/workspace`.

### Step 5: Write `test.py`
Create a test file `test.py` that generates a mock sine-wave WAV file in-memory using `numpy` and `soundfile` (or mock bytes if libraries are unavailable), uploads it to `/parse/upload` using TestClient, and verifies metadata (duration/samplerate).
