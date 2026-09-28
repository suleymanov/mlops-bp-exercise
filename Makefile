format:
	ruff format .

lint:
	ruff check .

test:
	pytest unit_tests

check: lint format test
