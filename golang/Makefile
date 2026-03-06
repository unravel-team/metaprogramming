GO_BIN ?= $(HOME)/go/bin
PATH := $(GO_BIN):$(PATH)
MAIN_PACKAGE := ./cmd/golang
BUILD_OUTPUT := ./bin/golang
AIR_OUTPUT := ./tmp/main

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
	@command -v go >/dev/null 2>&1 || { echo "go is required"; exit 1; }
	@command -v gofumpt >/dev/null 2>&1 || { echo "gofumpt is required"; exit 1; }
	@command -v golangci-lint >/dev/null 2>&1 || { echo "golangci-lint is required"; exit 1; }
	@command -v gotestsum >/dev/null 2>&1 || { echo "gotestsum is required"; exit 1; }
	@command -v tagref >/dev/null 2>&1 || { echo "tagref is required"; exit 1; }
	@echo "Go scaffold is ready."

.PHONY: init
init: doctor .env ## Bootstrap dependencies and one-time setup
	go mod download
	go mod tidy

.PHONY: sync
sync: init ## Alias for init

.PHONY: install-air
install-air: ## Install air for live reload
	go install github.com/air-verse/air@latest

.PHONY: install-gofumpt
install-gofumpt: ## Install gofumpt
	go install mvdan.cc/gofumpt@latest

.PHONY: install-golangci-lint
install-golangci-lint: ## Install golangci-lint
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

.PHONY: install-gotestsum
install-gotestsum: ## Install gotestsum
	go install gotest.tools/gotestsum@latest

.PHONY: install-gopls
install-gopls: ## Install gopls
	go install golang.org/x/tools/gopls@latest

.PHONY: install-dev-tools
install-dev-tools: ## Install optional development tools
	$(MAKE) install-air install-gofumpt install-golangci-lint install-gotestsum install-gopls

.PHONY: check-lint
check-lint:
	golangci-lint run ./...

.PHONY: check-tagref
check-tagref:
	tagref

.PHONY: check
check: check-lint check-tagref ## Run linting and docs validation
	@echo "All checks passed!"

.PHONY: format
format: ## Apply canonical formatting
	gofumpt -w .
	gofmt -w .

.PHONY: test
test: ## Run the default test suite
	gotestsum --format testname ./...

.PHONY: build-air
build-air: ## Build the live-reload binary
	go build -o $(AIR_OUTPUT) $(MAIN_PACKAGE)

.PHONY: build
build: ## Produce the default build artifact
	go build -o $(BUILD_OUTPUT) $(MAIN_PACKAGE)

.PHONY: dev
dev: ## Run the starter project with live reload
	air -c .air.toml

.PHONY: server
server: build ## Run the starter binary
	$(BUILD_OUTPUT)

.PHONY: upgrade-libs
upgrade-libs: ## Upgrade scaffold dependencies
	go get -u ./...
	go mod tidy

.PHONY: clean
clean: ## Remove generated artifacts
	rm -rf bin tmp
