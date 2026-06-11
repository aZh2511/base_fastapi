requirements:
	- uv lock

install-requirements:
	- uv sync

dev:
	- rm -rf .venv
	- uv venv --python 3.14
	- uv sync

prod:
	- rm -rf .venv
	- uv venv --python 3.14
	- uv sync --no-dev

pre-commit:
	- pre-commit install

ruff:
	- ruff check --fix

tests:
	- coverage run -m pytest -v -s

run:
	- uv run uvicorn --app-dir src presentation.http.main:app --reload

db-up:
	- docker compose up -d postgres

db-down:
	- docker compose down

migrate-up:
	- uv run alembic upgrade head

migrate-down:
	- uv run alembic downgrade -1

migrate-new:
	- uv run alembic revision -m "$(m)"
