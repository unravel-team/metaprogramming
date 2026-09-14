# Language scaffold differences

All four folders are standalone copies with same core Make workflow:
`doctor`, `init`, `check`, `format`, `test`, `test-coverage`, `build`, `ci`,
cleaning, local infrastructure, migrations, Fly deployment, and release/version
targets. `init` is sole normal setup target. `build` waits for `check` and default
`test`; `ci` adds networked `audit-deps`. This document records intentional
language differences rather than hiding them behind a root wrapper.

## Setup and dependency consistency

| Language | Host prerequisites | `init` behavior | `check-deps` boundary |
|---|---|---|---|
| Python | Python 3.12+, uv, tagref | Copies missing `.env`; `uv sync --locked`. | `uv lock --check` validates `uv.lock`. |
| TypeScript | Node.js 22+, Corepack, tagref | Copies missing `.env`; `corepack pnpm install --frozen-lockfile`. | Frozen lockfile-only validation; neither installs nor changes lock. |
| Go | Go 1.24+, tagref | Copies missing `.env`; downloads/verifies modules and installs pinned tools into `.tools/bin`. | `go mod verify` plus `go mod tidy -diff`; reports drift without rewriting metadata. |
| Clojure | JDK 21+, Clojure CLI, tagref | Copies missing `.env`; prefetches pinned aliases. | `clojure -Srepro -Spath` resolves project classpath. No native Clojure lockfile means this is not an offline/frozen guarantee. |

Docker Compose is needed for local PostgreSQL. Fly CLI is required only for Fly
operations. Normal checks, tests, builds, development, and migrations do not
invoke `init` or explicit installers. Native resolvers may still fetch missing
cached dependencies; Clojure has no frozen/offline guarantee. `upgrade-deps` is
explicit maintenance and may change package metadata/locks.

## Checks, tests, and coverage

`test` always runs unit plus property suites. Integration and LLM categories are
separate targets; `test-all` includes all categories. Empty optional selectors are
accepted only according to each runner's stated policy. No scaffold enforces an
arbitrary coverage percentage.

| Language | Default/property runner | `check` specifics | Coverage output and limitation |
|---|---|---|---|
| Python | pytest with Hypothesis | UV lock, Ruff format/lint, Ty, BasedPyright, Bandit, tagref. | Terminal missing-lines report, `coverage.xml`, and HTML. Measures `src`; integration/LLM paths remain uncovered. |
| TypeScript | Vitest with fast-check | Frozen pnpm validation, Biome, TypeScript, Knip, jscpd, tagref. | V8 terminal, LCOV, HTML under `coverage/`; includes unimported library/route source. Node Vitest does not render async Next server components, so dedicated integration coverage is needed there. |
| Go | `go test` with Rapid | Module check, non-mutating gofmt, `go vet`, pinned `golangci-lint`, tagref. | Atomic profile, function summary, and HTML in `coverage/`; includes all packages and excludes only integration/LLM test prefixes. Unexecuted packages can be zero. |
| Clojure | Cognitect runner with test.check | Reproducible classpath resolution, pinned zprint, pinned clj-kondo, tagref. | Clofidence HTML in `coverage/` for unit/property tests; instruments production namespaces and skips test namespaces. External paths remain uncovered. |

Property-test failures shrink generated cases: Hypothesis, fast-check, Rapid, and
test.check each provide their ecosystem's shrinking behavior.

## Audit and dependency network policy

`check` is intended to run after setup without an advisory-service request.
`audit-deps` is deliberately separate and can need network/credentials; `ci`
combines check, default tests, and audit.

| Language | Audit target | Requirements |
|---|---|---|
| Python | `pip-audit` | Network access; advisories can fail target. |
| TypeScript | `pnpm audit --audit-level=low` | Network access; low-or-higher findings fail target. |
| Go | project-local `govulncheck` | `make init` and vulnerability database network access. |
| Clojure | `clj-watson` with CVSS threshold zero | Network plus `CLJ_WATSON_NVD_API_KEY`; optional OSS Index is disabled unless project configures it. |

