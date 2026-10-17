import sqlite3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from backend.database import get_db_connection
from backend.utils.auth import hash_password

router = APIRouter()

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    verification_code: str
    new_password: str

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "reset-password"}

@router.post("")
def reset_password(payload: ResetPasswordRequest):
    """
    Reset user password if email and verification code are valid.
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
                detail="Email address not found."
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
                detail="Invalid verification code."
            )
            
        # Update password hash
        new_hash = hash_password(payload.new_password)
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (new_hash, payload.email)
        )
        
        # Clear verification code
        cursor.execute("DELETE FROM verification_codes WHERE email = ?", (payload.email,))
        
        conn.commit()
        return {
            "status": "success",
            "message": "Password reset successfully."
        }
    finally:
        conn.close()
