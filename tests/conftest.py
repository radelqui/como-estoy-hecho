# Origen: plantilla/microservicio/esqueleto/tests/conftest.py · instanciado por instanciar_microservicio.py
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
