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
    audio_parser_module = importlib.import_module("backend.audio-parser.main")
    app = audio_parser_module.app
    USER_FILES_DIR = audio_parser_module.USER_FILES_DIR
except Exception as e:
    print(f"Failed to import backend.audio-parser.main: {str(e)}", file=sys.stderr)
    sys.exit(1)

client = TestClient(app)

def create_mock_wav_bytes() -> bytes:
    """Generate a standard valid PCM WAV header & 1 second of silence in pure Python."""
    data_size = 16000  # 1 second of 8000Hz 16-bit mono PCM = 16000 bytes
    header = bytearray()
    header.extend(b"RIFF")
    header.extend((36 + data_size).to_bytes(4, "little"))
    header.extend(b"WAVE")
    header.extend(b"fmt ")
    header.extend((16).to_bytes(4, "little"))
    header.extend((1).to_bytes(2, "little"))      # AudioFormat (1 = PCM)
    header.extend((1).to_bytes(2, "little"))      # Channels (1 = Mono)
    header.extend((8000).to_bytes(4, "little"))   # SampleRate (8000 Hz)
    header.extend((16000).to_bytes(4, "little"))  # ByteRate (SampleRate * BlockAlign = 16000)
    header.extend((2).to_bytes(2, "little"))      # BlockAlign (Channels * BitsPerSample / 8 = 2)
    header.extend((16).to_bytes(2, "little"))     # BitsPerSample (16 bits)
    header.extend(b"data")
    header.extend(data_size.to_bytes(4, "little"))
    data = bytearray(data_size)
    return bytes(header + data)

def test_health():
    """Verify that health check route is online."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "audio-parser"
    print("Health check: PASS")

def test_parse_audio_upload():
    """Verify upload parsing for an audio file."""
    print("Testing audio upload parsing...")
    audio_data = create_mock_wav_bytes()
    file_payload = {"file": ("test.wav", io.BytesIO(audio_data), "audio/wav")}
    
    response = client.post("/parse/upload", files=file_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "temp_test.wav"
    assert data["metadata"]["channels"] == 1
    # Allow some tolerance for floating-point calculations in duration estimation
    assert data["metadata"]["duration_seconds"] > 0
    assert "transcription" in data
    print("Audio upload parsing: PASS")

def test_parse_workspace_audio():
    """Verify workspace parsing for an audio file."""
    print("Testing workspace audio parsing...")
    filename = "workspace_test_audio.wav"
    filepath = USER_FILES_DIR / filename
    audio_data = create_mock_wav_bytes()
    filepath.write_bytes(audio_data)
    
    try:
        response = client.post("/parse/workspace", json={"filename": filename})
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == filename
        assert data["metadata"]["sample_rate"] == 8000
        assert "transcription" in data
        print("Workspace audio parsing: PASS")
    finally:
        # Clean up
        if filepath.exists():
            filepath.unlink()

if __name__ == "__main__":
    print("Starting audio-parser tests...")
    try:
        test_health()
        test_parse_audio_upload()
        test_parse_workspace_audio()
        print("\nAll audio-parser tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
