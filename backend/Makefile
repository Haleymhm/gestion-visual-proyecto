.PHONY: help install dev db-up db-down db-seed clean test lint format

help:
	@echo "Comandos disponibles:"
	@echo "  make install      - Instala las dependencias"
	@echo "  make dev          - Inicia el servidor de desarrollo"
	@echo "  make db-up        - Inicia la base de datos con Docker"
	@echo "  make db-down      - Para la base de datos"
	@echo "  make db-logs      - Muestra los logs de la BD"
	@echo "  make clean        - Limpia archivos temporales"
	@echo "  make migrations   - Ejecuta las migraciones de Alembic"

install:
	pip install -r requirements.txt

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

db-up:
	docker-compose up -d

db-down:
	docker-compose down

db-logs:
	docker-compose logs -f db

db-seed:
	python -m scripts.seed_data

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -delete
	rm -rf .pytest_cache .coverage htmlcov

migrations:
	alembic upgrade head

migrate-new:
	alembic revision --autogenerate -m

migrate-downgrade:
	alembic downgrade -1

test:
	pytest

lint:
	pylint app/

format:
	black .
	isort .
