import os
import sys
import importlib
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Dynamically import the module since it contains a hyphen
try:
    audio_gen_module = importlib.import_module("backend.audio-gen.main")
    app = audio_gen_module.app
    USER_FILES_DIR = audio_gen_module.USER_FILES_DIR
except Exception as e:
    print(f"Failed to import backend.audio-gen.main: {str(e)}", file=sys.stderr)
    sys.exit(1)

client = TestClient(app)

def test_health():
    """Verify that health check route is online."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "audio-gen"
    print("Health check: PASS")

def test_audio_generation():
    """Verify audio generation endpoint."""
    print("Testing audio generation...")
    filename = "test_generated_speech.wav"
    filepath = USER_FILES_DIR / filename
    
    try:
        response = client.post("/generate", json={
            "text": "AbrarCloud high-fidelity speech synthesizer test query",
            "voice": "alloy",
            "filename": filename
        })
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == filename
        
        # Verify file exists and is not empty
        assert filepath.exists()
        assert filepath.stat().st_size > 44  # Wave header is 44 bytes, so PCM must have frames
        
        print("Audio generation: PASS")
    finally:
        # Clean up
        if filepath.exists():
            filepath.unlink()

if __name__ == "__main__":
    print("Starting audio-gen tests...")
    try:
        test_health()
        test_audio_generation()
        print("\nAll audio-gen tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
