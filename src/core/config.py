import os

AIRTABLE_PAT = os.environ.get("AIRTABLE_PAT", "")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")
DB_PATH = os.environ.get("DB_PATH", "proxy.db")
