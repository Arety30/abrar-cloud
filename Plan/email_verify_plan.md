# Plan: Email Verification Module

This document outlines the blueprint and step-by-step logic for the `/backend/email-verify/` module.

---

## 1. Goal & Requirements
- **Purpose**: Verify a user's email address using a token/code.
- **Features**:
  - Accept request containing: Email and Verification Code.
  - Verify match in `verification_codes` table.
  - Set `email_verified = 1` in `users` table upon verification.
  - Delete verification code entries.

---

## 2. API Endpoints (FastAPI)
The module will run as an isolated FastAPI app in `/backend/email-verify/router.py` (which is loaded by `backend/main.py`) exposing:
1. `POST /`: Verification validation.
2. `GET /health`: Healthcheck.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize APIRouter
Create `/backend/email-verify/router.py` and define request schemas.

### Step 2: Implement Verify Logic
- Query user record.
- Verify if verification code matches.
- Update `users` table to set `email_verified = 1`.
- Clear the code from the `verification_codes` table.

### Step 3: Implement `test.py`
Create a test file `test.py` under `backend/email-verify/` to verify a user registration, run the verification flow, check database states, and clean up.
