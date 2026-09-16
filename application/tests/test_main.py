import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_create_normal_order():
    response = client.post(
        "/api/orders",
        json={
            "product_id": "DEVOPS-001",
            "quantity": 2,
            "mode": "normal",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "created"


def test_create_failed_order():
    response = client.post(
        "/api/orders",
        json={
            "product_id": "DEVOPS-002",
            "quantity": 1,
            "mode": "fail",
        },
    )

    assert response.status_code == 500


def test_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "chay_http_requests_total" in response.text
    assert "chay_orders_created_total" in response.text
