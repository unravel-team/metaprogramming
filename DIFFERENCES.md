# Language-Specific Makefile Features

This document highlights what each language's Makefile does that others do not. These differences reveal opportunities for building more standard tooling for codebase verification and analysis.

## Standardized Targets

The following targets are now standardized across all languages:

### Test Targets
- `test` - Alias for test-unit (runs unit tests)
- `test-unit` - Run only unit tests
- `test-llm` - Run LLM-specific tests
- `test-integration` - Run integration tests

### Infrastructure Targets
- `infra-build` - Build all local infrastructure (Docker Compose)
- `infra-up` - Bring up all local infrastructure
- `infra-down` - Bring down all local infrastructure
- `infra-logs` - Show logs from local infrastructure

### Database Migration Targets
- `migrate` - Run database migrations (language-specific tool)
- `migrate-create` - Create a new migration (Go, TypeScript)

### Verification Targets
- `check` - Run all checks (linters, type checkers, Dafny verification)
- `check-dafny` - Verify Dafny contracts in contracts/*.dfy

### Dependency Management
- `upgrade-deps` - Upgrade all dependencies to latest versions

## Database Migration Tools

### Tool Selection by Language

| Language | Tool | Rationale |
|----------|------|-----------|
| Python | **Alembic** | Industry standard for Python/SQLAlchemy, auto-generates migrations from models |
| Go | **Goose** | Modern Go-native tool, supports both SQL and Go code migrations, simple and reliable |
| TypeScript | **dbmate** | Language-agnostic, SQL-first, simple single binary, works well in polyglot environments |
| Clojure | **Migratus** | Standard in Clojure ecosystem (Kit framework), SQL-first with dual-file approach |

### Alembic vs dbmate vs sqlx-cli Comparison

#### Alembic (Python)
**Philosophy**: Code-first / ORM-integrated
- **Strengths**:
  - Auto-generates migrations from SQLAlchemy model diffs (`--autogenerate`)
  - Supports complex Python logic in migrations
  - Handles branching and merging of migration histories
  - Excellent for Python/SQLAlchemy projects
- **Weaknesses**:
  - Heavy dependency (requires Python + SQLAlchemy)
  - Steeper learning curve
  - Hard to use outside Python ecosystem

#### dbmate (Language-agnostic)
**Philosophy**: SQL-first / Minimalist
- **Strengths**:
  - Language-agnostic single binary (written in Go)
  - Simple, predictable, zero "magic"
  - Full control over SQL
  - Excellent for polyglot teams and microservices
  - Supports up/down migrations natively
- **Weaknesses**:
  - No auto-generation (must write SQL manually)
  - No type safety (requires external tools like Kanel for TypeScript)
  - Manual sync between migrations and application code

#### sqlx-cli (Rust)
**Philosophy**: SQL-first / Compile-time safety
- **Strengths**:
  - Compile-time query verification
  - Simple SQL file management
  - Excellent for Rust applications
  - Can be used as standalone SQL runner
- **Weaknesses**:
  - Rust-specific ecosystem
  - No auto-generation
  - Manual migration creation

### Why These Choices for Our Polyglot Project

1. **Python (Alembic)**: Since we're using Python with SQLAlchemy, Alembic is the natural choice. Its auto-generation feature saves time and keeps migrations in sync with models.

2. **Go (Goose)**: Goose is the modern Go-native choice. It supports both SQL migrations (for simple schema changes) and Go code migrations (for complex data transformations). It's more reliable than golang-migrate and simpler than Atlas.

3. **TypeScript (dbmate)**: In a polyglot environment, dbmate shines because it's language-agnostic. While Prisma is popular in TypeScript, it adds heavy abstraction and requires learning its schema language. dbmate keeps us close to SQL and works consistently across services.

4. **Clojure (Migratus)**: Migratus is the standard in the Clojure ecosystem, especially for Kit framework projects. Its dual-file approach (timestamp-name.up.sql / timestamp-name.down.sql) is clear and git-friendly.

### Alternative: Universal Migration Tool

For maximum consistency, we could use **dbmate** across Go, TypeScript, and Clojure, keeping Alembic only for Python. This would provide:
- Single tool knowledge for most services
- Consistent SQL-first approach
- Language-agnostic deployment scripts

However, we chose language-native tools because:
- They integrate better with each language's ecosystem
- Developers familiar with each language already know these tools
- Each tool has language-specific strengths (e.g., Goose's Go migrations, Migratus's Clojure integration)

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
