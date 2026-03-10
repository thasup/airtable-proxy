import sqlite3
from src.core.config import DB_PATH
import os
print(f"DB Path is {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(c.fetchall())
