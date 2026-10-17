# Plan: Database Editor Module

This document outlines the blueprint and step-by-step logic for the `/backend/database-editor/` module.

---

## 1. Goal & Requirements
- **Purpose**: Provide a database explorer and editor allowing the client to list tables, query records, run SQL scripts, and insert/delete rows in our local SQLite database.
- **Library Requirements**: 
  - Use Python's built-in `sqlite3` for query execution and metadata extraction.
  - Integrate with the database connection defined in `/backend/database.py`.

---

## 2. API Endpoints (FastAPI)
The module will run as an isolated FastAPI app in `/backend/database-editor/main.py` exposing:
1. `GET /tables`: Fetch a list of all table names inside the SQLite database.
2. `POST /query`: Accept a JSON payload containing raw SQL (e.g. `SELECT * FROM users`) and return the column headers and rows.
3. `POST /insert`: Helper to insert a row into a table given table name and key-value column pairs.
4. `DELETE /delete`: Helper to delete a row based on table name, key column, and key value.
5. `GET /health`: Healthcheck.

---

## 3. Step-by-Step Implementation Logic

### Step 1: Initialize FastAPI App
Create `main.py` with FastAPI and import `get_db_connection` from `backend.database`.

### Step 2: Implement Table Listing
Query SQLite catalog:
`SELECT name FROM sqlite_master WHERE type='table';`

### Step 3: Implement Query Runner
Execute raw SQL query using a database cursor. If it is a SELECT query, fetch results and map rows to list of dicts. If it is a write query (INSERT/UPDATE/DELETE), commit the transaction and return affected row count.

### Step 4: Implement Insert/Delete Helpers
Construct SQL strings dynamically based on the input payload dictionary, execute, and commit.

### Step 5: Write `test.py`
Create a test file `test.py` that connects via TestClient, creates a temporary table, inserts a record, runs a SELECT query, verifies the values, deletes the table, and verifies cleanup.
