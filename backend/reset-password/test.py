import os
import sys
import importlib
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    reset_pwd_module = importlib.import_module("backend.reset-password.router")
    app = reset_pwd_module.router
except Exception as e:
    print(f"Failed to import backend.reset-password.router: {str(e)}", file=sys.stderr)
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
    assert response.json()["service"] == "reset-password"
    print("Health check: PASS")

def test_reset_password_flow():
    """Verify password reset endpoints."""
    print("Testing password reset flow...")
    from backend.database import get_db_connection
    from backend.utils.auth import verify_password
    
    test_email = "user@example.com"
    test_username = "testresetuser"
    initial_pwd_hash = "old_password_hash"
    
    # 1. Pre-populate DB with test user and code
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (real_name, username, email, password_hash) VALUES (?, ?, ?, ?)",
            ("Reset Test", test_username, test_email, initial_pwd_hash)
        )
        cursor.execute(
            "INSERT INTO verification_codes (email, code) VALUES (?, ?)",
            (test_email, "987654")
        )
        conn.commit()
        
        # 2. Reset password via endpoint
        response = client.post("", json={
            "email": test_email,
            "verification_code": "987654",
            "new_password": "brandnewpassword99"
        })
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # 3. Check updated hash
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (test_email,))
        user = cursor.fetchone()
        assert user is not None
        assert verify_password("brandnewpassword99", user["password_hash"])
        
        # 4. Check verification code got cleaned up
        cursor.execute("SELECT code FROM verification_codes WHERE email = ?", (test_email,))
        code_entry = cursor.fetchone()
        assert code_entry is None
        
        print("Password reset flow: PASS")
    finally:
        # Clean up
        cursor.execute("DELETE FROM users WHERE username = ?", (test_username,))
        cursor.execute("DELETE FROM verification_codes WHERE email = ?", (test_email,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    print("Starting reset-password tests...")
    try:
        test_health()
        test_reset_password_flow()
        print("\nAll reset-password tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
