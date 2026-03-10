HOME := $(shell echo $$HOME)
HERE := $(shell echo $$PWD)

# Set bash instead of sh for the @if [[ conditions,
# and use the usual safety flags:
SHELL = /bin/bash -Eeu

.DEFAULT_GOAL := help

.PHONY: help
help:    ## A brief listing of all available commands
	@awk '/^[a-zA-Z0-9_-]+:.*##/ { \
		printf "%-25s # %s\n", \
		substr($$1, 1, length($$1)-1), \
		substr($$0, index($$0,"##")+3) \
	}' $(MAKEFILE_LIST)

.env.sample:
	touch .env.sample

.env: .env.sample    ## Copy .env.sample to .env if .env doesn't exist
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.sample..."; \
		cp .env.sample .env; \
		echo "✓ .env created. Please edit it with your actual values."; \
	else \
		echo ".env already exists, skipping..."; \
	fi

pyproject.toml:
	@if [ ! -f pyproject.toml ]; then \
		echo "Creating pyproject.toml..."; \
		echo '[build-system]' > pyproject.toml; \
		echo 'requires = ["hatchling"]' >> pyproject.toml; \
		echo 'build-backend = "hatchling.build"' >> pyproject.toml; \
		echo '' >> pyproject.toml; \
		echo '[project]' >> pyproject.toml; \
		echo 'name = "metapy"' >> pyproject.toml; \
		echo 'version = "0.1.0"' >> pyproject.toml; \
		echo 'description = ""' >> pyproject.toml; \
		echo 'authors = []' >> pyproject.toml; \
		echo 'keywords = []' >> pyproject.toml; \
		echo 'packages = [{include="src"}]' >> pyproject.toml; \
	    echo 'requires-python = ">=3.14.0"' >> pyproject.toml; \
		echo '' >> pyproject.toml; \
	fi

tests:
	mkdir tests

src:
	mkdir -p src/metapy && touch src/metapy/__init__.py

.venv: pyproject.toml tests src
	uv venv
	uv lock
	uv sync --locked --no-cache

.PHONY: venv
venv: .venv .env    ## Create the .venv and the .env files
	@echo "Virtual environment created at .venv/"

.PHONY: install-ruff
install-ruff: pyproject.toml
	uv add ruff --group dev
	@if ! grep -q "\[tool.ruff.lint\]" pyproject.toml; then \
		echo '' >> pyproject.toml; \
		echo '[tool.ruff.lint]' >> pyproject.toml; \
		echo 'select = [' >> pyproject.toml; \
		echo '    # pycodestyle' >> pyproject.toml; \
		echo '    "E",' >> pyproject.toml; \
		echo '    # Pyflakes' >> pyproject.toml; \
		echo '    "F",' >> pyproject.toml; \
		echo '    # pyupgrade' >> pyproject.toml; \
		echo '    "UP",' >> pyproject.toml; \
		echo '    # flake8-bugbear' >> pyproject.toml; \
		echo '    "B",' >> pyproject.toml; \
		echo '    # flake8-simplify' >> pyproject.toml; \
		echo '    "SIM",' >> pyproject.toml; \
		echo '    # isort' >> pyproject.toml; \
		echo '    "I",' >> pyproject.toml; \
		echo ']' >> pyproject.toml; \
		echo 'ignore = ["E501"]' >> pyproject.toml; \
	fi

.PHONY: install-pytest
install-pytest: pyproject.toml
	uv add pytest pytest-asyncio --group dev
	@if ! grep -q "\[tool.pytest.ini_options\]" pyproject.toml; then \
		echo '' >> pyproject.toml; \
		echo '[tool.pytest.ini_options]' >> pyproject.toml; \
		echo 'testpaths = ["tests"]' >> pyproject.toml; \
		echo 'addopts = "-v --tb=short"' >> pyproject.toml; \
		echo 'asyncio_mode = "auto"' >> pyproject.toml; \
		echo 'log_cli = true' >> pyproject.toml; \
		echo 'log_cli_level = "INFO"' >> pyproject.toml; \
		echo 'log_cli_format = "%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"' >> pyproject.toml; \
		echo 'asyncio_default_fixture_loop_scope = "function"' >> pyproject.toml; \
	fi

.PHONY: install-ty
install-ty:
	uv add ty --group dev

