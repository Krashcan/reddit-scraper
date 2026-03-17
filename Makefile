.PHONY: test lint format check hooks

test:
	.venv/bin/python -m pytest tests/ -v

lint:
	.venv/bin/ruff check .

format:
	.venv/bin/black .

check: format lint test

hooks:
	@echo '#!/bin/sh' > .git/hooks/pre-commit
	@echo 'make check' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "pre-commit hook installed"
