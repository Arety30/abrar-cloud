import sqlite3
from pathlib import Path
from backend.config import settings

DB_PATH = settings.BASE_DIR / "backend" / "abrar_cloud.db"

def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        real_name TEXT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email_verified INTEGER DEFAULT 0
    )
    """)
    
    # Create Verification Codes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verification_codes (
        email TEXT PRIMARY KEY,
        code TEXT NOT NULL,
        expires_at INTEGER
    )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on import
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
init_db()