.PHONY: install-basedpyright
install-basedpyright: pyproject.toml
	uv add basedpyright --group dev
	@if ! grep -q "\[tool.basedpyright\]" pyproject.toml; then \
		echo '' >> pyproject.toml; \
		echo '[tool.basedpyright]' >> pyproject.toml; \
		echo 'reportAny = false' >> pyproject.toml; \
		echo 'reportExplicitAny = false' >> pyproject.toml; \
		echo 'reportUnknownMemberType = false' >> pyproject.toml; \
		echo 'reportUnknownArgumentType = false' >> pyproject.toml; \
		echo 'reportUnknownVariableType = false' >> pyproject.toml; \
		echo 'reportUnknownLambdaType = false' >> pyproject.toml; \
	fi

.PHONY: install-tagref
install-tagref:
	@if ! command -v tagref >/dev/null 2>&1; then \
		echo "tagref executable not found. Please install it from https://github.com/stepchowfun/tagref?tab=readme-ov-file#installation-instructions"; \
		exit 1; \
	fi

.PHONY: install-bandit
install-bandit:
	uv tool install bandit

.git/hooks/pre-push:
	@echo "Setting up Git hooks..."
	@cp dev_tools/hooks/pre-push .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "✅ Git hooks installed successfully!"
	@echo "The pre-push hook will run make check, make format, and make test before each push."

.PHONY: install-hooks
install-hooks: .git/hooks/pre-push

AGENTS.md:
	@echo "Download the CONVENTIONS.md file from the [[https://github.com/unravel-team/metapy][metapy]] project, then symlink it to AGENTS.md and CLAUDE.md"

.aider.conf.yml:
	@echo "Download the .aider.conf.yml file from the [[https://github.com/unravel-team/metapy][metapy]] project"

.gitignore:
	@echo "Download the .gitignore file from the [[https://github.com/unravel-team/metapy][metapy]] project"

.PHONY: install-dev-tools
install-dev-tools: install-ruff install-pytest install-ty  install-basedpyright install-tagref install-bandit install-hooks AGENTS.md .aider.conf.yml .gitignore    ## Install all development tools (Ruff, Pytest, Ty, Tagref, Bandit, Hooks)

.PHONY: check-bandit
check-bandit:
	bandit -q -ii -lll -c .bandit.yml -r src/

.PHONY: check-tagref
check-tagref: install-tagref
	tagref

.PHONY: check-uv
check-uv:
	uv lock --check

.PHONY: check-ruff
check-ruff:
	uv run ruff check -n src tests

.PHONY: check-ty
check-ty:
	uv run ty check src tests

.PHONY: check-basedpyright
check-basedpyright:
	uv run basedpyright src tests

.PHONY: check
check: check-uv check-ruff check-tagref check-ty check-bandit check-basedpyright    ## Check that the code is well linted, well typed, well documented. Fast checks first, slow later
	@echo "All checks passed!"

.PHONY: format
format:  ## Format the code using ruff
	uv run ruff check -n --fix
	uv run ruff format

.PHONY: megalinter
megalinter:
	docker run --rm -v "$(HERE):/tmp/lint" oxsecurity/megalinter:v8

.PHONY: test
test:    ## Run only the unit tests
	uv run pytest -m "unit"

.PHONY: test-llm
test-llm:    ## Run only the llm tests
	uv run pytest -m "llm"

.PHONY: test-integration
test-integration:    ## Run only the integration tests
	uv run pytest -m "integration"

.PHONY: build
build: check     ## Build the deployment artifact
	uv build

.PHONY: docker-build
docker-build:   ## Build the FastAPI server Dockerfile
	docker build -f Dockerfile -t metapy:latest -t metapy:$$(git rev-parse --short HEAD) .

.PHONY: docker-compose-build
docker-compose-build:  ## Build all the local infra (docker-compose)
	docker compose build

.PHONY: up
up:   ## Bring up all the local infra (docker-compose) and synthetic data
	docker compose up

.PHONY: logs
logs:
	docker compose logs

.PHONY: down
down:       ## Bring down all the local infra (docker-compose)
	docker compose down

.PHONY: down-clean
down-clean:  ## Bring down all the local infra and delete volumes
	@echo "Warning: Deleting volumes will lead to data loss. You will start from scratch and this may introduce bugs (e.g., if your code does not work with existing data in postgres)."
	@read -p "Are you sure you want to proceed? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker compose down -v; \
		echo "Volumes deleted."; \
	else \
		echo "Aborted."; \
	fi

