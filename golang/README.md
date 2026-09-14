# Go Scaffold

Copied standalone Go library and HTTP service scaffold.

## Setup

Install Go 1.24+, Docker Compose, Fly CLI (`fly`), and `tagref` on host. `make init`
copies `.env.example` only when `.env` is absent, downloads declared modules, and
installs pinned Air, Goose, `govulncheck`, and `golangci-lint` under `.tools/bin`. It never installs
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

- `make test` runs unit and Rapid property suites over `./...`.
- `make test-unit` runs every `Test...` function except prefixes `TestProperty`,
  `TestIntegration`, and `TestLLM`; ordinary names such as `TestParse` remain unit
  tests. Name optional category functions with those prefixes.
- `make test-property` runs `TestProperty...` tests using
  [`pgregory.net/rapid`](https://pkg.go.dev/pgregory.net/rapid), which shrinks failed
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
`make clean-cache` clears Go build/test caches with `go clean -cache -testcache`; it
does not remove downloaded module cache, but affects Go cache shared by local projects.

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
