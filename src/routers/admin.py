import json
import secrets
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.config import ADMIN_SECRET
from src.core.security import hash_token
from src.db.tokens import create_token, revoke_token, get_token_by_id

router = APIRouter(prefix="/admin/tokens")
security = HTTPBearer()

def verify_admin(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not credentials or credentials.credentials != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

class TokenCreate(BaseModel):
    name: str
    allowed_bases: List[str]

@router.post("")
def create_new_token(data: TokenCreate, _=Depends(verify_admin)):
    raw_token = "sk_agent_" + secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    
    allowed_bases_str = json.dumps(data.allowed_bases)
    token_id = create_token(data.name, token_hash, allowed_bases_str)
    
    created = get_token_by_id(token_id)
    if not created:
         raise HTTPException(status_code=500, detail="Failed to create token")
         
    return {
        "id": created["id"],
        "token": raw_token,
        "name": created["name"],
        "allowed_bases": json.loads(created["allowed_bases"]),
        "created_at": created["created_at"],
        "is_active": bool(created["is_active"])
    }

@router.delete("/{token_id}")
def revoke_existing_token(token_id: str, _=Depends(verify_admin)):
    success = revoke_token(token_id)
    if not success:
        raise HTTPException(status_code=404, detail="Token not found or already revoked")
    return {"status": "success"}
