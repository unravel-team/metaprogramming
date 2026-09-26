SHELL := /bin/bash
.SHELLFLAGS := -Eeu -o pipefail -c
.DEFAULT_GOAL := help

# Keep setup and normal commands on the same project-owned cache.
export UV_CACHE_DIR
override UV_CACHE_DIR := $(CURDIR)/.cache/uv
UV_RUN := uv run --no-sync
VERSION_SCRIPT := scripts/release.py
PLACEHOLDER_APP := replace-with-your-fly-app-name
PLACEHOLDER_PACKAGE := python-scaffold

.PHONY: help doctor init check check-format check-deps audit-deps format test test-unit test-property test-integration test-llm test-all test-coverage build ci dev clean clean-cache infra-build infra-up infra-down infra-logs infra-down-clean migrate migrate-create deploy deploy-pypi version major minor patch release upgrade-deps

help: ## Show scaffold workflow targets
	@awk '/^[a-zA-Z0-9_-]+:.*##/ { printf "%-20s %s\n", substr($$1, 1, length($$1)-1), substr($$0, index($$0, "##") + 3) }' $(MAKEFILE_LIST)

doctor: ## Diagnose host prerequisites and synced project tools
	@for command in uv docker flyctl tagref; do \
		if command -v $$command >/dev/null 2>&1; then \
			echo "$$command: found"; \
		else \
			echo "$$command: missing"; \
		fi; \
	done
	@status=0; for command in python ruff pytest basedpyright ty bandit; do \
		if $(UV_RUN) $$command --version >/dev/null 2>&1; then \
			echo "$$command: found"; \
		else \
			echo "$$command: missing or project is not initialized"; status=1; \
		fi; \
	done; exit $$status

init: ## Create .env when absent and install locked dependencies
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example."; else echo ".env exists; not replacing it."; fi
	@uv sync --locked

check-deps: ## Verify dependency metadata matches UV lock
	@uv lock --check

check-format: ## Check Ruff formatting without rewriting files
	@$(UV_RUN) ruff format --check src tests scripts alembic migrations

check-ruff: ## Lint source, tests, release helper, and Alembic files
	@$(UV_RUN) ruff check src tests scripts alembic migrations

check-ty: ## Run Ty type checks on shipped source and tests
	@$(UV_RUN) ty check src tests

check-basedpyright: ## Run BasedPyright using the source scope in pyproject.toml
	@$(UV_RUN) basedpyright

check-bandit: ## Scan application source for common security issues
	@$(UV_RUN) bandit -q -ii -lll -c .bandit.yml -r src

check-tagref: ## Verify documented source references
	@tagref

check: check-deps check-format check-ruff check-ty check-basedpyright check-bandit check-tagref ## Run offline quality checks

audit-deps: ## Query package advisories; requires network access
	@$(UV_RUN) pip-audit

format: ## Apply Ruff lint fixes and formatting
	@$(UV_RUN) ruff check --fix src tests scripts alembic migrations
	@$(UV_RUN) ruff format src tests scripts alembic migrations

test-unit: ## Run unit tests; exclude property, integration, and LLM selectors
	@$(UV_RUN) pytest -m "unit and not property and not integration and not llm"

test-property: ## Run Hypothesis property tests; exclude external selectors
	@$(UV_RUN) pytest -m "property and not integration and not llm"

test-integration: ## Run integration selector; empty suite is declared skipped
	@set +e; $(UV_RUN) pytest -m "integration"; status=$$?; set -e; \
	if [ $$status -eq 5 ]; then echo "No integration tests selected; skipped by scaffold policy."; exit 0; fi; \
	exit $$status

test-llm: ## Run LLM selector; empty suite is declared skipped
	@set +e; $(UV_RUN) pytest -m "llm"; status=$$?; set -e; \
	if [ $$status -eq 5 ]; then echo "No LLM tests selected; skipped by scaffold policy."; exit 0; fi; \
	exit $$status

test: test-unit test-property ## Run default unit and property test suites

test-all: ## Run complete pytest suite, including integration and LLM tests
	@$(UV_RUN) pytest

test-coverage: ## Write terminal, XML, and HTML coverage for default suites
	@$(UV_RUN) pytest -m "(unit or property) and not integration and not llm" --cov=python_scaffold --cov-report=term-missing --cov-report=xml:coverage.xml --cov-report=html:coverage

build: check test ## Validate then build wheel and source distribution
	@uv build

ci: check test audit-deps ## Run quality checks, default tests, and network audit

dev: ## Run FastAPI with reload on http://127.0.0.1:8000
	@$(UV_RUN) uvicorn python_scaffold.api:app --host 0.0.0.0 --port 8000 --reload

infra-build: ## Build local Docker Compose services
	@docker compose build

infra-up: ## Start local PostgreSQL with named data volume
	@docker compose up -d

infra-down: ## Stop local Docker Compose services
	@docker compose down

infra-logs: ## Follow local Docker Compose service logs
	@docker compose logs -f

