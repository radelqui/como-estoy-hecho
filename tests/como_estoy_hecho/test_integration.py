"""Integration tests: auto-discovery mounts domain router and static UI."""
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_domain_router_auto_mounted():
    r = client.post(
        "/api/v1/como-estoy-hecho",
        json={"pregunta": "test"},
        headers={"X-Customer-Id": "C999"},
    )
    assert r.status_code in (200, 502)


def test_static_ui_serves_react_placeholder():
    r = client.get("/como-estoy-hecho/ui/")
    assert r.status_code == 200
    assert "react" in r.text
