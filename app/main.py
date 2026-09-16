# Origen: plantilla/microservicio/esqueleto/app/main.py · instanciado por instanciar_microservicio.py
from fastapi import FastAPI

from app.api.health.routes import router as health_router

app = FastAPI(title="como-estoy-hecho")
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
