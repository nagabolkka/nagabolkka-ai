import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

KEY = "test-key"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "ai_internal_key", KEY)
    monkeypatch.setattr(settings, "openai_api_key", "")  
    return TestClient(app, headers={"X-Internal-Key": KEY})