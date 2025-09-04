.PHONY: test unit integration e2e coverage

test:
	pytest -q

unit:
	pytest -q tests/unit

integration:
	pytest -q tests/integration

e2e:
	pytest -q tests/e2e

coverage:
	pytest --cov --cov-report=term-missing
