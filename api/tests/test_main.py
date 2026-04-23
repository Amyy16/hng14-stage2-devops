import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


with patch("redis.Redis") as mock_redis_class:
    mock_redis_instance = MagicMock()
    mock_redis_class.return_value = mock_redis_instance
    mock_redis_instance.ping.return_value = True
    from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_mock():
    """Reset mock state before every test so they don't interfere"""
    mock_redis_instance.reset_mock()
    yield


# ── Test 1: Health endpoint ──────────────────────────────────────
def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ── Test 2: Create job returns a job_id ─────────────────────────
def test_create_job_returns_job_id():
    mock_redis_instance.lpush.return_value = 1
    mock_redis_instance.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID is always 36 chars


# ── Test 3: Create job pushes to Redis queue ─────────────────────
def test_create_job_pushes_to_redis():
    mock_redis_instance.lpush.return_value = 1
    mock_redis_instance.hset.return_value = 1

    response = client.post("/jobs")
    job_id = response.json()["job_id"]

    # Confirm job was pushed to the queue
    mock_redis_instance.lpush.assert_called_once()

    # Confirm status was set to queued
    mock_redis_instance.hset.assert_called_once_with(
        f"job:{job_id}", "status", "queued"
    )
