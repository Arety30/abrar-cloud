import sqlite3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from backend.database import get_db_connection

router = APIRouter()

class VerifyRequest(BaseModel):
    email: EmailStr
    verification_code: str

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "email-verify"}

@router.post("")
def verify_email(payload: VerifyRequest):
    """
    Verify user's email address using a valid verification code.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (payload.email,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email address not registered."
            )
            
        # Verify code
        cursor.execute(
            "SELECT code FROM verification_codes WHERE email = ?",
            (payload.email,)
        )
        code_entry = cursor.fetchone()
        if not code_entry or code_entry["code"] != payload.verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code."
            )
            
        # Set verified state
        cursor.execute(
            "UPDATE users SET email_verified = 1 WHERE email = ?",
            (payload.email,)
        )
        
        # Clear code
        cursor.execute("DELETE FROM verification_codes WHERE email = ?", (payload.email,))
        
        conn.commit()
        return {
            "status": "success",
            "message": "Email address verified successfully."
        }
    finally:
        conn.close()