.PHONY: migrate
migrate:    ## Run Alembic database migrations
	uv run python -m alembic upgrade head

.PHONY: server
server:    ## Run the FastAPI server locally
	ENABLE_TRACING=true uv run -m unravel.fastapi.main

.PHONY: backup-current-image
backup-current-image:
	@echo "Backing up currently running image..."
	@if [ -f .fly_image ]; then \
		mv .fly_image .fly_image.backup; \
		echo "✅ Backed up current .fly_image to .fly_image.backup"; \
	fi

.fly_image:
	@IMAGE=$$(flyctl image show --app metapy | awk 'NR>2 && NF>0 {print $$2"/"$$3":"$$4; exit}'); \
	echo "$$IMAGE" > .fly_image; \
	echo "✅ Current production image saved: $$IMAGE"

.PHONY: tag-deploy-internal
tag-deploy-internal: .fly_image
	@if [ -f .can_tag ]; then \
		TAG="fly-$$(date +%Y-%m-%d)"; \
		IMAGE=$$(cat .fly_image); \
		if git tag -m "$$(printf 'image: %s' "$$IMAGE")" "$$TAG" 2>/dev/null; then \
			echo "✅ Tagged current commit as $$TAG"; \
			rm .can_tag; \
		else \
			echo "⚠️  Tag $$TAG already exists, skipping tag creation"; \
			echo "Image: $$IMAGE"; \
		fi; \
	fi

.PHONY: deploy-internal
deploy-internal:
	@echo "Deploying to production..."
	@if flyctl deploy --config fly.toml; then \
		echo "✅ Deployment successful!"; \
	    touch .can_tag; \
	else \
		echo "❌ Deployment failed!"; \
		if [ -f .fly_image.backup ]; then \
			echo "Working image in: .fly_image.backup"; \
		fi; \
		exit 1; \
	fi

.PHONY: deploy
deploy: build backup-current-image deploy-internal tag-deploy-internal    ## Deploy with backup and auto-tagging

.PHONY: rollback
rollback:    ## Rollback to the previous version stored in backup
	@if [ ! -f .fly_image.backup ]; then \
		echo "❌ No backup image found (.fly_image.backup missing)"; \
		echo "Cannot rollback without a backup image."; \
		exit 1; \
	fi
	@BACKUP_IMAGE=$$(cat .fly_image.backup); \
	echo "Rolling back to: $$BACKUP_IMAGE"; \
	if flyctl deploy --config fly.toml --image "$$BACKUP_IMAGE"; then \
		if [ -f .fly_image ]; then \
			BAD_DEPLOY_IMAGE=$$(cat .fly_image); \
			echo "Overwriting bad deploy image: $$BAD_DEPLOY_IMAGE"; \
		fi; \
		mv .fly_image.backup .fly_image; \
		echo "✅ Rollback successful! Restored to: $$BACKUP_IMAGE"; \
	else \
		echo "❌ Rollback failed!"; \
		exit 1; \
	fi

.PHONY: deploy-build-only
deploy-build-only:
	flyctl deploy --config fly.toml --build-only
	@echo "✅ Build-only Deploy complete! Please update .fly_image manually!"

.PHONY: prepare
prepare: deploy-build-only backup-current-image    ## Build the latest code and upload image to fly.io. Useful in hot-swap and migration situations

.PHONY: deploy-reuse-image
deploy-reuse-image:	.fly_image    ## Deploy only config changes to production, reusing the latest image
	@echo "Deploying config-only changes..."
	@IMAGE=$$(cat .fly_image); \
	echo "Using current production image: $$IMAGE"; \
	if flyctl deploy --config fly.toml --image "$$IMAGE"; then \
		echo "✅ Config deployment successful!"; \
	else \
		echo "❌ Config deployment failed!"; \
		exit 1; \
	fi

.PHONY: upgrade-libs
upgrade-libs:    ## Upgrade all the deps to their latest versions
	uv sync --upgrade

.PHONY: clean-cache
clean-cache:    ## Clean UV Cache (only needed in extreme conditions)
	@echo "Cleaning cache! This removes all downloaded deps!"
	uv cache clean

.PHONY: clean
clean:     ## Delete any existing artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
