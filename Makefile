.PHONY: lint format test run

lint:
	ruff app/

format:
	black app/

test:
	pytest

run:
	uvicorn app.main:app --reload 