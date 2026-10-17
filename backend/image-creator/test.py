import os
import sys
import importlib
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Dynamically import the module since it contains a hyphen
try:
    image_creator_module = importlib.import_module("backend.image-creator.main")
    app = image_creator_module.app
    USER_FILES_DIR = image_creator_module.USER_FILES_DIR
except Exception as e:
    print(f"Failed to import backend.image-creator.main: {str(e)}", file=sys.stderr)
    sys.exit(1)

client = TestClient(app)

def test_health():
    """Verify that health check route is online."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "image-creator"
    print("Health check: PASS")

def test_image_generation():
    """Verify image generation endpoint."""
    print("Testing image generation...")
    filename = "test_generated_output.png"
    filepath = USER_FILES_DIR / filename
    
    try:
        response = client.post("/generate", json={
            "prompt": "Test visual prompt",
            "width": 256,
            "height": 256,
            "filename": filename
        })
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == filename
        
        # Verify file exists and is indeed a valid image of 256x256
        assert filepath.exists()
        with Image.open(filepath) as img:
            assert img.width == 256
            assert img.height == 256
            
        print("Image generation: PASS")
    finally:
        # Clean up
        if filepath.exists():
            filepath.unlink()

if __name__ == "__main__":
    print("Starting image-creator tests...")
    try:
        test_health()
        test_image_generation()
        print("\nAll image-creator tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
