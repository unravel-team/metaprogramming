SHELL := /bin/bash
.SHELLFLAGS := -Eeu -o pipefail -c
.DEFAULT_GOAL := help

CLOJURE := clojure -Srepro
PLACEHOLDER_APP := replace-with-your-fly-app-name
PLACEHOLDER_LIB := clojure-scaffold
CLOJURE_SOURCES := $(shell find src app test scripts -type f -name '*.clj' -print) build.clj

.PHONY: help
help: ## Show scaffold workflow targets
	@awk '/^[a-zA-Z0-9_-]+:.*##/ { printf "%-20s %s\n", substr($$1, 1, length($$1)-1), substr($$0, index($$0, "##") + 3) }' $(MAKEFILE_LIST)

.PHONY: doctor
doctor: ## Diagnose host prerequisites and project aliases
	@for command in clojure docker flyctl tagref; do \
		if command -v $$command >/dev/null 2>&1; then echo "$$command: found"; else echo "$$command: missing"; fi; \
	done
	@$(CLOJURE) -Sdescribe
	@echo "zprint, Migratus, Clofidence, Polylith, and clj-watson resolve from pinned deps.edn aliases; run make init to prefetch them."

.PHONY: init
init: ## Copy .env when absent and prefetch pinned project dependencies
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example."; else echo ".env exists; not replacing it."; fi
	@$(CLOJURE) -P -M:test
	@$(CLOJURE) -P -M:zprint
	@$(CLOJURE) -P -M:clj-kondo
	@$(CLOJURE) -P -T:build jar
	@$(CLOJURE) -P -M:run
	@$(CLOJURE) -P -M:migratus
	@$(CLOJURE) -P -M:poly
	@$(CLOJURE) -P -M:enrich-repl
	@$(CLOJURE) -P -X:test:coverage
	@$(CLOJURE) -P -M:clj-watson
	@$(CLOJURE) -P -X:deploy-clojars
	@$(CLOJURE) -P -M:antq
	@$(CLOJURE) -P -M:sync-deps

.PHONY: check-deps
check-deps: ## Resolve base, test, run, and Migratus classpaths; Clojure CLI has no native lockfile
	@$(CLOJURE) -Spath >/dev/null
	@$(CLOJURE) -A:test -Spath >/dev/null
	@$(CLOJURE) -A:run -Spath >/dev/null
	@$(CLOJURE) -A:migratus -Spath >/dev/null

.PHONY: check-format
check-format: ## Check Clojure formatting with pinned zprint without rewriting files
	@$(CLOJURE) -M:zprint -c $(CLOJURE_SOURCES)

.PHONY: check-cljkondo
check-cljkondo: ## Lint source, tests, scripts, and build metadata with pinned clj-kondo
	@$(CLOJURE) -M:clj-kondo --config '{:config-paths ^:replace []}' --lint $(CLOJURE_SOURCES)

.PHONY: check-tagref
check-tagref: ## Validate documented cross-file references
	@tagref check

.PHONY: check
check: check-deps check-format check-cljkondo check-tagref ## Run reproducible dependency, format, lint, and reference checks

.PHONY: audit-deps
audit-deps: ## Scan base and :migratus advisories; network and CLJ_WATSON_NVD_API_KEY required
	@test -n "$${CLJ_WATSON_NVD_API_KEY:-}" || { echo "CLJ_WATSON_NVD_API_KEY is required for a reliable NVD scan."; exit 2; }
	@CLJ_WATSON_ANALYZER_OSSINDEX_ENABLED=false $(CLOJURE) -M:clj-watson scan -p deps.edn -a migratus --cvss-fail-threshold 0

.PHONY: format
format: ## Apply pinned zprint formatting to Clojure source and tests
	@$(CLOJURE) -M:zprint -w $(CLOJURE_SOURCES)

.PHONY: test-unit
test-unit: ## Run only ^:unit tests, excluding property, integration, and LLM metadata
	@$(CLOJURE) -M:test -i :unit -e :property -e :integration -e :llm

.PHONY: test-property
test-property: ## Run only ^:property tests, excluding integration and LLM metadata
	@$(CLOJURE) -M:test -i :property -e :integration -e :llm

