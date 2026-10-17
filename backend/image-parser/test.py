import os
import io
import sys
import importlib
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Dynamically import the module since it contains a hyphen
try:
    image_parser_module = importlib.import_module("backend.image-parser.main")
    app = image_parser_module.app
    USER_FILES_DIR = image_parser_module.USER_FILES_DIR
except Exception as e:
    print(f"Failed to import backend.image-parser.main: {str(e)}", file=sys.stderr)
    sys.exit(1)

client = TestClient(app)

def create_mock_image() -> bytes:
    """Create a simple 10x10 red PNG image in-memory."""
    img = Image.new("RGB", (10, 10), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes.read()

def test_health():
    """Verify that health check route is online."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "image-parser"
    print("Health check: PASS")

def test_parse_image_upload():
    """Verify upload parsing for an image."""
    print("Testing image upload parsing...")
    img_data = create_mock_image()
    file_payload = {"file": ("test.png", io.BytesIO(img_data), "image/png")}
    
    response = client.post("/parse/upload", files=file_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "temp_test.png"
    assert data["metadata"]["width"] == 10
    assert data["metadata"]["height"] == 10
    assert data["metadata"]["format"] == "PNG"
    assert "mock" in data["description"].lower() or "ai description" in data["description"].lower()
    print("Image upload parsing: PASS")

def test_parse_workspace_image():
    """Verify workspace parsing for an image."""
    print("Testing workspace image parsing...")
    filename = "workspace_test_img.png"
    filepath = USER_FILES_DIR / filename
    img_data = create_mock_image()
    filepath.write_bytes(img_data)
    
    try:
        response = client.post("/parse/workspace", json={"filename": filename})
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == filename
        assert data["metadata"]["width"] == 10
        assert data["metadata"]["height"] == 10
        assert data["metadata"]["format"] == "PNG"
        print("Workspace image parsing: PASS")
    finally:
        # Clean up
        if filepath.exists():
            filepath.unlink()

if __name__ == "__main__":
    print("Starting image-parser tests...")
    try:
        test_health()
        test_parse_image_upload()
        test_parse_workspace_image()
        print("\nAll image-parser tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
