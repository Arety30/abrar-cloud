import os
import sys
import importlib
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    verify_module = importlib.import_module("backend.email-verify.router")
    app = verify_module.router
except Exception as e:
    print(f"Failed to import backend.email-verify.router: {str(e)}", file=sys.stderr)
    sys.exit(1)

from fastapi import FastAPI
test_app = FastAPI()
test_app.include_router(app)
client = TestClient(test_app)

def test_health():
    """Verify that health check route is online."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "email-verify"
    print("Health check: PASS")

def test_email_verification():
    """Verify email verification flow."""
    print("Testing email verification flow...")
    from backend.database import get_db_connection
    
    test_email = "user@example.com"
    test_username = "testverifyuser"
    
    # 1. Pre-populate DB with unverified user and code
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (real_name, username, email, password_hash, email_verified) VALUES (?, ?, ?, ?, ?)",
            ("Verify Test", test_username, test_email, "pwhash", 0)
        )
        cursor.execute(
            "INSERT INTO verification_codes (email, code) VALUES (?, ?)",
            (test_email, "112233")
        )
        conn.commit()
        
        # 2. Verify email via endpoint
        response = client.post("", json={
            "email": test_email,
            "verification_code": "112233"
        })
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # 3. Check verification status flag is 1
        cursor.execute("SELECT email_verified FROM users WHERE email = ?", (test_email,))
        user = cursor.fetchone()
        assert user is not None
        assert user["email_verified"] == 1
        
        # 4. Check code is deleted
        cursor.execute("SELECT code FROM verification_codes WHERE email = ?", (test_email,))
        code_entry = cursor.fetchone()
        assert code_entry is None
        
        print("Email verification flow: PASS")
    finally:
        # Clean up
        cursor.execute("DELETE FROM users WHERE username = ?", (test_username,))
        cursor.execute("DELETE FROM verification_codes WHERE email = ?", (test_email,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    print("Starting email-verify tests...")
    try:
        test_health()
        test_email_verification()
        print("\nAll email-verify tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
