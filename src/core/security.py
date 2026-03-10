import hashlib
import json
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.db.tokens import get_active_token

security = HTTPBearer()

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def verify_agent_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")
        
    token = credentials.credentials
    token_hash = hash_token(token)
    
    token_data = get_active_token(token_hash)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token")
    
    return token_data

def verify_base_access(base_id: str, token_data: dict):
    allowed_bases = token_data.get("allowed_bases", "[]")
    try:
        allowed_list = json.loads(allowed_bases)
    except Exception:
        allowed_list = []
        
    if "*" not in allowed_list and base_id not in allowed_list:
        raise HTTPException(status_code=403, detail="Not authorized to access this base")
