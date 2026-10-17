# Plan: File Parser Module

This document outlines the blueprint and step-by-step logic for the `/backend/file-parser/` module in the AbrarCloud project.

---

## 1. Goal & Requirements
- **Purpose**: Parse raw files (Text, PDF, DOCX) uploaded by the user or existing in the workspace and extract their text content and metadata.
- **Library Requirements**: Use **LangChain** document loaders for file parsing.
  - PDF: `langchain_community.document_loaders.PyPDFLoader` (or custom wrapper around `pypdf` if langchain-community imports are missing).
  - DOCX: `langchain_community.document_loaders.Docx2txtLoader` (or custom wrapper around `docx` / `Docx2txt`).
  - Text: `langchain_community.document_loaders.TextLoader` (or standard UTF-8 parsing).

---

## 2. API Endpoints (FastAPI)
The module will run as an isolated FastAPI app in `/backend/file-parser/main.py` exposing:
1. `POST /parse/upload`: Accept a multipart file upload, save it temporarily or directly process it, and return the parsed text and metadata.
2. `POST /parse/workspace`: Accept a filename located in the user's workspace `~/AbrarCloud/userfiles/` and parse it.
3. `GET /health`: Healthcheck endpoint for testing integration.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize FastAPI App
Create `main.py` with FastAPI and load the configuration settings.

### Step 2: Implement File Parsers (LangChain integration)
Write helper functions using LangChain document loaders to extract data based on file extension:
- `.txt`, `.md`, `.json`: Load via `TextLoader`.
- `.pdf`: Save uploaded file, parse using `PyPDFLoader`, and collect text page-by-page.
- `.docx`: Save uploaded file, parse using `Docx2txtLoader` or standard `python-docx` if imports are restricted.

### Step 3: Implement Endpoints
Map the parsing helpers to `/parse/upload` and `/parse/workspace`.

### Step 4: Write `test.py`
Create a standalone Python test file `test.py` that spins up the FastAPI app using a TestClient, sends mock `.txt`, `.pdf`, and `.docx` files, and validates the text output.
