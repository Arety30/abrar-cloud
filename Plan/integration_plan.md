# Plan: Integration Module

This document outlines the blueprint and step-by-step logic for the root `/backend/router.py` module to bridge the backend services to the `templates/` folder structure.

---

## 1. Goal & Requirements
- **Purpose**: Bridge the backend APIs to the user-facing HTML templates. It will serve the static/dynamic templates (e.g. login, signup, reset-password, and other file editors) and route frontend requests to the appropriate backend service modules.
- **Features**:
  - Expose HTML serving endpoints that fetch and return the template files (e.g. `/templates/login`, `/templates/signup`, `/templates/reset-password`).
  - Bridge API request routing to ensure the main server can render these templates directly.

---

## 2. API Endpoints (FastAPI)
Expose routes in `/backend/router.py`:
1. `GET /templates/{template_name}`: Serve the corresponding `index.html` template file (like `~/AbrarCloud/templates/login/index.html`) using FastAPI's `HTMLResponse`.
2. `GET /templates`: List all available templates in `~/AbrarCloud/templates/`.
3. `GET /health`: Healthcheck.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize FastAPI APIRouter
Create `/backend/router.py` using `APIRouter()`.

### Step 2: Implement Template Reader Helper
Write a function that reads the `index.html` file from `~/AbrarCloud/templates/[template_name]/index.html` and returns it. If the file or folder is missing, return a clean HTML error page or fallback response.

### Step 3: Implement Endpoints
Map the template reader to `/templates/{template_name}` and list all template folders under `/templates`.

### Step 4: Register Router in `backend/main.py`
Modify `backend/main.py` to import and register the root `/backend/router.py` so the root API can serve both the modules and the frontend templates.

### Step 5: Write `test.py`
Create a test file `test.py` inside `backend/` to verify template serving and listing.
