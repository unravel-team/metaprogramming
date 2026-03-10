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

.gitignore:
	@echo "Download the .gitignore file from the [[https://github.com/unravel-team/metats][metats]] project"

.PHONY: install-dev-tools
install-dev-tools: install-sveltekit install-vitest install-biome install-svelte-check .gitignore    ## Install all development tools (SvelteKit, Vitest, Biome, svelte-check)

.PHONY: upgrade-libs
upgrade-libs:    ## Upgrade all dependencies to their latest versions
	bun update
	bun audit fix

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

.PHONY: check
check: check-biome check-typescript check-tagref    ## Check that the code is well linted, well typed, well documented
	@echo "All checks passed!"

.PHONY: format
format:    ## Format code with Biome
	@if [ -d "$(BIOME_SCOPE)" ]; then \
		bunx @biomejs/biome check --write $(BIOME_SCOPE); \
	else \
		echo "No $(BIOME_SCOPE) directory found; skipping Biome format"; \
	fi

.PHONY: test
test:    ## Run all the tests for the code
	bun test

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

.PHONY: docker-compose-build
docker-compose-build:   ## Build all the local infra (docker-compose)
	docker compose build

.PHONY: up
up:     ## Bring up all the local infra (docker-compose)
	docker compose up

.PHONY: down
down:       ## Bring down all the local infra (docker-compose)
	docker compose down -v

.PHONY: logs
logs:      ## Show all the logs (docker-compose)
	docker compose logs

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
