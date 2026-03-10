import logging
from src.db.connection import get_db_connection

logger = logging.getLogger("proxy")
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def log_access(agent_id: str, ip_address: str, status_code: int, path: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO access_logs (agent_id, ip_address, status_code, path)
            VALUES (?, ?, ?, ?)
        """, (agent_id, ip_address, status_code, path))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log to database: {e}")
        
    logger.info(f"Access - Agent: {agent_id}, IP: {ip_address}, Status: {status_code}, Path: {path}")
