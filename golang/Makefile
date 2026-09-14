SHELL := /bin/bash
.SHELLFLAGS := -Eeu -o pipefail -c
.DEFAULT_GOAL := help

TOOLS_BIN := $(CURDIR)/.tools/bin
AIR := $(TOOLS_BIN)/air
GOOSE := $(TOOLS_BIN)/goose
GOVULNCHECK := $(TOOLS_BIN)/govulncheck
GOLANGCI_LINT := $(TOOLS_BIN)/golangci-lint
VERSION_SCRIPT := scripts/release.sh
PLACEHOLDER_APP := replace-with-your-fly-app-name
PLACEHOLDER_MODULE := example.com/golang-scaffold

.PHONY: help doctor init check check-format check-deps check-vet check-lint check-tagref audit-deps format test test-unit test-property test-integration test-llm test-all test-coverage build build-air ci dev clean clean-cache infra-build infra-up infra-down infra-logs infra-down-clean migrate migrate-create deploy deploy-go version major minor patch release upgrade-deps

help: ## Show scaffold workflow targets
	@awk '/^[a-zA-Z0-9_-]+:.*##/ { printf "%-20s %s\n", substr($$1, 1, length($$1)-1), substr($$0, index($$0, "##") + 3) }' $(MAKEFILE_LIST)

doctor: ## Diagnose host prerequisites and project-local tools
	@for command in go docker fly tagref; do \
		if command -v $$command >/dev/null 2>&1; then echo "$$command: found"; else echo "$$command: missing"; fi; \
	done
	@go version
	@for tool in air goose govulncheck golangci-lint; do \
		if [ -x "$(TOOLS_BIN)/$$tool" ]; then echo "$$tool: installed"; else echo "$$tool: run make init"; fi; \
	done

init: ## Copy .env when absent, download modules, and install pinned local tools
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example."; else echo ".env exists; not replacing it."; fi
	@go mod download
	@go mod verify
	@mkdir -p "$(TOOLS_BIN)"
	@GOBIN="$(TOOLS_BIN)" go install github.com/air-verse/air@v1.61.7
	@GOBIN="$(TOOLS_BIN)" go install github.com/pressly/goose/v3/cmd/goose@v3.26.0
	@GOBIN="$(TOOLS_BIN)" go install golang.org/x/vuln/cmd/govulncheck@v1.1.4
	@GOBIN="$(TOOLS_BIN)" go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.13.2

check-deps: ## Verify modules and require tidy metadata without changing it
	@go mod verify
	@go mod tidy -diff

check-format: ## Fail when gofmt would rewrite Go source
	@unformatted="$$(gofmt -l $$(find . -type f -name '*.go' -not -path './.tools/*'))"; \
	if [ -n "$$unformatted" ]; then printf 'Run make format; gofmt would change:\n%s\n' "$$unformatted"; exit 1; fi

check-vet: ## Run Go static analysis without changing dependencies
	@go vet -mod=readonly ./...

check-lint: ## Run pinned golangci-lint static analysis and configured formatters
	@$(GOLANGCI_LINT) run

check-tagref: ## Validate documented source references
	@tagref

check: check-deps check-format check-vet check-lint check-tagref ## Run offline dependency, format, static, and reference checks

audit-deps: ## Query Go vulnerability data; requires network and initialized local tool
	@$(GOVULNCHECK) ./...

format: ## Format all Go source with gofmt
	@gofmt -w $$(find . -type f -name '*.go' -not -path './.tools/*')

test-unit: ## Run all ordinary ./... tests; skip TestProperty, TestIntegration, and TestLLM prefixes
	@go test -mod=readonly ./... -run '^Test' -skip '^(TestProperty|TestIntegration|TestLLM)' $(TEST_ARGS)

test-property: ## Run Rapid property tests named TestProperty across ./...
	@go test -mod=readonly ./... -run '^TestProperty' $(TEST_ARGS)

test-integration: ## Invoke Go integration selector; no matching tests succeed by Go test policy
	@go test -mod=readonly ./... -run '^TestIntegration' $(TEST_ARGS)

test-llm: ## Invoke Go LLM selector; no matching tests succeed by Go test policy
	@go test -mod=readonly ./... -run '^TestLLM' $(TEST_ARGS)

test: test-unit test-property ## Run default unit and property suites

test-all: ## Run complete Go test suite, including integration and LLM selectors
	@go test -mod=readonly ./... $(TEST_ARGS)

test-coverage: ## Write atomic profile, function summary, and HTML for all but integration/LLM tests
	@mkdir -p coverage
	@go test -mod=readonly ./... -run '^Test' -skip '^(TestIntegration|TestLLM)' -covermode=atomic -coverpkg=./... -coverprofile=coverage/coverage.out $(TEST_ARGS)
	@go tool cover -func=coverage/coverage.out
	@go tool cover -html=coverage/coverage.out -o coverage/coverage.html

build: check test ## Validate gates, then build runnable Fly application artifact
	@mkdir -p bin
	@go build -mod=readonly -o bin/golang ./cmd/golang

