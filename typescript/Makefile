SHELL = /bin/bash -Eeuo pipefail
.DEFAULT_GOAL := help

.PHONY: help
help: ## List the supported scaffold commands
	@awk '/^[a-zA-Z0-9_.-]+:.*##/ { \
		printf "%-25s # %s\n", \
		substr($$1, 1, length($$1)-1), \
		substr($$0, index($$0,"##")+3) \
	}' $(MAKEFILE_LIST)

.PHONY: doctor
doctor: ## Verify toolchain prerequisites and platform assumptions
	@command -v bun >/dev/null 2>&1 || { echo "bun is required"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "node is required"; exit 1; }
	@command -v tagref >/dev/null 2>&1 || { echo "tagref is required"; exit 1; }
	@echo "TypeScript scaffold is ready."

.PHONY: init
init: doctor ## Bootstrap dependencies and one-time setup
	@if [ -f bun.lock ] || [ -f bun.lockb ]; then \
		bun install --frozen-lockfile; \
	else \
		bun install; \
	fi

.PHONY: install
install: init ## Alias for init

.PHONY: install-dev-tools
install-dev-tools: init ## Alias for init

.PHONY: check-tagref
check-tagref:
	tagref

.PHONY: check-biome
check-biome:
	bunx @biomejs/biome check src tests

.PHONY: check-typescript
check-typescript:
	bunx tsc --noEmit

.PHONY: check
check: check-biome check-typescript check-tagref ## Run linting, typing, and docs validation
	@echo "All checks passed!"

.PHONY: format
format: ## Apply Biome formatting
	bunx @biomejs/biome check --write src tests

.PHONY: test
test: ## Run the default test suite
	bun run test

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	bun run test:watch

.PHONY: test-coverage
test-coverage: ## Run tests with coverage
	bun run test:coverage

.PHONY: build
build: ## Produce the default build artifact
	bun run build

.PHONY: dev
dev: ## Run the starter project in watch mode
	bun run dev

.PHONY: upgrade-libs
upgrade-libs: ## Upgrade scaffold dependencies
	bun update

.PHONY: clean
clean: ## Remove generated artifacts
	rm -rf coverage dist node_modules
