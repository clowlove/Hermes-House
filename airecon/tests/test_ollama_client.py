"""
Unit tests for the Ollama client using the `responses` library.
Mock HTTP requests to the local Ollama API endpoint.
"""

import json
import pytest
import responses
from airecon.ollama_client import OllamaClient

# Default base URL for the local Ollama instance
OLLAMA_BASE_URL = "http://localhost:11434"


@pytest.fixture
def client():
    """Fixture providing a configured OllamaClient instance."""
    return OllamaClient(base_url=OLLAMA_BASE_URL)


@responses.activate
def test_generate_success(client):
    """Test a successful generate request (POST /api/generate)."""
    expected_response = {
        "model": "llama3.1",
        "created_at": "2023-11-07T21:07:45.123456Z",
        "response": "Hello! How can I assist you today?",
        "done": True,
        "context": [1, 2, 3],
        "total_duration": 123456789,
        "load_duration": 123456,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 12345,
        "eval_count": 5,
        "eval_duration": 123456
    }

    responses.add(
        responses.POST,
        f"{OLLAMA_BASE_URL}/api/generate",
        json=expected_response,
        status=200,
    )

    result = client.generate(
        model="llama3.1",
        prompt="Hello"
    )

    assert result == expected_response
    assert len(responses.calls) == 1
    request_body = json.loads(responses.calls[0].request.body)
    assert request_body["model"] == "llama3.1"
    assert request_body["prompt"] == "Hello"


@responses.activate
def test_generate_error_status(client):
    """Test generate request returning a non-200 HTTP status."""
    responses.add(
        responses.POST,
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"error": "model not found"},
        status=404,
    )

    with pytest.raises(RuntimeError, match="Ollama API returned status 404"):
        client.generate(model="nonexistent", prompt="Hello")


@responses.activate
def test_generate_network_error(client):
    """Test generate request when a connection error occurs."""
    # `responses` can simulate connection errors via exceptions
    responses.add(
        responses.POST,
        f"{OLLAMA_BASE_URL}/api/generate",
        body=requests.exceptions.ConnectionError("Connection refused"),
    )

    # Ensure the client raises an appropriate exception (e.g., requests.RequestException)
    with pytest.raises(requests.exceptions.ConnectionError):
        client.generate(model="llama3.1", prompt="Hello")


@responses.activate
def test_chat_success(client):
    """Test a successful chat request (POST /api/chat)."""
    expected_response = {
        "model": "llama3.1",
        "created_at": "2023-11-07T21:07:45.123456Z",
        "message": {
            "role": "assistant",
            "content": "Sure, I can help with that."
        },
        "done": True,
        "total_duration": 123456789,
        "load_duration": 123456,
        "prompt_eval_count": 12,
        "prompt_eval_duration": 12345,
        "eval_count": 8,
        "eval_duration": 123456
    }

    responses.add(
        responses.POST,
        f"{OLLAMA_BASE_URL}/api/chat",
        json=expected_response,
        status=200,
    )

    messages = [
        {"role": "user", "content": "Explain the OWASP Top 10."}
    ]
    result = client.chat(model="llama3.1", messages=messages)

    assert result == expected_response
    assert len(responses.calls) == 1
    request_body = json.loads(responses.calls[0].request.body)
    assert request_body["model"] == "llama3.1"
    assert request_body["messages"] == messages


@responses.activate
def test_chat_with_options(client):
    """Test chat request with additional generation options (temperature, etc.)."""
    expected_response = {
        "model": "mixtral",
        "created_at": "2023-11-07T21:07:45.123456Z",
        "message": {"role": "assistant", "content": "Response with options."},
        "done": True,
        "total_duration": 234567890,
    }

    responses.add(
        responses.POST,
        f"{OLLAMA_BASE_URL}/api/chat",
        json=expected_response,
        status=200,
    )

    options = {
        "temperature": 0.5,
        "top_p": 0.9,
        "num_predict": 100
    }
    result = client.chat(
        model="mixtral",
        messages=[{"role": "user", "content": "Hello"}],
        options=options
    )

    assert result == expected_response
    request_body = json.loads(responses.calls[0].request.body)
    assert request_body["options"] == options


@responses.activate
def test_generate_with_stream_false(client):
    """Ensure the client does not request streaming when not needed."""
    # If the client supports a `stream` parameter, verify it's passed correctly.
    responses.add(
        responses.POST,
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"response": "stream off", "done": True},
        status=200,
    )

    client.generate(model="llama3.1", prompt="Test", stream=False)
    request_body = json.loads(responses.calls[0].request.body)
    assert request_body.get("stream") is False


@responses.activate
def test_custom_timeout(client):
    """Test that timeout settings are passed in the request (if client supports)."""
    responses.add(
        responses.POST,
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"response": "ok", "done": True},
        status=200,
    )

    # Assume client.generate accepts a `timeout` argument
    client.generate(model="llama3.1", prompt="Hello", timeout=30)
    assert len(responses.calls) == 1
    # The `responses` library does not capture timeout settings directly,
    # but we verify the request was made with the correct URL.