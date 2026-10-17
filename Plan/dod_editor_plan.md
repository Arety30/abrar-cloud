# Plan: Document Editor Module (dod-editor)

This document outlines the blueprint and step-by-step logic for the `/backend/dod-editor/` module.

---

## 1. Goal & Requirements
- **Purpose**: Provide document editing features where an agent (inspired by OpenManus) receives text commands (e.g. "Fix the spelling in this file", "Add a paragraph summarizing cloud computing") and applies edits to workspace files.
- **Library Requirements**: 
  - Agentic Logic: Import the `OpenManusAgent` class from `/backend/utils/agent.py` to run reasoning and tool usage (file reading/writing) for editing tasks.
  - Fallback logic: If LangChain/OpenAI settings are missing, use the deterministic fallback implementation in the agent.

---

## 2. API Endpoints (FastAPI)
The module will run as an isolated FastAPI app in `/backend/dod-editor/main.py` exposing:
1. `POST /edit`: Receives a filename, edit instructions, and option to create if missing. Reads the file, runs the `OpenManusAgent` with the instruction context, saves the agent's modified file content back to the workspace, and returns the result.
2. `GET /health`: Healthcheck.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize FastAPI App
Create `main.py` with FastAPI and load the workspace directories.

### Step 2: Integrate OpenManus Agent
Import `OpenManusAgent` and initialize it with document editor system instructions:
> "You are the AbrarCloud Document Editor Agent. You edit files in the user workspace. Carefully parse the requested file, make the requested edits while maintaining formatting, and write the file back."

### Step 3: Implement Edpoints
- Map `/edit` endpoint: validate file existence, run agent, return edited content and step summary.

### Step 4: Write `test.py`
Create a test file `test.py` that writes a test file, sends an edit instruction (e.g., "Add the word 'AbrarCloud' to the end"), verifies the file content updates, and cleans up.
