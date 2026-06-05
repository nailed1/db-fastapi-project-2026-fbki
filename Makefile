.PHONY: install dev test lint fmt docs docker-up docker-down migrate seed clean \
	db-test-create migrate-test test-db-setup setup-passwords

# ── Setup ──────────────────────────────────────────────────────────────────────
install:
	poetry install

# ── Development ────────────────────────────────────────────────────────────────
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ── Quality ────────────────────────────────────────────────────────────────────
# Same DATABASE_URL as CI (Postgres hotel_test + migrations applied).
TEST_DATABASE_URL ?= postgresql+asyncpg://hotel_user:hotel_pass@localhost:5432/hotel_test

test:
	DATABASE_URL=$(TEST_DATABASE_URL) poetry run pytest

test-unit:
	poetry run pytest tests/unit -v

test-integration:
	DATABASE_URL=$(TEST_DATABASE_URL) poetry run pytest tests/integration -v

lint:
	poetry run ruff check .
	poetry run mypy app

fmt:
	poetry run ruff format .
	poetry run ruff check --fix .

# ── Documentation ──────────────────────────────────────────────────────────────
docs:
	cd docs && poetry run sphinx-build -b html . _build/html
	@echo "Docs built at docs/_build/html/index.html"

docs-clean:
	rm -rf docs/_build

# ── Docker ─────────────────────────────────────────────────────────────────────
COMPOSE := docker compose -f docker/docker-compose.yml

docker-up:
	$(COMPOSE) up -d

docker-down:
	$(COMPOSE) down

docker-build:
	$(COMPOSE) build

docker-logs:
	$(COMPOSE) logs -f app

# ── Database ───────────────────────────────────────────────────────────────────
migrate:
	poetry run python -m app.db.migrate

# Заменить placeholder-хеши staff на bcrypt (как docker/entrypoint.sh)
setup-passwords:
	poetry run python -m app.db.setup_passwords

# Тестовая БД hotel_test (как в CI). docker-up поднимает только hotel_db.
db-test-create:
	-$(COMPOSE) exec -T db psql -U hotel_user -d hotel_db -c "CREATE DATABASE hotel_test;"

migrate-test:
	DATABASE_URL=$(TEST_DATABASE_URL) poetry run python -m app.db.migrate

test-db-setup: db-test-create migrate-test
	@echo "hotel_test ready — run: make test-integration"

seed:
	poetry run python -m app.db.seed

# ── Library ────────────────────────────────────────────────────────────────────
lib-build:
	cd packages/hotel_utils && poetry build

lib-publish-test:
	cd packages/hotel_utils && poetry publish -r testpypi

# ── Misc ───────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist
