# Plan: Audio Generator Module (audio-gen)

This document outlines the blueprint and step-by-step logic for the `/backend/audio-gen/` module.

---

## 1. Goal & Requirements
- **Purpose**: Expose an endpoint that takes a text string and generates a corresponding speech audio file (WAV/MP3) saved to the workspace.
- **Library Requirements**: 
  - API Mode: Connect to OpenAI TTS API (`tts-1`) if settings are configured.
  - Local Fallback: Generate a synthetic WAV file in pure Python (representing pitch/frequency shifts mapped to the input text characters). This runs extremely fast with zero neural network overhead, saving RAM and running smoothly on any local device.

---

## 2. API Endpoints (FastAPI)
The module will run as an isolated FastAPI app in `/backend/audio-gen/main.py` exposing:
1. `POST /generate`: Accept a JSON text prompt, voice selection, and output filename. Write WAV/MP3 to `~/AbrarCloud/userfiles/` and return metadata.
2. `GET /health`: Healthcheck.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize FastAPI App
Create `main.py` with FastAPI and settings.

### Step 2: Implement Audio Generation Pipeline
- **API Mode**: Check if `OPENAI_API_KEY` is present. If yes, query OpenAI's `tts-1` endpoint with voice choice, stream back response bytes, and write to the output file.
- **Local Fallback Mode**: Build a simple PCM WAV generator. It translates the string's length or characters into a sequence of tones (pitch modulation) and outputs a valid WAV file in the workspace.

### Step 3: Implement Endpoints
Expose `/generate`.

### Step 4: Write `test.py`
Create a test file `test.py` that sends a text prompt to `/generate`, verifies a WAV file is saved in the workspace, and inspects its format and byte size.
