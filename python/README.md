# Python Scaffold

Copied standalone Python library and FastAPI service scaffold.

## Setup

Install Python 3.12+, [UV](https://docs.astral.sh/uv/), and `tagref`. Docker
Compose supports local PostgreSQL; Fly CLI is needed only for Fly deployment.

  ```sh
  make init
  make check test
  make dev
  ```

`make init` copies `.env.example` when `.env` is absent and installs dependencies
locked in `uv.lock`. Normal workflow commands use `uv run --no-sync`: run
`make init` first rather than allowing checks/tests to change dependency state.
Migration targets also load `.env` through UV, with exported `DATABASE_URL`
taking precedence. `make doctor` reports host commands and every project tool.
`make upgrade-deps` is intentional maintenance work; review changed metadata and
lockfile together.

## Test workflow

- `make test`: unit and Hypothesis property suites only.
- `make test-unit` / `make test-property`: category-specific local tests.
- `make test-integration` / `make test-llm`: invoke respective pytest selectors.
  Empty optional selections report skipped policy; runner failures do not hide.
- `make test-all`: complete suite, including external tests.
- `make test-coverage`: unit/property coverage in terminal, `coverage.xml`, and
  `coverage/index.html`. It measures `src`; unrun integration/LLM paths remain
  uncovered. No arbitrary percentage threshold exists.

`make check` is offline after `make init`: lock consistency, Ruff format/lint,
Ty, BasedPyright, Bandit, and tag references. `make audit-deps` queries PyPI
advisories through `pip-audit`, requires network, and may fail on findings.
`make ci` declares check, default tests, and audit prerequisites; Make may schedule
them in parallel. Run `make init` first and provide network access for audit.

## Service, migrations, and local infrastructure

`make dev` serves `python_scaffold.api:app`; `GET /health` returns
`{"status":"ok"}` [ref:health-route]. `make infra-up` starts PostgreSQL with
named `postgres_data` volume. After `make init`, both Alembic migration targets
load `DATABASE_URL` from `.env`; an exported value takes precedence, otherwise
Alembic uses its local default. Create revisions with:

  ```sh
  make migrate-create MESSAGE='add widgets'
  ```

`make infra-down-clean` always prints data-loss warning and reads confirmation;
only exact `yes` removes volumes. No bypass variable exists.

## Build, release, and deploy safety

`make build` waits for check and default test gates, then writes package
artifacts. Customize `project.name`, package description, and `fly.toml` app
name before distribution. `make deploy` rejects placeholder Fly app identity;
container binds `0.0.0.0:8080` and Fly checks `/health`.

`make version` prints plain semantic version. `make major`, `make minor`, and
`make patch` update project metadata, UV lock metadata, and literate source
sequentially after prevalidation, with standard reset rules. `make release`
requires this copied scaffold to be clean standalone Git root before and after
validation/build, then creates local annotated `vVERSION` tag. It never commits,
pushes, or changes branches. `make deploy-pypi` requires unique package name,
`UV_PUBLISH_TOKEN`, and annotated `vVERSION` tag pointing exactly at clean `HEAD`;
it uses PEP 503 canonical identity for unique-name and artifact checks, removes
stale `dist`, builds, and publishes only current-version wheel and source
distribution. No publish/deploy command runs automatically.
