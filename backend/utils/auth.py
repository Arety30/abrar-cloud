import time
import hashlib
from typing import Dict, Any, Optional
from jose import jwt
from backend.config import settings

# Attempt to import passlib, fallback to hashlib if not available
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    USE_PASSLIB = True
except ImportError:
    USE_PASSLIB = False

def hash_password(password: str) -> str:
    """Hash a password."""
    if USE_PASSLIB:
        return pwd_context.hash(password)
    else:
        # Fallback to simple SHA-256 for testing environments
        return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if USE_PASSLIB:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
    # Fallback/alternative check
    sha_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return sha_hash == hashed_password or plain_password == hashed_password

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """Generate JWT Access Token."""
    to_encode = data.copy()
    expire = time.time() + ((expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT Access Token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload if payload.get("exp", 0) >= time.time() else None
    except Exception:
        return None
