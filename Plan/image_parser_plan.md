# Plan: Image Parser Module

This document outlines the blueprint and step-by-step logic for the `/backend/image-parser/` module.

---

## 1. Goal & Requirements
- **Purpose**: Parse image files (PNG, JPG, JPEG, GIF) to extract metadata (dimensions, format, mode, EXIF) and generate description/captioning.
- **Library Requirements**: 
  - Metadata: Use **Pillow** (PIL) to open images and read properties/metadata.
  - AI Description: Use **LangChain** vision models (e.g. ChatOpenAI with `gpt-4o-mini` or `gpt-4o`) to describe image contents.
  - Fallback logic: If no OpenAI API Key is provided, extract metadata and return a mock/rule-based visual analysis description so that endpoints remain fully functional.

---

## 2. API Endpoints (FastAPI)
The module will run as an isolated FastAPI app in `/backend/image-parser/main.py` exposing:
1. `POST /parse/upload`: Accept a multipart image upload, save temporarily, extract PIL metadata, call LangChain vision helper, and return results.
2. `POST /parse/workspace`: Locate a file in `~/AbrarCloud/userfiles/`, process it, and return metadata/description.
3. `GET /health`: Healthcheck endpoint.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize FastAPI App
Create `main.py` with FastAPI and route definitions.

### Step 2: Implement Metadata Extraction
Use Pillow to read:
- Width and Height
- Image Format (e.g. PNG, JPEG)
- Color Mode (e.g. RGB, RGBA, L)
- EXIF tags (if present)

### Step 3: Implement LangChain Vision integration
Write helper function to convert the image to base64, feed it to a ChatOpenAI model with a vision prompt, and receive the description.
If API keys are missing, return a deterministic rule-based placeholder description based on file properties.

### Step 4: Implement Endpoints
Expose `/parse/upload` and `/parse/workspace`.

### Step 5: Write `test.py`
Create a test file `test.py` that generates a mock 1x1 pixel image using Pillow, sends it to `/parse/upload` using TestClient, and verifies the extracted height/width/format metadata.
