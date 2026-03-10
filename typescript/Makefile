HOME := $(shell echo $$HOME)
HERE := $(shell echo $$PWD)

BIOME_SCOPE ?= src/

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

.PHONY: doctor
doctor: ## Verify toolchain prerequisites
	@for cmd in bun node tagref dbmate dafny; do \
		command -v $$cmd >/dev/null 2>&1 || { echo "$$cmd is required"; exit 1; }; \
	done
	@echo "TypeScript scaffold ready."

.PHONY: init
init: install-sveltekit install-vitest install-biome install-svelte-check install-dbmate install-dafny install-hooks .gitignore    ## Bootstrap dependencies and setup

.PHONY: ci
ci:
	bun ci

node_modules:
	bun install

.PHONY: install
install: node_modules    ## Install dependencies and create node_modules

package.json:
	@if [ ! -f package.json ]; then \
		echo "Creating package.json..."; \
		bun init -y; \
		echo "Please configure your package.json manually"; \
	fi

.PHONY: install-sveltekit
install-sveltekit: package.json    ## Install SvelteKit dependencies (does not scaffold a project)
	@echo "Installing SvelteKit dependencies (requires an existing SvelteKit project scaffold)..."
	bun install --save-dev @sveltejs/kit @sveltejs/adapter-auto @sveltejs/vite-plugin-svelte svelte vite
	@node -e "const pkg=require('./package.json'); process.exit(pkg.scripts && pkg.scripts.dev ? 0 : 1)" >/dev/null 2>&1 || bun pkg set scripts.dev="vite dev"
	@node -e "const pkg=require('./package.json'); process.exit(pkg.scripts && pkg.scripts.build ? 0 : 1)" >/dev/null 2>&1 || bun pkg set scripts.build="vite build"
	@node -e "const pkg=require('./package.json'); process.exit(pkg.scripts && pkg.scripts.preview ? 0 : 1)" >/dev/null 2>&1 || bun pkg set scripts.preview="vite preview"

.PHONY: install-biome
install-biome: package.json
	bun install --save-dev @biomejs/biome
	@if [ ! -f biome.json ]; then \
		bunx @biomejs/biome init; \
	fi

.PHONY: install-vitest
install-vitest: package.json
	bun install --save-dev vitest
	@if ! bun pkg get scripts.test >/dev/null 2>&1; then bun pkg set scripts.test="vitest run"; fi
	@if ! bun pkg get scripts.test:watch >/dev/null 2>&1; then bun pkg set scripts.test:watch="vitest"; fi
	@if ! bun pkg get scripts.test:coverage >/dev/null 2>&1; then bun pkg set scripts.test:coverage="vitest run --coverage"; fi

.PHONY: install-svelte-check
install-svelte-check: package.json
	bun install --save-dev svelte-check typescript

.PHONY: install-dbmate
install-dbmate:
	@if command -v brew >/dev/null 2>&1; then \
		brew install dbmate; \
	elif command -v curl >/dev/null 2>&1; then \
		curl -fsSL https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64.tar.gz | tar -xz && sudo mv dbmate /usr/local/bin/; \
	else \
		echo "Please install dbmate manually from https://github.com/amacneil/dbmate"; \
		exit 1; \
	fi

.PHONY: install-dafny
install-dafny:
	@if command -v brew >/dev/null 2>&1; then \
		brew install dafny; \
	elif [ "$$(uname)" = "Linux" ]; then \
		echo "Installing Dafny via snap..."; \
		snap install dafny --classic; \
	else \
		echo "Please install Dafny manually from https://github.com/dafny-lang/dafny/releases"; \
		exit 1; \
	fi

.git/hooks/pre-push:
	@echo "Setting up Git hooks..."
	@cat > .git/hooks/pre-push << 'EOF'
#!/bin/sh

# Redirect output to stderr for visibility
exec 1>&2

echo "Running pre-push checks..."

echo "Running make check (lints/static analysis)"

if ! make check; then
	echo "❌ make check failed. Aborting push."
	echo "   Fix the issues and try again."
	exit 1
fi

echo "Running make format (auto-formatting)"
if ! make format; then
	echo "❌ make format failed. Aborting push."
	exit 1
fi

echo "Checking for uncommitted changes after formatting"
if ! git diff --exit-code --quiet; then
	echo "⚠️  Code was reformatted by 'make format'!"
	echo "   Please commit these changes before pushing."
	exit 1
fi

echo "Running make test (unit tests)"
if ! make test; then
	echo "❌ make test failed. Aborting push."
	echo "   Fix the test failures and try again."
	exit 1
fi

