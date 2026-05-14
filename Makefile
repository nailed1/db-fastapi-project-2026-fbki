.PHONY: install dev test lint fmt docs docker-up docker-down migrate seed clean

# ── Setup ──────────────────────────────────────────────────────────────────────
install:
	poetry install

# ── Development ────────────────────────────────────────────────────────────────
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ── Quality ────────────────────────────────────────────────────────────────────
test:
	poetry run pytest

test-unit:
	poetry run pytest tests/unit -v

test-integration:
	poetry run pytest tests/integration -v

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
docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down

docker-build:
	docker compose -f docker/docker-compose.yml build

docker-logs:
	docker compose -f docker/docker-compose.yml logs -f app

# ── Database ───────────────────────────────────────────────────────────────────
migrate:
	poetry run python -m app.db.migrate

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
