# Deletion Suggestions for Makefiles

After reviewing the original Makefiles from oldmeta, here are suggestions for targets you might want to delete. These are just suggestions—you should decide what to keep based on your team's needs.

## Clojure (clojure/Makefile)

### Potentially Deletable Targets

**repl-enrich**
- Purpose: Launch REPL with Java source code paths via enrich-classpath
- Suggestion: Delete if your team doesn't need to debug into Java sources
- Command to delete: Remove the `.enrich-classpath-repl` target and `repl-enrich` phony target

**install-kondo-configs**
- Purpose: Download clj-kondo configuration from dependencies
- Suggestion: Keep if you use external libraries; delete if you only write your own code
- Command to delete: Remove this target and its `.clj-kondo` prerequisite

**install-zprint-config**
- Purpose: Create .zprint.edn and .dir-locals.el files
- Suggestion: Keep if you use zprint; delete if you don't
- Command to delete: Remove this target and its prerequisites

**upgrade-libs**
- Purpose: Upgrade all dependencies using antq
- Suggestion: Delete if you manage dependencies manually or use a different tool
- Command to delete: Remove `install-antq`, `.antqtool.lastupdated`, and `upgrade-libs` targets

**deploy** and **deploy-lib**
- Purpose: Deploy to production or Clojars
- Suggestion: Delete if scaffolds shouldn't include deployment logic
- Command to delete: Remove both targets

## Go (golang/Makefile)

### Potentially Deletable Targets

**install-air**
- Purpose: Install air for hot-reload in development
- Suggestion: Delete if you don't do web development or use a different hot-reload tool
- Command to delete: Remove this target and the `dev` target that depends on it

**install-gopls**
- Purpose: Install Go language server for IDE support
- Suggestion: Delete if you don't need IDE integration in the scaffold
- Command to delete: Remove this target from `install-dev-tools`

**sync**
- Purpose: Download and vendor dependencies
- Suggestion: Keep - this is useful for dependency management

**install-hooks**
- Purpose: Set up git pre-push hooks
- Suggestion: Keep - this enforces quality checks

## Python (python/Makefile)

### Potentially Deletable Targets

**test-integration** and **test-llm**
- Purpose: Run specific test categories
- Suggestion: Delete if you only run unit tests; keep if you need separate test suites
- Command to delete: Remove these phony targets

**install-bandit**
- Purpose: Install bandit security linter
- Suggestion: Delete if security scanning is done separately; keep for development-time security checks
- Command to delete: Remove this target from `install-dev-tools` and bandit check from `check` target

**docker-build**, **docker-compose-build**
- Purpose: Build Docker images
- Suggestion: Delete if scaffolds shouldn't include Docker setup
- Command to delete: Remove these targets and their prerequisites

**up**, **down**, **migrate**
- Purpose: Manage local infrastructure (Docker Compose, databases)
- Suggestion: Delete if scaffolds shouldn't include infrastructure management
- Command to delete: Remove these targets

**deploy**, **rollback**
- Purpose: Deploy to production
- Suggestion: Delete if scaffolds shouldn't include deployment logic
- Command to delete: Remove these targets

## TypeScript (typescript/Makefile)

### Potentially Deletable Targets

**ci**
- Purpose: Run bun ci command
- Suggestion: Delete if not needed in CI; keep if it's useful
- Command to delete: Remove this target

**install-dev-tools** (if exists)
- Purpose: Install development-specific tools
- Suggestion: Review and keep only what your team uses
- Command to delete: Remove unused tool installation targets

## General Recommendations

### Keep These Core Targets
- `help` - Essential for discoverability
- `doctor` - Essential for toolchain verification
- `init` - Essential for bootstrapping
- `check` - Essential for code quality
- `format` - Essential for consistency
- `test` - Essential for verification
- `build` - Essential for creating artifacts

### Consider Deleting These Categories
- Deployment targets (deploy, rollback) - scaffolds shouldn't dictate deployment
- Infrastructure targets (docker, docker-compose, migrate) - scaffolds shouldn't include infrastructure
- Hot-reload targets (air, dev) - unless doing web development
- Tool installation targets for niche tools - keep only what's broadly useful

### Keep These Categories
- Code quality targets (linters, formatters, type checkers)
- Test targets (unit tests, maybe integration tests)
- Dependency management targets (sync, install)
- Git hooks (pre-push quality checks)

## How to Delete

1. Find the target definition in the Makefile
2. Delete the target line and its commands
3. Remove the target from any `.PHONY:` declarations
4. Remove the target from any other targets that depend on it
5. Test the Makefile still works with `make help`

## Example: Deleting a Target

To delete the `repl-enrich` target from clojure/Makefile:

```makefile
# DELETE THESE LINES:
.PHONY: repl-enrich
repl-enrich: .enrich-classpath-repl    ## Launch a repl enriched with Java source code paths
	@if grep --silent "^clojure" .enrich-classpath-repl; then \
		echo "Executing: $$(cat .enrich-classpath-repl)" && \
		eval $$(cat .enrich-classpath-repl); \
	else \
		echo "Falling back to Clojure repl... (you can avoid further falling back by removing .enrich-classpath-repl)"; \
		clojure $(DEPS_MAIN_OPTS); \
	fi

.enrich-classpath-repl: Makefile deps.edn $(wildcard $(HOME)/.clojure/deps.edn) $(wildcard $(XDG_CONFIG_HOME)/.clojure/deps.edn)
	cd $$(mktemp -d -t enrich-classpath.XXXXXX); clojure -Sforce -Srepro -J-XX:-OmitStackTraceInFastThrow -J-Dclojure.main.report=stderr -Sdeps '{:deps {mx.cider/tools.deps.enrich-classpath {:mvn/version $(ENRICH_CLASSPATH_VERSION)}}}' -M -m cider.enrich-classpath.clojure "clojure" "$(HERE)" "true" $(DEPS_MAIN_OPTS) | grep "^clojure" > $(HERE)/$@
```

Also delete the `ENRICH_CLASSPATH_VERSION` variable if it's only used by this target.