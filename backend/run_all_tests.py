import sys
import subprocess
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent

TESTS = [
    ("Signup Tests", BACKEND_DIR / "signup" / "test.py"),
    ("Reset Password Tests", BACKEND_DIR / "reset-password" / "test.py"),
    ("Email Verification Tests", BACKEND_DIR / "email-verify" / "test.py"),
    ("File Parser Tests", BACKEND_DIR / "file-parser" / "test.py"),
    ("Image Parser Tests", BACKEND_DIR / "image-parser" / "test.py"),
    ("Audio Parser Tests", BACKEND_DIR / "audio-parser" / "test.py"),
    ("Document Editor Tests", BACKEND_DIR / "dod-editor" / "test.py"),
    ("Database Editor Tests", BACKEND_DIR / "database-editor" / "test.py"),
    ("Image Creator Tests", BACKEND_DIR / "image-creator" / "test.py"),
    ("Audio Generator Tests", BACKEND_DIR / "audio-gen" / "test.py"),
    ("Root Integration Tests", BACKEND_DIR / "test_integration.py")
]

def run_tests():
    print("====================================================")
    print("          ABRARCLOUD BACKEND TEST RUNNER            ")
    print("====================================================\n")
    
    python_bin = sys.executable
    success_count = 0
    failures = []
    
    for label, test_path in TESTS:
        print(f"--- Running: {label} ---")
        if not test_path.exists():
            print(f"Error: Test file not found at {test_path}\n")
            failures.append((label, "Test file not found"))
            continue
            
        try:
            # Run the test script as a subprocess
            result = subprocess.run([python_bin, str(test_path)], capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
                print(f"Result: SUCCESS ✅\n")
                success_count += 1
            else:
                print(result.stdout)
                print(result.stderr, file=sys.stderr)
                print(f"Result: FAILED ❌ (Exit code {result.returncode})\n")
                failures.append((label, f"Exit code {result.returncode}"))
        except Exception as e:
            print(f"Result: EXCEPTION ❌ ({str(e)})\n")
            failures.append((label, f"Exception: {str(e)}"))
            
    print("====================================================")
    print("                   TEST SUMMARY                     ")
    print("====================================================")
    print(f"Total Tests Run: {len(TESTS)}")
    print(f"Passed: {success_count}/{len(TESTS)} ✅")
    
    if failures:
        print("\nFailures:")
        for label, error in failures:
            print(f" - {label}: {error} ❌")
        sys.exit(1)
    else:
        print("\nAll systems fully operational! 🎉")
        sys.exit(0)

if __name__ == "__main__":
    run_tests()