infra-down-clean: ## Prompt, then remove local services and volumes only for yes
	@echo "Warning: removing volumes permanently deletes local PostgreSQL data."
	@read -r -p "Type yes to remove volumes: " confirm || confirm=""; \
	if [ "$$confirm" = "yes" ]; then docker compose down --volumes; else echo "Aborted; volumes preserved."; fi

migrate: ## Apply Alembic migrations using .env DATABASE_URL or exported override
	@$(UV_RUN) --env-file .env alembic upgrade head

migrate-create: ## Create Alembic revision; use MESSAGE='describe change'
	@test -n "$(MESSAGE)" || { echo "MESSAGE is required, e.g. make migrate-create MESSAGE='add widgets'"; exit 2; }
	@$(UV_RUN) --env-file .env alembic revision --autogenerate -m "$(MESSAGE)"

deploy: build ## Deploy to Fly only after app identity is customized
	@app_name=$$(awk -F '"' '/^app = / { print $$2; exit }' fly.toml); \
	if [ -z "$$app_name" ] || [ "$$app_name" = "$(PLACEHOLDER_APP)" ]; then \
		echo "Set a unique app name in fly.toml before deploy."; exit 2; \
	fi; \
	flyctl deploy --config fly.toml

deploy-pypi: ## Build and publish current artifacts only from exact clean release tag
	@root=$$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Publishing requires standalone Git repository."; exit 2; }; \
	[ "$$root" = "$$(pwd -P)" ] || { echo "Publishing must run from standalone project root."; exit 2; }; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Publishing requires clean committed state."; exit 2; fi; \
	package_name=$$(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["name"])'); \
	package_identity=$$(python3 -c 'import re, sys; print(re.sub(r"[-_.]+", "-", sys.argv[1]).lower())' "$$package_name"); \
	version=$$(python3 $(VERSION_SCRIPT) version); \
	if [ "$$package_identity" = "$(PLACEHOLDER_PACKAGE)" ]; then echo "Set unique project.name before publishing."; exit 2; fi; \
	if [ -z "$${UV_PUBLISH_TOKEN:-}" ]; then echo "UV_PUBLISH_TOKEN is required."; exit 2; fi; \
	tag="v$$version"; git rev-parse --verify --quiet "$$tag^{tag}" >/dev/null && [ "$$(git rev-parse "$$tag^{commit}")" = "$$(git rev-parse HEAD)" ] || { echo "Annotated $$tag must identify current HEAD."; exit 2; }; \
	rm -rf dist; \
	$(MAKE) --no-print-directory build; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Build changed release state."; exit 2; fi; \
	distribution=$$(python3 -c 'import re, tomllib; name=tomllib.load(open("pyproject.toml", "rb"))["project"]["name"]; print(re.sub(r"[-_.]+", "-", name).lower().replace("-", "_"))'); \
	sdist="dist/$$distribution-$$version.tar.gz"; wheel="dist/$$distribution-$$version-py3-none-any.whl"; \
	test -f "$$sdist" && test -f "$$wheel" || { echo "Expected current-version distribution artifacts are missing."; exit 2; }; \
	uv publish "$$sdist" "$$wheel"

version: ## Print semantic package version
	@python3 $(VERSION_SCRIPT) version

major: ## Bump major version metadata only
	@python3 $(VERSION_SCRIPT) major

minor: ## Bump minor version metadata only
	@python3 $(VERSION_SCRIPT) minor

patch: ## Bump patch version metadata only
	@python3 $(VERSION_SCRIPT) patch

release: ## Validate then tag clean standalone HEAD with local annotated version
	@root=$$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Release requires standalone Git repository."; exit 2; }; \
	[ "$$root" = "$$(pwd -P)" ] || { echo "Release must run from standalone project root."; exit 2; }; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Release requires clean committed state."; exit 2; fi; \
	$(MAKE) --no-print-directory build; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Build changed release state."; exit 2; fi; \
	version=$$(python3 $(VERSION_SCRIPT) version); tag="v$$version"; \
	if git rev-parse --verify --quiet "refs/tags/$$tag" >/dev/null; then echo "$$tag already exists."; exit 2; fi; \
	git tag --annotate "$$tag" --message "Release $$tag"

upgrade-deps: ## Deliberately update dependency constraints and UV lock
	@uv lock --upgrade
	@uv sync

clean: ## Remove local build, coverage, and Python bytecode artifacts
	@rm -rf build dist coverage coverage.xml .coverage
	@find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@find . -type f -name '*.py[co]' -delete

clean-cache: ## Remove only project-owned UV, pytest, and Ruff caches
	@for cache in .cache/uv .pytest_cache .ruff_cache; do \
		path="$$cache"; while :; do \
			[ ! -L "$$path" ] || { echo "Refusing symlink cache path: $$path"; exit 2; }; \
			case "$$path" in */*) path="$${path%/*}" ;; *) break ;; esac; \
		done; \
	done; \
	rm -rf -- .cache/uv .pytest_cache .ruff_cache
