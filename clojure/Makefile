CLOJURE_SOURCES := $(shell find src test -type f \( -name '*.clj' -o -name '*.cljc' -o -name '*.cljs' \) 2>/dev/null) build.clj
ZPRINT := clojure -M:zprint

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
	@command -v clojure >/dev/null 2>&1 || { echo "clojure is required"; exit 1; }
	@command -v clj-kondo >/dev/null 2>&1 || { echo "clj-kondo is required"; exit 1; }
	@command -v tagref >/dev/null 2>&1 || { echo "tagref is required"; exit 1; }
	@echo "Clojure scaffold is ready."

.clj-kondo:
	mkdir -p .clj-kondo

.PHONY: install-kondo-configs
install-kondo-configs: .clj-kondo ## Download clj-kondo configs from project dependencies
	clj-kondo --lint "$$(clojure -Spath)" --copy-configs --skip-lint

.PHONY: install-zprint-config
install-zprint-config: ## Confirm the committed zprint configuration
	@echo ".zprint.edn and .dir-locals.el are committed to this scaffold."

.PHONY: install-gitignore
install-gitignore: ## Confirm the committed gitignore
	@echo ".gitignore is committed to this scaffold."

.PHONY: init
init: doctor install-kondo-configs ## Bootstrap dependencies and one-time setup
	clojure -P
	clojure -P -M:test

.PHONY: install
install: init ## Alias for init

.PHONY: install-dev-tools
install-dev-tools: init ## Alias for init

.PHONY: check-tagref
check-tagref:
	tagref

.PHONY: check-cljkondo
check-cljkondo:
	clj-kondo --lint $(CLOJURE_SOURCES)

.PHONY: check-zprint
check-zprint:
	$(ZPRINT) -c $(CLOJURE_SOURCES)

.PHONY: check
check: check-tagref check-cljkondo check-zprint ## Run linting, formatting checks, and docs validation
	@echo "All checks passed!"

.PHONY: format
format: ## Apply canonical formatting
	$(ZPRINT) -w $(CLOJURE_SOURCES)

.PHONY: test
test: ## Run the default test suite
	clojure -M:test

.PHONY: build
build: ## Produce the default build artifact
	clojure -T:build jar

.PHONY: repl
repl: ## Launch a REPL using the Clojure CLI
	clojure

.PHONY: upgrade-libs
upgrade-libs: ## Update scaffold dependencies interactively
	@echo "Update deps.edn aliases or use your preferred dependency upgrade workflow."

.PHONY: clean
clean: ## Remove generated artifacts
	rm -rf target
	rm -rf .clj-kondo/.cache
