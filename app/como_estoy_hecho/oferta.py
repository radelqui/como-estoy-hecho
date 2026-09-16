"""Cliente de solo lectura para /oferta/<coleccion> de SYPNOSE (API pública).

Una sola herramienta acotada, tal como pide TRASPASO-5 R4: este dominio SOLO lee
la composición registrada, nunca elige otro endpoint ni otra colección por prompt
-- la URL/colección la fija el entorno (SYPNOSE_OFERTA_URL), no el usuario.
"""
import os
from typing import Protocol

DEFAULT_OFERTA_URL = "https://coforge.sypnose.cloud/oferta/coforge-santander"


class OfertaError(Exception):
    """La composición no se pudo leer desde SYPNOSE (red, timeout, HTTP no-2xx)."""


class OfertaClient(Protocol):
    async def fetch(self) -> dict: ...


class HttpOfertaClient:
    """Cliente real. Import perezoso de httpx: no es dependencia dura de este
    módulo (motor falso / tests no lo necesitan tocar la red en absoluto)."""

    def __init__(self, url: str | None = None, timeout: float = 5.0):
        self.url = url or os.getenv("SYPNOSE_OFERTA_URL", DEFAULT_OFERTA_URL)
        self.timeout = timeout

    async def fetch(self) -> dict:
        import httpx

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.url)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as exc:
            raise OfertaError(f"no se pudo leer la oferta de SYPNOSE: {exc}") from exc
