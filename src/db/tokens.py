from typing import Optional
import uuid
from src.db.connection import get_db_connection

def get_active_token(token_hash: str) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, is_active, allowed_bases
        FROM agent_tokens
        WHERE token_hash = ? AND is_active = 1
    """, (token_hash,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_token(name: str, token_hash: str, allowed_bases: str) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    token_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO agent_tokens (id, name, token_hash, is_active, allowed_bases)
        VALUES (?, ?, ?, 1, ?)
    """, (token_id, name, token_hash, allowed_bases))
    conn.commit()
    conn.close()
    return token_id

def revoke_token(token_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE agent_tokens
        SET is_active = 0
        WHERE id = ?
    """, (token_id,))
    rowcount = cursor.rowcount
    conn.commit()
    conn.close()
    return rowcount > 0

def get_token_by_id(token_id: str) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, is_active, allowed_bases, created_at
        FROM agent_tokens
        WHERE id = ?
    """, (token_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
