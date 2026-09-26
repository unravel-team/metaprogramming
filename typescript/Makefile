SHELL := /bin/bash
.SHELLFLAGS := -Eeu -o pipefail -c
.DEFAULT_GOAL := help

# Keep the dependency store local; installed packages are not cache-cleanup targets.
PNPM := corepack pnpm --store-dir "$(CURDIR)/.cache/pnpm/store"
PLACEHOLDER_APP := replace-with-your-fly-app-name
PLACEHOLDER_PACKAGE := typescript-scaffold
VERSION_SCRIPT := scripts/release.mjs

.PHONY: help doctor init check check-format check-deps audit-deps format test test-unit test-property test-integration test-llm test-all test-coverage build ci dev clean clean-cache infra-build infra-up infra-down infra-logs infra-down-clean migrate migrate-create deploy deploy-npm version major minor patch release upgrade-deps check-lint check-types check-knip check-jscpd check-tagref

help: ## Show scaffold workflow targets
	@awk '/^[a-zA-Z0-9_-]+:.*##/ { printf "%-20s %s\n", substr($$1, 1, length($$1)-1), substr($$0, index($$0, "##") + 3) }' $(MAKEFILE_LIST)

doctor: ## Diagnose host prerequisites and project-local tools
	@for command in node corepack docker flyctl tagref; do \
		if command -v $$command >/dev/null 2>&1; then echo "$$command: found"; else echo "$$command: missing"; fi; \
	done
	@$(PNPM) --version
	@for tool in next vitest tsc dbmate; do \
		if [ -x "node_modules/.bin/$$tool" ]; then echo "$$tool: installed"; else echo "$$tool: run make init"; fi; \
	done

init: ## Copy .env when absent and install locked pnpm dependencies
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example."; else echo ".env exists; not replacing it."; fi
	@$(PNPM) install --frozen-lockfile

check-deps: ## Verify package manifest matches frozen lock without installing
	@$(PNPM) install --frozen-lockfile --lockfile-only

check-format: ## Check Biome formatting without rewriting files
	@$(PNPM) exec biome format src tests scripts *.config.ts package.json tsconfig*.json next-env.d.ts

check-lint: ## Lint source and test files with Biome
	@$(PNPM) exec biome lint src tests scripts *.config.ts

check-types: ## Type-check Next application, library, and tests without emitting
	@$(PNPM) exec tsc --noEmit -p tsconfig.json

check-knip: ## Find unused files, exports, and dependencies
	@$(PNPM) exec knip

check-jscpd: ## Detect duplicate code in source and tests
	@$(PNPM) exec jscpd src tests --config .jscpd.json

check-tagref: ## Validate documented source references
	@tagref

check: check-deps check-format check-lint check-types check-knip check-jscpd check-tagref ## Run offline quality checks

audit-deps: ## Query npm advisories; requires network and fails on findings
	@$(PNPM) audit --audit-level=low

format: ## Apply Biome formatting and safe lint fixes
	@$(PNPM) exec biome check --write src tests scripts *.config.ts package.json tsconfig*.json next-env.d.ts

test-unit: ## Run unit tests, excluding property, integration, and LLM files
	@$(PNPM) exec vitest run --config vitest.unit.config.ts

test-property: ## Run fast-check property tests, excluding external selectors
	@$(PNPM) exec vitest run --config vitest.property.config.ts

test-integration: ## Run integration tests; empty selector succeeds by declared policy
	@$(PNPM) exec vitest run --config vitest.integration.config.ts

test-llm: ## Run LLM tests; empty selector succeeds by declared policy
	@$(PNPM) exec vitest run --config vitest.llm.config.ts

test: test-unit test-property ## Run default unit and property suites

test-all: ## Run complete Vitest suite, including integration and LLM tests
	@$(PNPM) exec vitest run --config vitest.config.ts

test-coverage: ## Write V8 terminal, LCOV, and HTML coverage for default suites
	@$(PNPM) exec vitest run --coverage --config vitest.default.config.ts

build: check test ## Validate gates, then build Next app and separate library artifacts
	@$(PNPM) run build

ci: check test audit-deps ## Run offline checks, default tests, and network audit

dev: ## Run Next development server on http://127.0.0.1:3000
	@$(PNPM) run dev

