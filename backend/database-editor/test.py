import os
import sys
import importlib
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package can be imported from parent path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Dynamically import the module since it contains a hyphen
try:
    db_editor_module = importlib.import_module("backend.database-editor.main")
    app = db_editor_module.app
except Exception as e:
    print(f"Failed to import backend.database-editor.main: {str(e)}", file=sys.stderr)
    sys.exit(1)

client = TestClient(app)

def test_health():
    """Verify that health check route is online."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "database-editor"
    print("Health check: PASS")

def test_database_crud():
    """Verify full CRUD operations using the API endpoints."""
    print("Testing database CRUD operations...")
    
    # 1. Create a temporary table
    create_sql = """
    CREATE TABLE IF NOT EXISTS temp_test_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        value REAL
    );
    """
    response = client.post("/query", json={"sql": create_sql})
    assert response.status_code == 200
    assert response.json()["type"] == "write"
    
    try:
        # 2. Insert record
        insert_payload = {
            "table_name": "temp_test_items",
            "data": {
                "name": "Widget A",
                "value": 19.99
            }
        }
        response = client.post("/insert", json=insert_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        last_id = data["last_row_id"]
        
        # 3. Read/Query record
        query_payload = {"sql": "SELECT * FROM temp_test_items WHERE name = 'Widget A';"}
        response = client.post("/query", json=query_payload)
        assert response.status_code == 200
        qdata = response.json()
        assert qdata["type"] == "select"
        assert qdata["row_count"] == 1
        assert qdata["data"][0]["value"] == 19.99
        
        # 4. Delete record
        delete_payload = {
            "table_name": "temp_test_items",
            "primary_key_col": "id",
            "primary_key_val": last_id
        }
        response = client.post("/delete", json=delete_payload)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # 5. Check if deleted
        response = client.post("/query", json=query_payload)
        assert response.status_code == 200
        assert response.json()["row_count"] == 0
        print("CRUD Operations: PASS")
        
    finally:
        # Clean up table
        client.post("/query", json={"sql": "DROP TABLE IF EXISTS temp_test_items;"})

if __name__ == "__main__":
    print("Starting database-editor tests...")
    try:
        test_health()
        test_database_crud()
        print("\nAll database-editor tests completed successfully! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertion Error: Test failed! {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}", file=sys.stderr)
        sys.exit(1)
