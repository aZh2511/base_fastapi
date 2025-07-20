requirements:
	- uv lock

install-requirements:
	- uv sync

dev:
	- rm -rf .venv
	- uv venv --python 3.13 --dev
	- uv sync

prod:
	- rm -rf .venv
	- uv venv --python 3.13
	- uv sync --no-dev

pre-commit:
	- pre-commit install

ruff:
	- ruff check

tests:
	- coverage run -m pytest -v -s
