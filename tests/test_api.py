from fastapi.testclient import TestClient

from app.main import app
from app.services.guardrail_service import is_in_scope


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_insurance_question_is_allowed():
    assert is_in_scope("What health insurance plans are available?")


def test_unrelated_question_is_restricted():
    assert not is_in_scope("Write a Python programming tutorial.")


def test_greeting_is_allowed():
    assert is_in_scope("Hello")


def test_out_of_scope_chat():
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "message": "Tell me about football.",
            "history": [],
        },
    )

    assert response.status_code == 200
    assert "health insurance assistant" in response.text.lower()
    assert '"type": "done"' in response.text