echo "✅ All checks passed. Pushing changes..."
exit 0
EOF
	@chmod +x .git/hooks/pre-push
	@echo "✅ Git hooks installed successfully!"

.PHONY: install-hooks
install-hooks: .git/hooks/pre-push

.gitignore:
	@echo "Download the .gitignore file from the [[https://github.com/unravel-team/metats][metats]] project"

.PHONY: upgrade-deps
upgrade-deps:    ## Upgrade all dependencies to their latest versions
	bun update
	bun audit fix

.PHONY: upgrade-libs
upgrade-libs: upgrade-deps    ## Alias for upgrade-deps (deprecated)

.PHONY: check-tagref
check-tagref:
	@if ! command -v tagref >/dev/null 2>&1; then \
		echo "tagref executable not found. Please install it from https://github.com/stepchowfun/tagref/releases/"; \
		exit 1; \
	fi
	tagref

.PHONY: check-biome
check-biome:
	bunx @biomejs/biome check $(BIOME_SCOPE)

.PHONY: check-typescript
check-typescript:
	@if [ -f svelte.config.js ] || [ -f svelte.config.ts ]; then \
		bunx svelte-check --tsconfig ./tsconfig.json; \
	else \
		bunx tsc --noEmit; \
	fi

.PHONY: check-dafny
check-dafny:
	@if [ -d "contracts" ] && [ -n "$$(find contracts -name '*.dfy' 2>/dev/null)" ]; then \
		dafny verify contracts/*.dfy; \
	else \
		echo "No Dafny contracts found in contracts/*.dfy, skipping..."; \
	fi

.PHONY: check
check: check-biome check-typescript check-tagref check-dafny    ## Check that the code is well linted, well typed, well documented
	@echo "All checks passed!"

.PHONY: format
format:    ## Format code with Biome
	@if [ -d "$(BIOME_SCOPE)" ]; then \
		bunx @biomejs/biome check --write $(BIOME_SCOPE); \
	else \
		echo "No $(BIOME_SCOPE) directory found; skipping Biome format"; \
	fi

.PHONY: test-unit
test-unit:    ## Run unit tests
	bun test --config vitest.config.unit.ts

.PHONY: test-llm
test-llm:    ## Run LLM-specific tests
	bun test --config vitest.config.llm.ts

.PHONY: test-integration
test-integration:    ## Run integration tests
	bun test --config vitest.config.integration.ts

.PHONY: test
test: test-unit    ## Run unit tests (alias for test-unit)

.PHONY: test-watch
test-watch:    ## Run tests in watch mode
	bun run test:watch

.PHONY: test-coverage
test-coverage:    ## Run tests with coverage report
	bun run test:coverage

.PHONY: dev
dev:    ## Run the SvelteKit development server
	bun run dev

.PHONY: build
build: check    ## Build the SvelteKit application for production
	bun run build

.PHONY: preview
preview:    ## Preview the production build locally
	bun run preview

.PHONY: infra-build
infra-build:   ## Build all the local infra (docker-compose)
	docker compose build

.PHONY: infra-up
infra-up:     ## Bring up all the local infra (docker-compose)
	docker compose up

.PHONY: infra-down
infra-down:       ## Bring down all the local infra (docker-compose)
	docker compose down

.PHONY: infra-logs
infra-logs:      ## Show all the logs (docker-compose)
	docker compose logs

.PHONY: down
down: infra-down       ## Alias for infra-down (deprecated)

.PHONY: up
up: infra-up     ## Alias for infra-up (deprecated)

.PHONY: logs
logs: infra-logs      ## Alias for infra-logs (deprecated)

.PHONY: migrate
migrate: install-dbmate    ## Run database migrations (using dbmate)
	dbmate up

.PHONY: migrate-create
migrate-create: install-dbmate    ## Create a new database migration
	@read -p "Enter migration name: " name; \
	dbmate new $$name

.PHONY: migrate-rollback
migrate-rollback: install-dbmate    ## Rollback the last database migration
	dbmate rollback

.PHONY: deploy
deploy: build    ## Deploy the current code to production
	@echo "Run deployment commands here (Vercel, Netlify, etc.)!"

.PHONY: clean-cache
clean-cache:    ## Clean bun cache and SvelteKit/Vite caches
	bun cache clean --force
	rm -rf .svelte-kit
	rm -rf node_modules/.vite

.PHONY: clean
clean:     ## Delete any existing artifacts
	rm -rf node_modules/
	rm -rf .svelte-kit/
	rm -rf build/
	rm -rf dist/
	rm -rf coverage/
	rm -f *.tsbuildinfo
