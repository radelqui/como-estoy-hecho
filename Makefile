# Origen: plantilla/microservicio/esqueleto/Makefile · instanciado por instanciar_microservicio.py
.PHONY: install test lint dev run

SERVICE_NAME ?= como-estoy-hecho
SERVICE_PORT ?= 8010

install:
	pip3 install -e ".[dev]"

test:
	python3 -m pytest tests/ -v --tb=short

lint:
	ruff check app/ tests/
	ruff format --check app/ tests/

dev:
	uvicorn app.main:app --host 0.0.0.0 --port $(SERVICE_PORT) --reload

run:
	uvicorn app.main:app --host 0.0.0.0 --port $(SERVICE_PORT)
