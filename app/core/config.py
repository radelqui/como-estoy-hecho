# Origen: plantilla/microservicio/esqueleto/app/core/config.py · instanciado por instanciar_microservicio.py
import os

SERVICE_NAME = os.getenv("SERVICE_NAME", "como-estoy-hecho")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8010"))
USE_FAKE_ENGINE = os.getenv("USE_FAKE_ENGINE", "0") == "1"
