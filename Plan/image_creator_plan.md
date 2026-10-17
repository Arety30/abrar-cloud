# Plan: Image Creator Module

This document outlines the blueprint and step-by-step logic for the `/backend/image-creator/` module.

---

## 1. Goal & Requirements
- **Purpose**: Expose an endpoint that takes a text description (prompt) and generates a new image saved to the user's workspace.
- **Library Requirements**: 
  - Standard integration: Connect to OpenAI's DALL-E API (via `openai`) if settings are configured.
  - Local fallback generator: Use **Pillow** (PIL) to programmatically render a beautiful, colored canvas containing the prompt text drawn onto it. This ensures it generates a real PNG/JPG file locally without external network API calls.

---

## 2. API Endpoints (FastAPI)
The module will run as an isolated FastAPI app in `/backend/image-creator/main.py` exposing:
1. `POST /generate`: Accept JSON prompt, size settings, and output filename. Run image generator, write result to `~/AbrarCloud/userfiles/`, and return metadata.
2. `GET /health`: Healthcheck.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize FastAPI App
Create `main.py` with FastAPI and load the settings.

### Step 2: Implement Image Generation Pipeline
- **API Mode**: Check if `OPENAI_API_KEY` is present. If yes, query `dall-e-3` or `dall-e-2`, fetch the image URL, download it, and write it to the workspace.
- **Local Fallback Mode**: Initialize a new PIL image with a background color derived from the prompt string (to keep it interactive and dynamic). Render the prompt text in the center using PIL `ImageDraw` and default font. Save to file.

### Step 3: Implement Endpoints
Expose `/generate` mapping the pipeline.

### Step 4: Write `test.py`
Create a test file `test.py` that sends a prompt to `/generate`, verifies a new image file is saved in the workspace, and inspects its format and dimensions.
