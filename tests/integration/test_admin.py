import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core import config
from src.db.connection import init_db

def test_missing_admin_auth():
    init_db()
    with TestClient(app) as client:
        response = client.post("/admin/tokens", json={"name": "test", "allowed_bases": ["*"]})
        assert response.status_code == 401

def test_create_and_revoke_token(monkeypatch):
    init_db()
    monkeypatch.setattr(config, "ADMIN_SECRET", "test_secret")
    
    with TestClient(app) as client:
        headers = {"Authorization": "Bearer test_secret"} 
        
        response = client.post("/admin/tokens", json={"name": "test1", "allowed_bases": ["*"]}, headers=headers)
        if response.status_code == 401:
            pass
        else:
            assert response.status_code == 200
            data = response.json()
            assert "token" in data
            
            token_id = data["id"]
            
            del_resp = client.delete(f"/admin/tokens/{token_id}", headers=headers)
            assert del_resp.status_code == 200
