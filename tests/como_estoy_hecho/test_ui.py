# Origen: PLAN-CS2-U, Tarea 66 (R0) / 67 (R1) — interfaz real del dominio.
"""R1 (EARS literal del registro): al servirse la interfaz de como-estoy-hecho,
debe cargar React/ReactDOM desde CDN, mostrar X-Customer-Id + textarea, hacer
fetch al POST /api/v1/como-estoy-hecho con lectura en streaming, renderizar la
respuesta y los ficheros citados como enlaces, ser responsive; el test debe
comprobar 'react', 'fetch(' y '/api/v1/como-estoy-hecho' en el HTML servido, y
que el motor falso responde a través de la UI.

Tras el merge del esqueleto-v1.1 (auto-discovery), `app/main.py` monta este
router y sirve `app/como_estoy_hecho/static/` en `/como-estoy-hecho/ui/`
automáticamente -- se prueba contra la app REAL (`app.main.app`), no una app
aislada, tal como pide el brief de la Tarea 67.
"""
from fastapi.testclient import TestClient

from app.como_estoy_hecho.oferta import OfertaError
from app.como_estoy_hecho.router import get_oferta_client
from app.main import app


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


def make_client(oferta_client) -> TestClient:
    app.dependency_overrides[get_oferta_client] = lambda: oferta_client
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_ui_servida_por_app_main_con_react_fetch_y_endpoint():
    client = make_client(FakeOfertaClient(OFERTA_REAL))
    r = client.get("/como-estoy-hecho/ui/")
    assert r.status_code == 200
    html = r.text.lower()
    assert "react" in html
    assert "fetch(" in html
    assert "/api/v1/como-estoy-hecho" in html


def test_ui_bare_path_redirige_o_sirve_la_pagina():
    client = make_client(FakeOfertaClient(OFERTA_REAL))
    r = client.get("/como-estoy-hecho/ui")  # sin barra final
    assert r.status_code == 200
    assert "react" in r.text.lower()


def test_ui_es_responsive():
    client = make_client(FakeOfertaClient(OFERTA_REAL))
    html = client.get("/como-estoy-hecho/ui/").text.lower()
    assert "viewport" in html


def test_motor_falso_responde_a_traves_de_la_ui_por_app_main():
    """El endpoint que la UI invoca (mismo ENDPOINT del fetch,
    /api/v1/como-estoy-hecho) responde de verdad con el motor falso, montado
    por la app real vía auto-discovery -- no una página estática sin trasfondo."""
    client = make_client(FakeOfertaClient(OFERTA_REAL))
    r = client.post(
        "/api/v1/como-estoy-hecho",
        json={"pregunta": "¿cómo estás hecho?"},
        headers={"X-Customer-Id": "C123"},
    )
    assert r.status_code == 200
    assert "app/como_estoy_hecho/router.py@f792e77" in r.json()["respuesta"]
