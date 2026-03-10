import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.connection import init_db

def test_missing_auth():
    init_db()
    with TestClient(app) as client:
        response = client.get("/v0/appTest/Table")
        assert response.status_code == 401

def test_invalid_auth():
    init_db()
    with TestClient(app) as client:
        response = client.get("/v0/appTest/Table", headers={"Authorization": "Bearer invalid"})
        assert response.status_code == 401
