"""Enmascarado de PII en la respuesta del dominio "¿Cómo estoy hecho?".

Copia deliberada (no import) de la lógica de `rag-banking-agent/app/security/pii.py`
(`mask_pii`): el esqueleto de esta plantilla (TRASPASO-5 criterio 1) todavía no trae
un `app/security/pii.py` compartido -- lo extrae 02-backend-api -- y mi fence en este
worktree solo cubre `app/como_estoy_hecho/**`. En cuanto exista el módulo compartido,
esto debería sustituirse por un import de allí (issue anotado en el spec de la tarea).
"""
import re

IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}\b")
DNI_RE = re.compile(r"\b\d{8}[A-Z]\b")
CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def mask_pii(text: str) -> str:
    text = IBAN_RE.sub("[IBAN]", text)
    text = DNI_RE.sub("[DNI]", text)
    text = CARD_RE.sub("[TARJETA]", text)
    text = EMAIL_RE.sub("[EMAIL]", text)
    return text