clean: ## Remove local build, coverage, and library artifacts
	@rm -rf .next dist coverage

clean-cache: ## Remove only project-owned pnpm, Next, and tool caches
	@for cache in .cache/pnpm/store .next/cache node_modules/.cache coverage/.tmp; do \
		path="$$cache"; while :; do \
			[ ! -L "$$path" ] || { echo "Refusing symlink cache path: $$path"; exit 2; }; \
			case "$$path" in */*) path="$${path%/*}" ;; *) break ;; esac; \
		done; \
	done; \
	rm -rf -- .cache/pnpm/store .next/cache node_modules/.cache coverage/.tmp

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

migrate: ## Apply dbmate migrations using DATABASE_URL
	@$(PNPM) exec dbmate --migrations-dir db/migrations up

migrate-create: ## Create migration; use MESSAGE='describe change'
	@test -n "$(MESSAGE)" || { echo "MESSAGE is required, e.g. make migrate-create MESSAGE='add widgets'"; exit 2; }
	@$(PNPM) exec dbmate --migrations-dir db/migrations new "$(MESSAGE)"

deploy: ## Deploy to Fly only after app identity is customized
	@app_name=$$(awk -F '"' '/^app = / { print $$2; exit }' fly.toml); \
	if [ -z "$$app_name" ] || [ "$$app_name" = "$(PLACEHOLDER_APP)" ]; then echo "Set a unique app name in fly.toml before deploy."; exit 2; fi
	@$(MAKE) --no-print-directory build
	@flyctl deploy --config fly.toml

deploy-npm: ## Publish only clean standalone current-version release artifacts
	@root=$$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Publishing requires standalone Git repository."; exit 2; }; \
	[ "$$root" = "$$(pwd -P)" ] || { echo "Publishing must run from standalone project root."; exit 2; }; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Publishing requires clean committed state."; exit 2; fi; \
	package_name=$$(node -p 'require("./package.json").name'); \
	if [ "$$package_name" = "$(PLACEHOLDER_PACKAGE)" ]; then echo "Set a unique package name before publishing."; exit 2; fi; \
	if [ -z "$${NPM_TOKEN:-}" ]; then echo "NPM_TOKEN is required."; exit 2; fi; \
	version=$$(node $(VERSION_SCRIPT) version); tag="v$$version"; \
	git rev-parse --verify --quiet "$$tag^{tag}" >/dev/null && [ "$$(git rev-parse "$$tag^{commit}")" = "$$(git rev-parse HEAD)" ] || { echo "Annotated $$tag must identify current HEAD."; exit 2; }
	@$(MAKE) --no-print-directory build
	@if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Build changed release state."; exit 2; fi
	@npmrc=$$(mktemp); trap 'rm -f "$$npmrc"' EXIT; chmod 600 "$$npmrc"; \
	printf '//registry.npmjs.org/:_authToken=%s\n' "$$NPM_TOKEN" > "$$npmrc"; \
	NPM_CONFIG_USERCONFIG="$$npmrc" $(PNPM) --dir dist publish --access public --no-git-checks

version: ## Print semantic package version
	@node $(VERSION_SCRIPT) version

major: ## Bump major version metadata only
	@node $(VERSION_SCRIPT) major

minor: ## Bump minor version metadata only
	@node $(VERSION_SCRIPT) minor

patch: ## Bump patch version metadata only
	@node $(VERSION_SCRIPT) patch

release: ## Validate then tag clean standalone HEAD with local annotated version
	@root=$$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Release requires standalone Git repository."; exit 2; }; \
	[ "$$root" = "$$(pwd -P)" ] || { echo "Release must run from standalone project root."; exit 2; }; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Release requires clean committed state."; exit 2; fi
	@$(MAKE) --no-print-directory build
	@if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Build changed release state."; exit 2; fi
	@version=$$(node $(VERSION_SCRIPT) version); tag="v$$version"; \
	if git rev-parse --verify --quiet "refs/tags/$$tag" >/dev/null; then echo "$$tag already exists."; exit 2; fi; \
	git tag --annotate "$$tag" --message "Release $$tag"

upgrade-deps: ## Deliberately update package constraints and pnpm lockfile
	@$(PNPM) update --latest
	@$(PNPM) install
