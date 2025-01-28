install:
	poetry install
start:
	docker compose up

test:
	poetry run pytest

checks:
	poetry run ruff check .
	poetry run mypy .
fixes:
	poetry run ruff format .
	poetry run ruff check . --fix-only
