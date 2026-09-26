# Go Scaffold

Copied standalone Go library and HTTP service scaffold.

## Setup

Install Go 1.26+ [ref:go_setup_toolchain], Docker Compose, Fly CLI (`fly`), and `tagref` on host. `make init`
copies `.env.example` only when `.env` is absent, downloads declared modules, and
installs pinned Air, Goose, `govulncheck`, and `golangci-lint` under `.tools/bin`, and
copies Hegel's module-bundled native engine into `.tools/libhegel`. It never installs
host runtimes or tools with curl, Homebrew, or another system package manager.

```sh
make init
make check test
make dev
```

Normal checks, tests, builds, development, and migrations do not run `init` or
install dependencies. Run setup first; `make doctor` reports missing host commands
and project-local tools. `make upgrade-deps` intentionally changes dependency
requirements and `go.sum`; review those changes together.

## Test and quality workflow

- `make test` runs unit and Hegel property suites over `./...`.
- `make test-unit` runs every `Test...` function except prefixes `TestProperty`,
  `TestIntegration`, and `TestLLM`; ordinary names such as `TestParse` remain unit
  tests. Name optional category functions with those prefixes.
- `make test-property` runs `TestProperty...` tests using
  [`hegel.dev/go/hegel`](https://pkg.go.dev/hegel.dev/go/hegel), which shrinks failed
  generated cases.
- `make test-integration` and `make test-llm` always invoke `go test`; no matching
  Go tests succeed by Go's normal empty-selection behavior.
- `make test-all` includes every category.
- `make test-coverage` runs every `Test...` function except integration/LLM
  prefixes with `-covermode=atomic` and `-coverpkg=./...`, then writes
  `coverage/coverage.out`, function summary, and
  `coverage/coverage.html`. Packages without executable test paths can remain zero
  coverage; no arbitrary percentage gate exists.

`make check` runs module verification, non-mutating `gofmt` checking, `go vet`,
pinned `golangci-lint`, and `tagref`. `go mod tidy -diff` makes dependency drift visible without rewriting
metadata. `make audit-deps` calls pinned local `govulncheck`; vulnerability database
lookups need network access and findings fail command. `make ci` runs check, default
tests, and audit; run `make init` and provide network before CI.

### Hegel pilot

Hegel is pinned to v0.9.9. `internal/mathx/property_test.go` shows `hegel.Test` and
bounded integer generation while preserving the `TestProperty` naming contract.
Only test files import it; production application code stays unchanged.

`make init` runs `scripts/setup-hegel.sh` after module download/verification. It
copies the locked module's native engine into `.tools/libhegel`, rejecting symlinked
install destinations and unsupported platforms. Make exports that absolute path
via `HEGEL_LIBHEGEL_PATH`, overriding host settings. This prevents implicit native
extraction into the home cache; the module download cache remains shared as before.
`make upgrade-deps` refreshes the native copy too. After manually editing Go
requirements, rerun `make init`. Checks/tests never install or download this engine.
For direct `go test`, also export `HEGEL_LIBHEGEL_PATH="$PWD/.tools/libhegel"` from
the project root; otherwise upstream Hegel uses its default home cache.

Bundled engines cover Linux amd64/arm64, macOS arm64, and Windows amd64/arm64;
Intel macOS is unsupported by this scaffold setup. Make still requires Bash.
This pilot was exercised on macOS arm64 only; Linux/Windows and container libc
compatibility require their own acceptance run before broader adoption.

To investigate a failure, add `hegel.WithSeed(2026), hegel.WithDatabase("")` to
`hegel.Test`'s options and run `make test-property TEST_ARGS='-count=1 -v'`.
`-count=1` bypasses Go's successful-test cache. Replay requires unchanged property,
settings, and engine/library versions. Convert minimized inputs into ordinary
regressions for long-term reproduction, and remove temporary fixed seeds afterward.

Local `.hegel/` example databases can appear under tested package directories.
Git/Docker ignore them; `clean`/`clean-cache` preserve them and `.tools/libhegel`.
Hegel defaults to disabled persistence and deterministic generation in CI.
From the metaprogramming root, `HEGEL_PILOT=1 python3 -m unittest discover -s tests
-p test_hegel_pilot.py -v` exercises both installed languages: deliberate failure,
shrinking to 50, fresh-process seeded replay, and corrected-property success.
Hegel is beta; review upgrades and native compatibility together.

## Service, migrations, and local infrastructure

`make dev` always starts project-local Air. Air only runs `make build-air`, producing
`tmp/main`; reloads never rerun quality gates. Normal `make build` waits for check
and test, then creates `bin/golang`.

`GET /health` returns `{"status":"ok"}` [ref:health-route]. Container listens on
`0.0.0.0:8080`; Fly health configuration uses same port and route. `make infra-up`
starts local PostgreSQL with named `postgres_data` volume. Docker Compose reads
`POSTGRES_PASSWORD` from `.env`. `make migrate` reads a simple `DATABASE_URL=value`
from `.env` only when shell environment lacks `DATABASE_URL`; it never executes the
file, and an exported value wins. Goose receives resulting URL unchanged. Create real
SQL migrations with:

```sh
make migrate-create NAME='add widgets'
```

`make infra-down-clean` always prints data-loss warning and reads confirmation. Only
exact `yes` removes volumes; EOF, refusal, and every other response preserve data.
Make commands use project-local `GOCACHE=.cache/go-build`. `make clean-cache`
clears only that build/test cache and rejects symlinked cache paths. Shared build
and module caches remain untouched.

## Build, release, and deploy safety

Customize Fly app name before `make deploy`; placeholder identity is rejected. Build
uses Dockerfile application binary only, so module publication does not package a
separate container artifact. `make deploy` calls Fly only; no deployment happens from
normal checks or releases.

`make version` prints plain semantic version from `VERSION`. `make major`, `make
minor`, and `make patch` update only that metadata with normal reset rules. A v2+
bump refuses until `go.mod` module path deliberately ends in matching `/vN`, as Go
module imports require. `make release` requires clean, committed standalone Git root,
validates/builds it, then creates local annotated `vVERSION` tag. It never commits,
pushes, or changes branches.

Go has no central package registry. After setting non-placeholder public `module`
path, `make deploy-go` requires clean standalone `HEAD`, annotated current release
tag, `origin`, and push credentials, validates/builds, then pushes only `vVERSION` to
`origin` for Go module discovery. It never invents a registry upload. [ref:go-tag-release]
