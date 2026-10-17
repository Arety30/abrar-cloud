import sqlite3
from typing import Dict, Any, List
from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.database import get_db_connection

router = APIRouter()
app = FastAPI(title="Database Editor Service")

class QueryRequest(BaseModel):
    sql: str

class InsertRequest(BaseModel):
    table_name: str
    data: Dict[str, Any]

class DeleteRequest(BaseModel):
    table_name: str
    primary_key_col: str
    primary_key_val: Any

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "database-editor"}

@router.get("/tables")
def list_tables():
    """Fetch list of all tables in the SQLite database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row["name"] for row in cursor.fetchall()]
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@router.post("/query")
def run_query(payload: QueryRequest):
    """Execute raw SQL query and return results (if SELECT) or execution status."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(payload.sql)
        
        # Check if the query returns data
        is_select = payload.sql.strip().lower().startswith("select") or "returning" in payload.sql.lower()
        
        if is_select:
            columns = [description[0] for description in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            return {
                "type": "select",
                "columns": columns,
                "row_count": len(results),
                "data": results
            }
        else:
            conn.commit()
            return {
                "type": "write",
                "affected_rows": cursor.rowcount,
                "message": "Query executed successfully"
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SQL Execution Error: {str(e)}"
        )
    finally:
        conn.close()

@router.post("/insert")
def insert_record(payload: InsertRequest):
    """Insert a record into the specified table."""
    if not payload.data:
        raise HTTPException(status_code=400, detail="Data payload cannot be empty.")
        
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        columns = ", ".join(payload.data.keys())
        placeholders = ", ".join(["?"] * len(payload.data))
        values = list(payload.data.values())
        
        sql = f"INSERT INTO {payload.table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        conn.commit()
        
        return {
            "status": "success",
            "message": f"Record inserted into '{payload.table_name}' successfully.",
            "last_row_id": cursor.lastrowid
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insert Error: {str(e)}"
        )
    finally:
        conn.close()

@router.post("/delete")
def delete_record(payload: DeleteRequest):
    """Delete a record from the specified table."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql = f"DELETE FROM {payload.table_name} WHERE {payload.primary_key_col} = ?"
        cursor.execute(sql, (payload.primary_key_val,))
        conn.commit()
        
        return {
            "status": "success",
            "message": f"Record deleted from '{payload.table_name}' successfully.",
            "affected_rows": cursor.rowcount
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Delete Error: {str(e)}"
        )
    finally:
        conn.close()

app.include_router(router)
