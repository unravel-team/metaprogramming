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

.env: .env.sample
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.sample..."; \
		cp .env.sample .env; \
		echo "✓ .env created. Please edit it with your actual values."; \
	else \
		echo ".env already exists, skipping..."; \
	fi

go.mod:
	go mod init metago

.PHONY: sync
sync: go.mod .env   ## Download dependencies
	go mod download
	go mod tidy && go mod vendor

.PHONY: install-air
install-air:
	go install github.com/air-verse/air@latest

.PHONY: install-gofumpt
install-gofumpt:
	go install mvdan.cc/gofumpt@latest

.PHONY: install-golangci-lint
install-golangci-lint:
	brew install golangci-lint

.PHONY: install-gotestsum
install-gotestsum:
	go install gotest.tools/gotestsum@latest

.PHONY: install-gopls
install-gopls:
	go install golang.org/x/tools/gopls@latest

.PHONY: install-tagref
install-tagref:
	@if ! command -v tagref >/dev/null 2>&1; then \
		echo "tagref executable not found. Please install it from https://github.com/stepchowfun/tagref?tab=readme-ov-file#installation-instructions"; \
		exit 1; \
	fi

.git/hooks/pre-push:
	@echo "Setting up Git hooks..."
	@cp dev_tools/hooks/pre-push .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "✅ Git hooks installed successfully!"
	@echo "The pre-push hook will run make check, make format, and make test before each push."

.PHONY: install-hooks
install-hooks: .git/hooks/pre-push

CONVENTIONS.md:
	@echo "Download the CONVENTIONS.md file from the [[https://github.com/unravel-team/metago][metago]] project"

.aider.conf.yml:
	@echo "Download the .aider.conf.yml file from the [[https://github.com/unravel-team/metago][metago]] project"

.gitignore:
	@echo "Download the .gitignore file from the [[https://github.com/unravel-team/metago][metago]] project"

.PHONY: install-dev-tools
install-dev-tools: install-air install-gofumpt install-golangci-lint install-gopls install-gotestsum install-tagref install-hooks CONVENTIONS.md .aider.conf.yml .gitignore    ## Install all development tools

.PHONY: check-lint
check-lint:
	golangci-lint run

.PHONY: check-tagref
check-tagref: install-tagref
	tagref

.PHONY: build-air
build-air:
	go build -o bin/metago ./cmd/metago

.PHONY: build
build: check build-air       ## Build the deployment artifact

.PHONY: server
dev:  install-air  ## Run in development mode with auto-reload, using air
	air -c .air.toml

.PHONY: server
server: build  ## Run the server binary
	./bin/metago

.PHONY: check
check: check-lint check-tagref      ## Check that the code is well linted, well typed, well documented

.PHONY: format
format:     ## Format the code using gofumpt
	gofumpt -w .
	gofmt -w .

.PHONY: test
test:   ## Run the unit tests for the code
	gotestsum --format testname

.PHONY: upgrade-libs
upgrade-libs:  ## Install all the deps to their latest versions
	go get -u ./...
	go mod tidy

.PHONY: clean
clean:  ## Clean build artifacts
	rm -rf bin/
