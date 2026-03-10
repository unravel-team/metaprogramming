# Language-Specific Makefile Features

This document highlights what each language's Makefile does that others do not. These differences reveal opportunities for building more standard tooling for codebase verification and analysis.

## Clojure (clojure/Makefile)

### Unique to Clojure

**repl-enrich**
- Launches REPL with Java source code paths via enrich-classpath
- Enables debugging into Java dependencies
- Other languages typically have IDE support for this, but Clojure's tooling is REPL-first

**install-kondo-configs**
- Downloads clj-kondo configuration from dependencies
- Provides static analysis for external libraries
- Most languages don't have tooling that automatically fetches linter configs for dependencies

**install-zprint-config**
- Creates .zprint.edn and .dir-locals.el files
- Sets up code formatting integration with editors
- While other languages have formatters, Clojure's approach is tightly integrated with the REPL workflow

**upgrade-libs**
- Upgrades all dependencies using antq
- Automated dependency auditing and upgrade suggestions
- Other languages typically handle this via package managers (npm, pip, go mod), not Makefile targets

### Standardization Opportunities
- REPL-first workflow support could be standardized across languages
- Automatic linter config fetching from dependencies is a pattern that could benefit other ecosystems

## Go (golang/Makefile)

### Unique to Go

**install-air**
- Installs air for hot-reload in development
- Go's compiled nature requires a specific hot-reload tool
- Other interpreted languages (Python, Node) often have built-in hot-reload

**install-gopls**
- Installs Go language server for IDE support
- Go's toolchain is opinionated and includes gopls as the standard LSP
- Other languages have multiple LSP options

**sync**
- Downloads and vendors dependencies
- Go's vendor/ directory workflow is language-specific
- Other languages typically use package manager commands (npm install, pip install)

### Standardization Opportunities
- Hot-reload tooling varies significantly across compiled vs interpreted languages
- Dependency vendoring is a concept that could be standardized

## Python (python/Makefile)

### Unique to Python

**test-integration** and **test-llm**
- Separate test categories for integration and LLM testing
- Python's testing ecosystem (pytest) makes test categorization easy
- Other languages typically run all tests or use tags, but Python's explicit test-type targets are notable

**install-bandit**
- Installs bandit security linter
- Runtime security scanning is more critical in Python due to its dynamic nature
- Compiled languages catch many of these issues at compile time

**docker-build**, **docker-compose-build**
- Build Docker images with Python-specific configurations
- Python's dependency management (requirements.txt, poetry) requires specific Docker setup
- Other languages have similar needs but different dependency formats

**up**, **down**, **migrate**
- Manage local infrastructure (Docker Compose, databases)
- Python web frameworks (Django, Flask) have strong database migration tooling
- The integration of database migrations into the Makefile is more common in Python projects

### Standardization Opportunities
- Security-focused linting could be standardized, especially for dynamic languages
- Database migration tooling integration could be abstracted

## TypeScript (typescript/Makefile)

### Unique to TypeScript

**ci**
- Runs bun ci command
- TypeScript's ecosystem is rapidly evolving with new runtimes (bun, deno)
- The presence of a `ci` target is a nod to TypeScript's CI/CD integration needs

**install-dev-tools** (tooling varies)
- TypeScript's tooling landscape is fragmented (npm, yarn, pnpm, bun)
- Makefiles in TypeScript projects often need to accommodate multiple package managers
- Other languages have more canonical toolchains

### Standardization Opportunities
- Multi-runtime support (node, bun, deno) could be standardized
- Package manager abstraction could be built into standard tooling

## Cross-Language Patterns

### Common Targets (Standardized)
These targets appear across all languages and are good candidates for standard tooling:
- `help` - Discoverability
- `doctor` - Toolchain verification
- `init` - Bootstrapping
- `check` - Code quality
- `format` - Consistency
- `test` - Verification
- `build` - Artifact creation

### Language-Specific Patterns

**Deployment Targets**
- Clojure: `deploy`, `deploy-lib` (Clojars-specific)
- Python: `deploy`, `rollback` (often cloud-provider specific)
- Other languages: Typically use CI/CD pipelines instead of Makefile targets

**Infrastructure Targets**
- Python: `up`, `down`, `migrate` (Django/Flask ecosystem)
- Go: Often uses docker-compose separately
- TypeScript: Varies by framework (Next.js, Express, etc.)

**Hot-Reload Targets**
- Go: `install-air`, `dev` (compiled language requirement)
- Python: Often handled by framework (uvicorn --reload)
- TypeScript: Framework-specific (next dev, vite dev)

**Tool Installation Targets**
- Clojure: Highly opinionated (clj-kondo, zprint, antq)
- Go: Standardized (gopls, air)
- Python: Diverse (bandit, black, mypy, pytest)
- TypeScript: Fragmented (eslint, prettier, typescript itself)

## Standardization Opportunities

### 1. Dependency Auditing
- Clojure has `upgrade-libs` (antq)
- Python has `pip-audit`, `safety`
- Go has `go mod tidy` and `govulncheck`
- TypeScript has `npm audit`
- **Opportunity**: A unified interface for dependency security scanning

### 2. Hot-Reload Development
- Go: air
- Python: uvicorn --reload, watchdog
- TypeScript: vite, next dev, parcel
- **Opportunity**: A language-agnostic hot-reload abstraction

### 3. Database Migrations
- Python: Often in Makefile (`make migrate`)
- Go: Typically separate (migrate, golang-migrate)
- TypeScript: Prisma, TypeORM, or framework-specific
- **Opportunity**: Standard database migration interface

### 4. Git Hooks
- Most languages: `install-hooks` target
- Implementation varies: pre-commit, husky, lein-git-down
- **Opportunity**: Unified git hook management

### 5. Linter Config Management
- Clojure: Auto-fetches configs from dependencies
- Other languages: Manual config or .gitignore-d files
- **Opportunity**: Automatic linter config propagation

## How to Use This Document

When building standard tooling:
1. **Identify common patterns** - Look for targets that appear across languages
2. **Spot unique needs** - See what each language requires that others don't
3. **Find abstraction points** - Look for similar functionality with different implementations
4. **Prioritize standardization** - Focus on high-value, high-frequency patterns (test, check, format)
5. **Respect language differences** - Don't force uniformity where language ergonomics matter

## Example: Building a Standard Dependency Auditor

Currently, each language has a different command:
```bash
# Clojure
make upgrade-libs

# Python
pip-audit check
# or
safety check

# Go
govulncheck ./...

# TypeScript
npm audit
```

A standard tool could provide a unified interface:
```bash
make audit-dependencies  # Works for all languages
```

The Makefile would delegate to the appropriate language-specific tool, but the interface is consistent.