.PHONY: test-integration
test-integration: ## Invoke ^:integration selector; empty selector succeeds by declared runner policy
	@$(CLOJURE) -M:test -i :integration

.PHONY: test-llm
test-llm: ## Invoke ^:llm selector; empty selector succeeds by declared runner policy
	@$(CLOJURE) -M:test -i :llm

.PHONY: test
test: test-unit test-property ## Run default unit and property test suites

.PHONY: test-all
test-all: ## Run complete Cognitect suite, including integration and LLM tests
	@$(CLOJURE) -M:test

.PHONY: test-coverage
test-coverage: ## Write Clofidence coverage for unit and property tests to coverage/
	@rm -rf coverage
	@$(CLOJURE) -X:test:coverage

.PHONY: build
build: check test ## Validate gates, then create library JAR without local Maven installation
	@$(CLOJURE) -T:build jar

.PHONY: ci
ci: check test audit-deps ## Run offline checks, default tests, and network vulnerability audit

.PHONY: dev
dev: ## Run JVM HTTP server on http://0.0.0.0:8080
	@$(CLOJURE) -M:run

.PHONY: clean
clean: ## Remove local JAR, class, coverage, and Migratus artifacts
	@rm -rf target coverage

.PHONY: clean-cache
clean-cache: ## Remove project-local CLI/linter caches; preserve global Maven cache
	@for cache in .cpcache .clj-kondo/.cache; do \
		path="$$cache"; while :; do \
			[ ! -L "$$path" ] || { echo "Refusing symlink cache path: $$path"; exit 2; }; \
			case "$$path" in */*) path="$${path%/*}" ;; *) break ;; esac; \
		done; \
	done; \
	rm -rf -- .cpcache .clj-kondo/.cache

.PHONY: infra-build
infra-build: ## Build local Docker Compose services
	@docker compose build

.PHONY: infra-up
infra-up: ## Start local PostgreSQL with named data volume
	@docker compose up -d

.PHONY: infra-down
infra-down: ## Stop local Docker Compose services
	@docker compose down

.PHONY: infra-logs
infra-logs: ## Follow local Docker Compose service logs
	@docker compose logs -f

.PHONY: infra-down-clean
infra-down-clean: ## Prompt, then remove local services and volumes only for exact yes
	@echo "Warning: removing volumes permanently deletes local PostgreSQL data."
	@read -r -p "Type yes to remove volumes: " confirm || confirm=""; \
	if [ "$$confirm" = "yes" ]; then docker compose down --volumes; else echo "Aborted; volumes preserved."; fi

.PHONY: migrate
migrate: ## Apply Migratus migrations using exported or plain .env DATABASE_URL
	@$(CLOJURE) -M:migratus -m migratus-run migrate

# Reuse the runner's existing environment parser without duplicating credential handling.
.PHONY: migrate-rollback
migrate-rollback: ## Roll back the latest Migratus migration
	@$(CLOJURE) -M:migratus -e "(require 'migratus-run 'migratus.core) (migratus.core/rollback ((ns-resolve 'migratus-run 'database-config)))"

.PHONY: migrate-status
migrate-status: ## Print completed and pending Migratus migrations
	@$(CLOJURE) -M:migratus -e "(require 'migratus-run 'migratus.core) (let [config ((ns-resolve 'migratus-run 'database-config))] (prn {:completed (migratus.core/completed-list config) :pending (migratus.core/pending-list config)}))"

.PHONY: migrate-create
migrate-create: ## Create Migratus migration files; use NAME='describe change'
	@test -n "$(NAME)" || { echo "NAME is required, e.g. make migrate-create NAME='add widgets'"; exit 2; }
	@$(CLOJURE) -M:migratus -m migratus-run create "$(NAME)"

.PHONY: deploy
deploy: ## Deploy Fly app only after fly.toml app identity is customized
	@app_name=$$(awk -F '"' '/^app = / { print $$2; exit }' fly.toml); \
	if [ -z "$$app_name" ] || [ "$$app_name" = "$(PLACEHOLDER_APP)" ]; then echo "Set a unique app name in fly.toml before deploy."; exit 2; fi
	@$(MAKE) --no-print-directory build
	@flyctl deploy --config fly.toml

.PHONY: deploy-clojars
deploy-clojars: ## Publish current JAR only from exact clean standalone annotated release tag
	@root=$$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Publishing requires standalone Git repository."; exit 2; }; \
	[ "$$root" = "$$(pwd -P)" ] || { echo "Publishing must run from standalone project root."; exit 2; }; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Publishing requires clean committed state."; exit 2; fi; \
	lib=$$($(CLOJURE) -T:build library-name); \
	if [ -z "$$lib" ] || [ "$${lib##*/}" = "$(PLACEHOLDER_LIB)" ]; then echo "Set a unique build.clj library identity before publishing."; exit 2; fi; \
	if [ -z "$${CLOJARS_USERNAME:-}" ] || [ -z "$${CLOJARS_PASSWORD:-}" ]; then echo "CLOJARS_USERNAME and CLOJARS_PASSWORD are required."; exit 2; fi; \
	version=$$($(CLOJURE) -T:build version); tag="v$$version"; \
	git rev-parse --verify --quiet "$$tag^{tag}" >/dev/null && [ "$$(git rev-parse "$$tag^{commit}")" = "$$(git rev-parse HEAD)" ] || { echo "Annotated $$tag must identify current HEAD."; exit 2; }
	@$(MAKE) --no-print-directory build
	@if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Build changed release state."; exit 2; fi
	@artifact=$$($(CLOJURE) -T:build artifact-path); pom_file=$$($(CLOJURE) -T:build pom-path); \
	test -f "$$artifact" && test -f "$$pom_file" || { echo "Expected current-version JAR and POM are missing."; exit 2; }; \
	$(CLOJURE) -X:deploy-clojars :installer :remote :artifact "\"$$artifact\"" :pom-file "\"$$pom_file\"" :sign-releases? false