build-air: ## Build Air reload binary only; normal quality gates do not run on reload
	@mkdir -p tmp
	@go build -mod=readonly -o tmp/main ./cmd/golang

ci: check test audit-deps ## Run offline checks, default tests, and network vulnerability audit

dev: ## Run development server through project-local Air on http://127.0.0.1:8080
	@$(AIR) -c .air.toml

clean: ## Remove local build, Air, and coverage artifacts
	@rm -rf bin tmp coverage

clean-cache: ## Clear Go build and test caches; preserve downloaded module cache
	@go clean -cache -testcache

infra-build: ## Build local Docker Compose services
	@docker compose build

infra-up: ## Start local PostgreSQL with named data volume
	@docker compose up -d

infra-down: ## Stop local Docker Compose services
	@docker compose down

infra-logs: ## Follow local Docker Compose service logs
	@docker compose logs -f

infra-down-clean: ## Prompt, then remove local services and volumes only for exact yes
	@echo "Warning: removing volumes permanently deletes local PostgreSQL data."
	@read -r -p "Type yes to remove volumes: " confirm || confirm=""; \
	if [ "$$confirm" = "yes" ]; then docker compose down --volumes; else echo "Aborted; volumes preserved."; fi

migrate: ## Apply Goose migrations from DATABASE_URL or a simple .env value
	@database_url="$${DATABASE_URL:-}"; \
	if [ -z "$$database_url" ] && [ -f .env ]; then database_url=$$(awk -F= '$$1 == "DATABASE_URL" { sub(/^[^=]*=/, ""); print; exit }' .env); fi; \
	test -n "$$database_url" || { echo "DATABASE_URL is required; export it or set it in .env."; exit 2; }; \
	$(GOOSE) -dir migrations postgres "$$database_url" up

migrate-create: ## Create Goose SQL migration; use NAME='describe change'
	@test -n "$(NAME)" || { echo "NAME is required, e.g. make migrate-create NAME='add widgets'"; exit 2; }
	@$(GOOSE) -dir migrations create "$(NAME)" sql

deploy: ## Deploy to Fly only after fly.toml app identity is customized
	@app_name=$$(awk -F '"' '/^app = / { print $$2; exit }' fly.toml); \
	if [ -z "$$app_name" ] || [ "$$app_name" = "$(PLACEHOLDER_APP)" ]; then echo "Set a unique app name in fly.toml before deploy."; exit 2; fi
	@$(MAKE) --no-print-directory build
	@fly deploy --config fly.toml

deploy-go: ## Push current annotated release tag to origin for Go module discovery
	@root=$$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Publishing requires standalone Git repository."; exit 2; }; \
	[ "$$root" = "$$(pwd -P)" ] || { echo "Publishing must run from standalone project root."; exit 2; }; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Publishing requires clean committed state."; exit 2; fi; \
	module_path=$$(awk '$$1 == "module" { print $$2; exit }' go.mod); \
	if [ -z "$$module_path" ] || [ "$$module_path" = "$(PLACEHOLDER_MODULE)" ]; then echo "Set a public module path in go.mod before publishing."; exit 2; fi; \
	version=$$($(VERSION_SCRIPT) version); $(VERSION_SCRIPT) validate-module "$$version"; tag="v$$version"; \
	git rev-parse --verify --quiet "$$tag^{tag}" >/dev/null && [ "$$(git rev-parse "$$tag^{commit}")" = "$$(git rev-parse HEAD)" ] || { echo "Annotated $$tag must identify current HEAD."; exit 2; }; \
	git remote get-url origin >/dev/null 2>&1 || { echo "origin remote and push credentials are required."; exit 2; }; \
	$(MAKE) --no-print-directory build; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Build changed release state."; exit 2; fi; \
	git push origin "$$tag"

version: ## Print plain semantic version
	@$(VERSION_SCRIPT) version

major: ## Bump major version metadata only, guarding Go module v2+ paths
	@$(VERSION_SCRIPT) major

minor: ## Bump minor version metadata only
	@$(VERSION_SCRIPT) minor

patch: ## Bump patch version metadata only
	@$(VERSION_SCRIPT) patch

release: ## Validate then locally annotate clean standalone HEAD with current version
	@root=$$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Release requires standalone Git repository."; exit 2; }; \
	[ "$$root" = "$$(pwd -P)" ] || { echo "Release must run from standalone project root."; exit 2; }; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Release requires clean committed state."; exit 2; fi; \
	version=$$($(VERSION_SCRIPT) version); $(VERSION_SCRIPT) validate-module "$$version"
	@$(MAKE) --no-print-directory build
	@if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then echo "Build changed release state."; exit 2; fi
	@version=$$($(VERSION_SCRIPT) version); tag="v$$version"; \
	if git rev-parse --verify --quiet "refs/tags/$$tag" >/dev/null; then echo "$$tag already exists."; exit 2; fi; \
	git tag --annotate "$$tag" --message "Release $$tag"

upgrade-deps: ## Deliberately update Go dependency requirements and checksums
	@go get -u ./...
	@go mod tidy
