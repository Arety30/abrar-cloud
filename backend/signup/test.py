import os
import sys
import importlib
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Dynamically import the module since it contains a hyphen (if any, though signup does not, let's keep pattern)
try:
    signup_module = importlib.import_module("backend.signup.router")
    app = signup_module.router
except Exception as e:
    print(f"Failed to import backend.signup.router: {str(e)}", file=sys.stderr)
    sys.exit(1)

# Create a clean standalone FastAPI app for testing this router
from fastapi import FastAPI
test_app = FastAPI()
test_app.include_router(app)
client = TestClient(test_app)

def test_health():
    """Verify that health check route is online."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "signup"
    print("Health check: PASS")

def test_user_registration():
    """Verify user registration and constraints."""
    print("Testing user registration...")
    from backend.database import get_db_connection
    
    payload = {
        "real_name": "Test User",
        "username": "testsignupuser",
        "email": "user@example.com",
        "password": "securepassword123"
    }
    
    # 1. Register user
    response = client.post("", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user"]["username"] == payload["username"]
    
    # 2. Try registering duplicate
    response = client.post("", json=payload)
    assert response.status_code == 400
    
    # Clean up DB
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (payload["username"],))
        cursor.execute("DELETE FROM verification_codes WHERE email = ?", (payload["email"],))
        conn.commit()
        print("User registration: PASS")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting signup tests...")
    try:
        test_health()
        test_user_registration()
        print("\nAll signup tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
