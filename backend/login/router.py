from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from backend.database import get_db_connection
from backend.utils.auth import verify_password, create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

@router.post("")
def login(payload: LoginRequest):
    """
    Log in a user. Matches Username, Email, and Password as required by the UI.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query user by username and email
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND email = ?", 
        (payload.username, payload.email)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or email credentials."
        )
        
    # Verify password
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password."
        )
        
    # Generate token
    token_data = {"sub": user["username"], "email": user["email"]}
    access_token = create_access_token(token_data)
    
    return {
        "status": "success",
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "real_name": user["real_name"]
        }
    }
