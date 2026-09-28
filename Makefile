format:
	ruff format .

lint:
	ruff check .

test:
	pytest

check: lint format test