## Services, migrations, and local data

Each template has PostgreSQL Compose configuration, named volume, `.env.example`,
`GET /health`, Dockerfile, and `fly.toml`. Containers bind `0.0.0.0:8080` for
Fly. `deploy` rejects placeholder Fly app identity before the remote operation
and requires a successful build; it is never part of normal verification or release.

| Language | Development command | Migration tool | Environment behavior |
|---|---|---|---|
| Python | FastAPI/Uvicorn reload on port 8000 | Alembic | Alembic reads `DATABASE_URL` or its local configuration default. |
| TypeScript | Next development server on port 3000 | dbmate | `DATABASE_URL` uses `.env` defaults or exported override. |
| Go | project-local Air on port 8080; reload builds only `tmp/main` | Goose | Exported `DATABASE_URL` wins; otherwise target reads a simple value from `.env` without executing it. |
| Clojure | JVM HTTP server on port 8080 | Migratus | Requires externally supplied `DATABASE_URL`. |

`migrate-create` creates migration files; Python's Alembic autogeneration also
inspects the configured database. `migrate` contacts that database. `infra-down-clean` prints data-loss warning and removes volumes only for
exact `yes`; EOF, refusal, or any other response keeps local data.

## Artifact and cache behavior

| Language | Build result | `clean-cache` behavior |
|---|---|---|
| Python | Wheel and source distribution. | Removes project test/lint/coverage caches and UV download cache. |
| TypeScript | Next application plus separate `dist/` library JS/declarations; package whitelist keeps application internals out of npm artifact. | Removes `.next/cache`, local tool cache, coverage temporary files; leaves dependencies. |
| Go | Runnable `bin/golang` Fly binary. | Runs `go clean -cache -testcache`; preserves downloaded module cache, though build/test caches may be shared by local projects. |
| Clojure | Library JAR in `target/`, never installed into local Maven. | Removes project CLI/linter cache and preserves global Maven cache. |

`clean` removes generated build and coverage artifacts separately from cache cleanup.

## Versions, release, and publication

Across languages, `version` prints plain semantic version; `major`, `minor`, and
`patch` edit version metadata only with normal reset rules. `release` validates and
builds clean, committed standalone Git root then creates local annotated `vVERSION`
tag. It does not commit, push, change branches, or release from nested scaffold
folder.

| Language | Metadata and special guard | Explicit publish target |
|---|---|---|
| Python | Project version and lock/literate version metadata stay synchronized. | `deploy-pypi`: needs unique package name, `UV_PUBLISH_TOKEN`, and current exact-HEAD annotated tag; rebuilds current wheel/source distribution. |
| TypeScript | `package.json` version. | `deploy-npm`: needs unique package name, `NPM_TOKEN`, and current exact-HEAD annotated tag; temporary restrictive npm config supplies registry credential. |
| Go | `VERSION`; v2+ version requires matching `/vN` module path. | `deploy-go`: needs non-placeholder public module, `origin`, credentials, and current tag; pushes tag for module discovery rather than uploading registry artifact. |
| Clojure | `VERSION` with build-derived library identity. | `deploy-clojars`: needs unique `build.clj` library, Clojars credentials, current tag, JAR, and POM. |

Publication targets independently repeat standalone, clean-state, identity,
credential, and exact-release-tag guards. `release`, `ci`, checks, and tests never
publish.

## Clojure-only workflow additions

Clojure keeps two optional workflow helpers because they express JVM/REPL needs:

- `repl-enrich` uses pinned classpath enrichment, validates generated Clojure
  command, then launches enriched REPL.
- `poly` is available for teams adopting Polylith, but guard rejects base scaffold
  until `workspace.edn` and components exist.

`clojure.org` is source for generated Clojure workflow/config/source blocks. Tangle
it and require byte-for-byte parity. Python has same literate parity requirement
for `python.org`; version metadata intentionally remains outside generated blocks
where needed so version bumps survive tangling.