.PHONY: version
version: ## Print plain semantic version
	@$(CLOJURE) -T:build version

.PHONY: major
major: ## Bump major version metadata only
	@$(CLOJURE) -T:build major

.PHONY: minor
minor: ## Bump minor version metadata only
	@$(CLOJURE) -T:build minor

.PHONY: patch
patch: ## Bump patch version metadata only
	@$(CLOJURE) -T:build patch

.PHONY: release
release: ## Validate then locally annotate clean standalone HEAD with current version
	@root=$$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Release requires standalone Git repository."; exit 2; }; \
	[ "$$root" = "$$(pwd -P)" ] || { echo "Release must run from standalone project root."; exit 2; }; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Release requires clean committed state."; exit 2; fi
	@$(MAKE) --no-print-directory build
	@if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Build changed release state."; exit 2; fi
	@version=$$($(CLOJURE) -T:build version); tag="v$$version"; \
	if git rev-parse --verify --quiet "refs/tags/$$tag" >/dev/null; then echo "$$tag already exists."; exit 2; fi; \
	git tag --annotate "$$tag" --message "Release $$tag"

.PHONY: upgrade-deps
upgrade-deps: ## Update deps.edn constraints and synchronize canonical Org source
	@$(CLOJURE) -M:antq --upgrade
	@$(CLOJURE) -M:sync-deps

.PHONY: repl
repl: ## Start a reproducible Clojure REPL with project source paths
	@$(CLOJURE) -M

.PHONY: repl-enrich
repl-enrich: ## Generate then start REPL with pinned Java-source classpath enrichment
	@enriched_command="$$($(CLOJURE) -M:enrich-repl | awk '/^clojure / { command=$$0 } END { print command }')"; \
	[[ "$$enriched_command" == clojure\ * ]] || { echo "Enrich did not return a Clojure command."; exit 2; }; \
	echo "Starting enriched REPL."; \
	eval "$$enriched_command"

.PHONY: poly
poly: ## Run Polylith only in a workspace containing workspace.edn
	@test -f workspace.edn || { echo "This base scaffold is not a Polylith workspace; add workspace.edn and components before running poly."; exit 2; }
	@$(CLOJURE) -M:poly info
