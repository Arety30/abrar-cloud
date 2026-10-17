import sqlite3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from backend.database import get_db_connection
from backend.utils.auth import hash_password

router = APIRouter()

class SignupRequest(BaseModel):
    real_name: str
    username: str
    email: EmailStr
    password: str

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "signup"}

@router.post("")
def register_user(payload: SignupRequest):
    """
    Register a new user in the SQLite database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (payload.username, payload.email))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or Email already registered."
            )
            
        # Hash password and insert
        hashed = hash_password(payload.password)
        cursor.execute(
            "INSERT INTO users (real_name, username, email, password_hash) VALUES (?, ?, ?, ?)",
            (payload.real_name, payload.username, payload.email, hashed)
        )
        
        # Pre-populate a mock verification code (e.g. "123456") for the verification flow
        cursor.execute(
            "INSERT OR REPLACE INTO verification_codes (email, code, expires_at) VALUES (?, ?, ?)",
            (payload.email, "123456", int(cursor.lastrowid or 0)) # store dummy metadata
        )
        
        conn.commit()
        return {
            "status": "success",
            "message": "User registered successfully. Verification code '123456' generated.",
            "user": {
                "username": payload.username,
                "email": payload.email,
                "real_name": payload.real_name
            }
        }
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email integrity violation."
        )
    finally:
        conn.close()
