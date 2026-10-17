# Plan: Signup Module

This document outlines the blueprint and step-by-step logic for the `/backend/signup/` module.

---

## 1. Goal & Requirements
- **Purpose**: Allow new users to register an account on AbrarCloud.
- **Features**:
  - Accept user registration details matching the UI fields: Real Name, Username, Email, and Password.
  - Check for username and email uniqueness in the SQLite database.
  - Hash password using `passlib` before storage.
  - Return registered user details and generate a mock verification code for testing.

---

## 2. API Endpoints (FastAPI)
The module will run as an isolated FastAPI app in `/backend/signup/router.py` (which is loaded by `backend/main.py`) exposing:
1. `POST /`: Registration endpoint.
2. `GET /health`: Healthcheck.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize APIRouter
Create `/backend/signup/router.py` and define request schemas.

### Step 2: Implement Registration Logic
- Validate that the email/username is unique.
- Hash password using `get_password_hash` from `backend.utils.auth`.
- Save record inside `users` SQLite table.
- Insert a verification code (e.g. "123456") inside `verification_codes` for testing.

### Step 3: Implement `test.py`
Create a test file `test.py` under `backend/signup/` to verify registration, constraint violations (duplicate username/email), and verify user presence.
