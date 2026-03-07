# Makefile for ScraperFC API

.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate

help:
	@echo "ScraperFC API - Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean cache files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker Compose"
	@echo "  make docker-down  - Stop Docker Compose"
	@echo "  make migrate      - Run database migrations"

install:
	pip install -e .

dev:
	uvicorn app.main:app --reload --port 8000

test:
	pytest test/ -v

lint:
	ruff check app/
	mypy app/

format:
	ruff format app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t scraperfc-api .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(message)"
