PYTHON ?= python3
SHELL = /bin/bash -Eeuo pipefail
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show repository automation commands
	@awk '/^[a-zA-Z0-9_.-]+:.*##/ { \
		printf "%-20s # %s\n", \
		substr($$1, 1, length($$1)-1), \
		substr($$0, index($$0,"##")+3) \
	}' $(MAKEFILE_LIST)

.PHONY: format
format: ## Regenerate canonical scaffold docs
	$(PYTHON) scripts/render_scaffold_docs.py

.PHONY: check
check: ## Validate scaffold metadata and contracts
	$(PYTHON) scripts/check_scaffolds.py

.PHONY: test
test: ## Run repository tests
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

.PHONY: smoke
smoke: ## Run end-to-end smoke checks for every scaffold
	$(PYTHON) scripts/smoke_scaffolds.py

.PHONY: clean
clean: ## Remove Python cache directories used by repo automation
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
