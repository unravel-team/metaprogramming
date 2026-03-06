HOME := $(shell echo $$HOME)
HERE := $(shell echo $$PWD)
PROJECT_PACKAGE := python_scaffold

SHELL = /bin/bash -Eeuo pipefail
.DEFAULT_GOAL := help

.PHONY: help
help: ## List the supported scaffold commands
	@awk '/^[a-zA-Z0-9_.-]+:.*##/ { \
		printf "%-25s # %s\n", \
		substr($$1, 1, length($$1)-1), \
		substr($$0, index($$0,"##")+3) \
	}' $(MAKEFILE_LIST)

.env: .env.sample
	@if [ ! -f .env ]; then \
		cp .env.sample .env; \
		echo "Created .env from .env.sample"; \
	fi

.PHONY: doctor
doctor: ## Verify toolchain prerequisites and platform assumptions
	@command -v python3 >/dev/null 2>&1 || { echo "python3 is required"; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo "uv is required"; exit 1; }
	@command -v tagref >/dev/null 2>&1 || { echo "tagref is required"; exit 1; }
	@echo "Python scaffold is ready."

.PHONY: init
init: doctor .env ## Bootstrap dependencies and one-time setup
	uv sync --locked

.PHONY: venv
venv: init ## Alias for init

.PHONY: install-ruff
install-ruff: init ## Alias for init

.PHONY: install-pytest
install-pytest: init ## Alias for init

.PHONY: install-ty
install-ty: init ## Alias for init

.PHONY: install-basedpyright
install-basedpyright: init ## Alias for init

.PHONY: install-bandit
install-bandit: init ## Alias for init

.PHONY: install-dev-tools
install-dev-tools: init ## Alias for init

.PHONY: check-tagref
check-tagref:
	tagref

.PHONY: check-uv
check-uv:
	uv lock --check

.PHONY: check-ruff
check-ruff:
	uv run ruff check src tests

.PHONY: check-ty
check-ty:
	uv run ty check src tests

.PHONY: check-basedpyright
check-basedpyright:
	uv run basedpyright src tests

.PHONY: check-bandit
check-bandit:
	uv run bandit -q -ii -lll -c .bandit.yml -r src/$(PROJECT_PACKAGE)

.PHONY: check
check: check-uv check-ruff check-tagref check-ty check-bandit check-basedpyright ## Run linting, typing, security, and docs validation
	@echo "All checks passed!"

.PHONY: format
format: ## Apply Ruff formatting
	uv run ruff check --fix src tests
	uv run ruff format src tests

.PHONY: test
test: ## Run the default test suite
	uv run pytest -m "unit"

.PHONY: test-llm
test-llm: ## Run only the llm tests
	uv run pytest -m "llm"

.PHONY: test-integration
test-integration: ## Run only the integration tests
	uv run pytest -m "integration"

.PHONY: build
build: ## Produce the default build artifact
	uv build

.PHONY: upgrade-libs
upgrade-libs: ## Upgrade scaffold dependencies
	uv lock --upgrade
	uv sync

.PHONY: clean
clean: ## Remove generated artifacts
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	rm -rf .venv build dist *.egg-info
