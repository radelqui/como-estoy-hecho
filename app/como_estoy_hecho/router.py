"""Dominio "¿Cómo estoy hecho?" (TRASPASO-5, PLAN-CS2-M, Tarea 57 / R1).

El agente responde leyendo su propia composición desde la API pública de SYPNOSE
(/oferta/<coleccion>) -- nunca desde texto fijo -- con el motor falso (determinista,
sin LLM real) citando ficheros@sha reales del payload recibido. Regla de identidad:
igual que en rag-banking-agent, el cliente no se autodeclara con un dato de negocio;
aquí se exige la cabecera X-Customer-Id.

Integración: `app/main.py` (esqueleto-v1.1) autodescubre este router
(`app.{paquete}.router.router`) y monta `app/como_estoy_hecho/static/` como
StaticFiles en `/como-estoy-hecho/ui/` -- no hay que registrar nada a mano
aquí ni definir una ruta propia para servir el HTML (ver `_autodiscover` en
`app/main.py`).

Nota de integración pendiente (fuera de mi fence en este worktree,
`app/como_estoy_hecho/**` y `tests/como_estoy_hecho/**` solamente):
`app/security/middleware.py` (CustomerIdMiddleware) devuelve 403 cuando falta
X-Customer-Id; el EARS de esta tarea pide 401. Como esta ruta empieza por
`/api/v1/como-estoy-hecho` (no `/api/v1/health`), la middleware compartida
interceptaría la request ANTES de llegar aquí y respondería 403, no 401. Este
router hace su propia comprobación de identidad para cumplir el EARS con
independencia de esa middleware; si un día decide seguir aplicando, alguien con
permiso en `app/security/` debe alinear el código de estado (403 vs 401) o
excluir esta ruta de la comprobación genérica.
"""
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.como_estoy_hecho.oferta import HttpOfertaClient, OfertaClient, OfertaError
from app.como_estoy_hecho.pii import mask_pii

log = logging.getLogger(__name__)
router = APIRouter()


def get_oferta_client() -> OfertaClient:
    return HttpOfertaClient()


def _citas_ficheros(oferta: dict) -> list[str]:
    """Extrae "ruta@sha" reales del payload de /oferta -- nunca inventados."""
    citas: list[str] = []
    lineas = oferta.get("soluciones") or oferta.get("lineas") or []
    if isinstance(lineas, dict):
        lineas = [lineas]
    for linea in lineas:
        for fichero in linea.get("ficheros", []) or []:
            ruta = fichero.get("ruta") or fichero.get("path")
            sha = fichero.get("sha")
            if ruta and sha:
                citas.append(f"{ruta}@{sha}")
    # payload plano alternativo: {"ficheros": [...]} en la raíz
    for fichero in oferta.get("ficheros", []) or []:
        ruta = fichero.get("ruta") or fichero.get("path")
        sha = fichero.get("sha")
        if ruta and sha:
            citas.append(f"{ruta}@{sha}")
    return citas


def _responder_motor_falso(oferta: dict) -> str:
    """Motor falso (USE_FAKE_ENGINE): determinista, cita solo lo recibido."""
    citas = _citas_ficheros(oferta)
    if not citas:
        return "Estoy hecho de la composición registrada en SYPNOSE, sin ficheros citables ahora mismo."
    return "Estoy hecho de: " + ", ".join(citas) + "."


@router.post("/api/v1/como-estoy-hecho")
async def como_estoy_hecho(request: Request, oferta_client: OfertaClient = Depends(get_oferta_client)):
    customer_id = request.headers.get("x-customer-id") or getattr(request.state, "customer_id", None)
    if not customer_id:
        return JSONResponse(status_code=401, content={"detail": "X-Customer-Id requerido"})

    try:
        oferta = await oferta_client.fetch()
    except OfertaError:
        log.exception("fallo leyendo /oferta de SYPNOSE")
        return JSONResponse(
            status_code=502, content={"detail": "No se pudo leer la composición desde SYPNOSE"}
        )

    respuesta = _responder_motor_falso(oferta)
    return {"respuesta": mask_pii(respuesta)}
