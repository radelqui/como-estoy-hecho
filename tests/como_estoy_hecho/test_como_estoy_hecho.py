# Origen: generado por instanciar_microservicio.py (dominio como-estoy-hecho)
"""R1 (PLAN-CS2-M, Tarea 57): identidad requerida, motor falso lee /oferta de
SYPNOSE (nunca texto fijo), PII enmascarada, sin filtrar identificadores internos.

App de pruebas AISLADA: solo el router de este dominio, sin app.main.app -- mi
fence en este worktree es `app/como_estoy_hecho/**` y `tests/como_estoy_hecho/**`,
no `app/main.py` (ver nota de integración en app/como_estoy_hecho/router.py).
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.como_estoy_hecho.oferta import OfertaError
from app.como_estoy_hecho.pii import mask_pii
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
        {
            "nombre": "rag-banking-agent",
            "ficheros": [
                {"ruta": "app/agent/runtime.py", "sha": "5acef41"},
                {"ruta": "app/agent/tools.py", "sha": "c1afb6d"},
            ],
        }
    ],
    "id_interno_registro": "no-debe-aparecer-nunca-en-la-respuesta",
}


def make_app(oferta_client) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_oferta_client] = lambda: oferta_client
    return app


def test_sin_x_customer_id_devuelve_401():
    client = TestClient(make_app(FakeOfertaClient(OFERTA_REAL)))
    r = client.post("/api/v1/como-estoy-hecho", json={"pregunta": "¿cómo estás hecho?"})
    assert r.status_code == 401


def test_con_identidad_responde_citando_ficheros_reales_de_la_oferta():
    client = TestClient(make_app(FakeOfertaClient(OFERTA_REAL)))
    r = client.post(
        "/api/v1/como-estoy-hecho",
        json={"pregunta": "¿cómo estás hecho?"},
        headers={"X-Customer-Id": "C123"},
    )
    assert r.status_code == 200
    respuesta = r.json()["respuesta"]
    # cita ficheros@sha REALES del payload recibido -- no texto fijo/inventado
    assert "app/agent/runtime.py@5acef41" in respuesta
    assert "app/agent/tools.py@c1afb6d" in respuesta


def test_no_filtra_identificadores_internos_del_payload():
    client = TestClient(make_app(FakeOfertaClient(OFERTA_REAL)))
    r = client.post(
        "/api/v1/como-estoy-hecho",
        json={"pregunta": "¿cómo estás hecho?"},
        headers={"X-Customer-Id": "C123"},
    )
    assert "no-debe-aparecer-nunca-en-la-respuesta" not in r.json()["respuesta"]


def test_respuesta_enmascara_pii_si_aparece_en_los_ficheros_citados():
    oferta_con_pii = {
        "soluciones": [
            {
                "ficheros": [
                    {"ruta": "docs/informe-12345678Z.md", "sha": "abc1234"},
                ]
            }
        ]
    }
    client = TestClient(make_app(FakeOfertaClient(oferta_con_pii)))
    r = client.post(
        "/api/v1/como-estoy-hecho",
        json={"pregunta": "¿cómo estás hecho?"},
        headers={"X-Customer-Id": "C123"},
    )
    respuesta = r.json()["respuesta"]
    assert "12345678Z" not in respuesta
    assert "[DNI]" in respuesta


def test_mask_pii_enmascara_iban_dni_tarjeta_email():
    out = mask_pii("IBAN ES91 2100 0418 4502 0005 1332, DNI 12345678Z, mail a@b.com")
    assert "[IBAN]" in out and "[DNI]" in out and "[EMAIL]" in out
    assert "ES91" not in out and "12345678Z" not in out and "a@b.com" not in out


def test_fallo_leyendo_oferta_devuelve_502_no_texto_fijo():
    client = TestClient(make_app(FakeOfertaClient(fail=True)))
    r = client.post(
        "/api/v1/como-estoy-hecho",
        json={"pregunta": "¿cómo estás hecho?"},
        headers={"X-Customer-Id": "C123"},
    )
    assert r.status_code == 502
