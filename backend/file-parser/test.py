import os
import io
import sys
import importlib
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Dynamically import the module since it contains a hyphen
try:
    file_parser_module = importlib.import_module("backend.file-parser.main")
    app = file_parser_module.app
    USER_FILES_DIR = file_parser_module.USER_FILES_DIR
except Exception as e:
    print(f"Failed to import backend.file-parser.main: {str(e)}", file=sys.stderr)
    sys.exit(1)

client = TestClient(app)

def test_health():
    """Verify that health check route is online."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "file-parser"
    print("Health check: PASS")

def test_parse_txt_upload():
    """Verify upload parsing for a Text file."""
    print("Testing text upload parsing...")
    test_content = "Hello, this is a test text file parsing validation."
    file_payload = {"file": ("test.txt", io.BytesIO(test_content.encode("utf-8")), "text/plain")}
    
    response = client.post("/parse/upload", files=file_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "temp_test.txt"
    assert data["extension"] == ".txt"
    assert data["content"] == test_content
    print("Text upload parsing: PASS")

def test_parse_workspace_txt():
    """Verify workspace parsing for a Text file."""
    print("Testing workspace text file parsing...")
    filename = "workspace_test.txt"
    filepath = USER_FILES_DIR / filename
    test_content = "This file is already in the workspace."
    
    # Pre-write file to workspace
    filepath.write_text(test_content, encoding="utf-8")
    
    try:
        response = client.post("/parse/workspace", json={"filename": filename})
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == filename
        assert data["extension"] == ".txt"
        assert data["content"] == test_content
        print("Workspace text parsing: PASS")
    finally:
        # Clean up
        if filepath.exists():
            filepath.unlink()

def test_nonexistent_file():
    """Verify that missing files return 404."""
    print("Testing missing file error handling...")
    response = client.post("/parse/workspace", json={"filename": "does_not_exist_xyz.txt"})
    assert response.status_code == 404
    print("Missing file handling: PASS")

if __name__ == "__main__":
    print("Starting file-parser tests...")
    try:
        test_health()
        test_parse_txt_upload()
        test_parse_workspace_txt()
        test_nonexistent_file()
        print("\nAll file-parser tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
