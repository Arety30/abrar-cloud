import os
import sys
import importlib
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Dynamically import the module since it contains a hyphen
try:
    dod_editor_module = importlib.import_module("backend.dod-editor.main")
    app = dod_editor_module.app
    USER_FILES_DIR = dod_editor_module.USER_FILES_DIR
except Exception as e:
    print(f"Failed to import backend.dod-editor.main: {str(e)}", file=sys.stderr)
    sys.exit(1)

client = TestClient(app)

def test_health():
    """Verify that health check route is online."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "dod-editor"
    print("Health check: PASS")

def test_document_editing():
    """Verify editing a file via agent instruction."""
    print("Testing document editing...")
    filename = "test_edit.txt"
    filepath = USER_FILES_DIR / filename
    filepath.write_text("Line 1: AbrarCloud Project\nLine 2: Empty content\n")
    
    try:
        response = client.post("/edit", json={
            "filename": filename,
            "instruction": "Change 'Empty content' to 'AI Agent modified this content successfully'",
            "create_if_missing": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == filename
        
        # Verify changes took place in the file
        updated_text = filepath.read_text()
        assert "modified" in updated_text.lower() or "agent" in updated_text.lower()
        print("Document editing: PASS")
    finally:
        # Clean up
        if filepath.exists():
            filepath.unlink()

if __name__ == "__main__":
    print("Starting dod-editor tests...")
    try:
        test_health()
        test_document_editing()
        print("\nAll dod-editor tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
