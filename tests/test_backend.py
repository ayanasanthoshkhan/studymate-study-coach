
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.memory import (
    create_conversation,
    save_message,
    get_history,
    get_memory_info
)

client = TestClient(app)


# TEST 1: API home endpoint
def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert "running" in response.json()["message"]


# TEST 2: Four study modes available
def test_study_modes():
    response = client.get("/modes")

    assert response.status_code == 200
    assert len(response.json()["modes"]) == 4


# TEST 3: Invalid study mode
def test_invalid_mode():
    response = client.post(
        "/chat",
        json={
            "message": "Explain Python",
            "conversation_id": None,
            "mode": "InvalidMode"
        }
    )

    assert response.status_code == 400


# TEST 4: Conversation truncation
def test_memory_truncation():
    conversation_id = create_conversation()

    for i in range(12):
        role = "user" if i % 2 == 0 else "model"

        save_message(
            conversation_id,
            role,
            f"Message {i + 1}"
        )

    history = get_history(conversation_id)
    memory = get_memory_info(conversation_id)

    assert len(history) == 10
    assert history[0]["content"] == "Message 3"
    assert history[-1]["content"] == "Message 12"

    assert memory["retained_messages"] == 10
    assert memory["truncated_messages"] == 2
    assert memory["truncation_active"] is True


# TEST 5: Chat endpoint without Gemini call
def test_chat_with_mocked_gemini():
    with patch(
        "backend.main.get_chatbot_response",
        return_value="Python is a programming language."
    ):
        response = client.post(
            "/chat",
            json={
                "message": "What is Python?",
                "conversation_id": None,
                "mode": "Explain"
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert "conversation_id" in data
    assert data["mode"] == "Explain"
    assert data["memory"]["retained_messages"] == 2


# TEST 6: Empty message
def test_empty_message():
    response = client.post(
        "/chat",
        json={
            "message": "   ",
            "conversation_id": None,
            "mode": "Explain"
        }
    )

    assert response.status_code == 400


# TEST 7: Unknown conversation ID
def test_unknown_conversation():
    response = client.post(
        "/chat",
        json={
            "message": "Hello",
            "conversation_id": "nonexistent-id",
            "mode": "Explain"
        }
    )

    assert response.status_code == 404


from google.genai import errors


# TEST 8: Gemini rate limit
def test_gemini_rate_limit():

    error = errors.ClientError(
        429,
        {"error": {
            "message": "Rate limit reached",
            "status": "RESOURCE_EXHAUSTED"
        }}
    )

    with patch(
        "backend.main.get_chatbot_response",
        side_effect=error
    ):
        response = client.post(
            "/chat",
            json={
                "message": "Explain Python",
                "conversation_id": None,
                "mode": "Explain"
            }
        )

    assert response.status_code == 429
    assert "rate limit" in response.json()["detail"].lower()


# TEST 9: Gemini server unavailable
def test_gemini_server_error():

    error = errors.ServerError(
        503,
        {"error": {
            "message": "Service unavailable",
            "status": "UNAVAILABLE"
        }}
    )

    with patch(
        "backend.main.get_chatbot_response",
        side_effect=error
    ):
        response = client.post(
            "/chat",
            json={
                "message": "Explain neural networks",
                "conversation_id": None,
                "mode": "Explain"
            }
        )

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


# TEST 10: AI request timeout
def test_gemini_timeout():

    with patch(
        "backend.main.get_chatbot_response",
        side_effect=TimeoutError("Request timed out")
    ):
        response = client.post(
            "/chat",
            json={
                "message": "Explain machine learning",
                "conversation_id": None,
                "mode": "Explain"
            }
        )

    assert response.status_code == 504
    assert "timed out" in response.json()["detail"].lower()

import httpx

# TEST 11: HTTP transport timeout
def test_http_transport_timeout():

    with patch(
        "backend.main.get_chatbot_response",
        side_effect=httpx.ReadTimeout(
            "Simulated Gemini timeout"
        )
    ):
        response = client.post(
            "/chat",
            json={
                "message": "Explain gradient descent",
                "conversation_id": None,
                "mode": "Explain"
            }
        )

    assert response.status_code == 504
    assert "timed out" in response.json()["detail"].lower()
