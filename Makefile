.PHONY: up down build logs shell-backend shell-frontend migrate migrate-create seed test-backend test-frontend test-all lint format restart db-shell

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

migrate:
	docker-compose exec backend alembic upgrade head

migrate-create:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

seed:
	docker-compose exec backend python -m app.seeds.run_seeds

test-backend:
	docker-compose exec backend pytest --cov=app --cov-report=term-missing -v

test-frontend:
	docker-compose exec frontend npm test -- --coverage

test-all: test-backend test-frontend

lint:
	docker-compose exec backend ruff check app/
	docker-compose exec frontend npm run lint

format:
	docker-compose exec backend ruff format app/
	docker-compose exec frontend npm run format

restart:
	docker-compose restart backend celery_worker celery_beat

db-shell:
	docker-compose exec db psql -U greenos -d greenos
