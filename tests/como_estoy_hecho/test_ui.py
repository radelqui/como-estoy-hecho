# Origen: PLAN-CS2-U, Tarea 66 (R0) / 67 (R1) — interfaz real del dominio.
"""R0 (EARS literal del registro): el HTML servido en GET /como-estoy-hecho/ui
contiene 'react', 'fetch(' y '/api/v1/como-estoy-hecho', y el motor falso
responde a través de la UI (mismo endpoint que consume el fetch de la página).

App de pruebas aislada, igual que test_como_estoy_hecho.py: solo el router de
este dominio, sin app.main.app (fuera de mi fence en este worktree).
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.como_estoy_hecho.oferta import OfertaError
from app.como_estoy_hecho.router import get_oferta_client, router


class FakeOfertaClient:
    def __init__(self, payload=None, fail=False):
        self.payload = payload or {}
        self.fail = fail

    async def fetch(self) -> dict:
        if self.fail:
            raise OfertaError("boom")
        return self.payload


OFERTA_REAL = {
    "soluciones": [
        {"ficheros": [{"ruta": "app/como_estoy_hecho/router.py", "sha": "f792e77"}]}
    ]
}


def make_app(oferta_client) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_oferta_client] = lambda: oferta_client
    return app


def test_ui_sirve_html_con_react_fetch_y_endpoint():
    client = TestClient(make_app(FakeOfertaClient(OFERTA_REAL)))
    r = client.get("/como-estoy-hecho/ui")
    assert r.status_code == 200
    html = r.text.lower()
    assert "react" in html
    assert "fetch(" in html
    assert "/api/v1/como-estoy-hecho" in html


def test_ui_es_responsive():
    client = TestClient(make_app(FakeOfertaClient(OFERTA_REAL)))
    html = client.get("/como-estoy-hecho/ui").text.lower()
    assert "viewport" in html


def test_motor_falso_responde_al_endpoint_que_llama_la_ui():
    """El endpoint que la UI invoca (mismo ENDPOINT del fetch, /api/v1/como-estoy-hecho)
    responde de verdad con el motor falso -- no es una página estática sin trasfondo."""
    client = TestClient(make_app(FakeOfertaClient(OFERTA_REAL)))
    r = client.post(
        "/api/v1/como-estoy-hecho",
        json={"pregunta": "¿cómo estás hecho?"},
        headers={"X-Customer-Id": "C123"},
    )
    assert r.status_code == 200
    assert "app/como_estoy_hecho/router.py@f792e77" in r.json()["respuesta"]
