import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from backend.main import app
except Exception as e:
    print(f"Failed to import backend.main: {str(e)}", file=sys.stderr)
    sys.exit(1)

client = TestClient(app)

def test_root_status():
    """Verify that root API status works."""
    print("Testing root API status...")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("Root status: PASS")

def test_integration_health():
    """Verify integration router health check."""
    print("Testing /backend/router/health...")
    response = client.get("/backend/router/health")
    assert response.status_code == 200
    assert response.json()["service"] == "root-integration-bridge"
    print("Integration health: PASS")

def test_serve_login_template():
    """Verify serving the Login HTML template."""
    print("Testing serving login template...")
    response = client.get("/backend/router/templates/login")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Abrar Cloud" in response.text
    assert "Username" in response.text
    print("Serving login template: PASS")

def test_list_templates():
    """Verify listing all templates."""
    print("Testing listing templates...")
    response = client.get("/backend/router")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "login" in response.text
    print("Listing templates: PASS")

def test_module_healthchecks():
    """Verify that all dynamically registered routers are online and accessible under the app."""
    print("Testing dynamic module health checks...")
    modules = [
        "login", "signup", "reset-password", "email-verify", "cloud",
        "file-parser", "fileeditor-ai", "audio-gen", "audio-parser",
        "image-creator", "image-editor", "image-parser", "pdf-editor",
        "ppt-editor", "spreadsheet-editor", "database-editor", "dod-editor"
    ]
    for module in modules:
        response = client.get(f"/{module}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    print("All module health checks: PASS")

if __name__ == "__main__":
    print("Starting root integration tests...")
    try:
        test_root_status()
        test_integration_health()
        test_serve_login_template()
        test_list_templates()
        test_module_healthchecks()
        print("\nAll integration and routing tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Integration test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during integration testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
