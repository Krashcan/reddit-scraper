.PHONY: test test-e2e lint format check hooks

test:
	uv run pytest tests/ -v

test-e2e:
	uv run pytest -m e2e -v --override-ini="addopts="

lint:
	uv run ruff check .

format:
	uv run black .

check: format lint test

hooks:
	@echo '#!/bin/sh' > .git/hooks/pre-commit
	@echo 'make check' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "pre-commit hook installed"
