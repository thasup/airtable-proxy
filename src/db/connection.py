import sqlite3
from src.core.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # AgentToken
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_tokens (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            allowed_bases TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # AccessLog
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            agent_id TEXT,
            ip_address TEXT,
            status_code INTEGER,
            path TEXT
        )
    """)
    
    conn.commit()
    conn.close()
