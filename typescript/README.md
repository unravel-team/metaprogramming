# TypeScript Scaffold

Copied standalone Next.js App Router application and TypeScript library scaffold.

## Setup

Install Node.js 22+, Corepack, Docker Compose, `tagref`, and Fly CLI (Fly is
needed only for deployment). This project pins pnpm in `packageManager`; use
`corepack pnpm` rather than installing pnpm globally.

```sh
make init
make check test
make dev
```

`make init` copies `.env.example` only when `.env` is absent, then installs exact
locked dependencies. Normal workflow targets use local tools through
`corepack pnpm exec` and never install or update dependencies. `make check-deps`
uses frozen lockfile-only validation, so it neither changes the lockfile nor
installs packages. `make doctor` diagnoses host and project-local requirements.
`make upgrade-deps` is deliberate maintenance: review both `package.json` and
`pnpm-lock.yaml` after it runs.

## Application and library

`src/app/page.tsx` and `src/app/layout.tsx` provide the default Next.js App
Router application. `GET /health` returns `{ "status": "ok" }`
[ref:health-route]. `src/index.ts` remains separate library API; `make build`
first validates gates, then runs `next build` and emits library JavaScript and
TypeScript declarations to `dist/`. `package.json` whitelists only `dist` and
this README for npm publication, keeping Next app internals out of library
artifacts.

`make dev` serves Next locally. The Fly Docker image runs Next standalone output
on `0.0.0.0:8080`; Fly health checks use `/health`.

## Tests and checks

- `make test` runs unit and fast-check property tests only.
- `make test-unit` excludes `*.property.test.ts`, `*.integration.test.ts`, and
  `*.llm.test.ts`; `make test-property` selects property files and excludes
  external variants.
- `make test-integration` and `make test-llm` invoke real Vitest configs. Their
  `passWithNoTests` policy permits intentionally empty optional suites.
- `make test-all` runs every `*.test.ts`, including integration and LLM files.
- `make test-coverage` runs default suites with V8 terminal, LCOV, and HTML
  reports under `coverage/`. It includes unimported library and route source, so
  unexecuted application paths show as uncovered. Async Next server components
  are not rendered by these Node-environment Vitest tests; V8 remapping excludes
  their unrendered `.tsx` files. Browser/server integration coverage needs a
  dedicated integration runner.

`make check` performs frozen dependency validation, Biome formatting/linting,
TypeScript checks, Knip, jscpd, and tag reference validation. It is offline after
`make init`. `make audit-deps` queries npm advisories, requires network access,
and fails when findings meet npm's low severity threshold. `make ci` includes
check, default tests, and audit; run init first and supply network access.

## Database and local infrastructure

`make infra-up` starts PostgreSQL with named `postgres_data` volume. Database
URL defaults come from `.env`; export `DATABASE_URL` for another database.
`make migrate` runs dbmate migrations in `db/migrations`; create one with:

```sh
make migrate-create MESSAGE='add widgets'
```

`make infra-down-clean` always prints data-loss warning and reads confirmation.
Only exact `yes` removes volumes; EOF, `no`, and `YES` preserve data. No bypass
variable exists.

## Build, release, and publish safety

Customize package name, description, and Fly app name before releasing. `make
deploy` rejects placeholder Fly app identity. `make version` prints plain semantic
version; `make major`, `make minor`, and `make patch` only update `package.json`
with normal semver reset rules. They never create commits, tags, or branches.

`make release` requires clean standalone Git repository root before and after
build, then creates local annotated `vVERSION` tag. It never pushes. `make
deploy-npm` requires clean standalone exact annotated release state, custom
package name, and `NPM_TOKEN`; it creates a restrictive temporary npm config
that supplies that token to the npm registry, then builds current artifacts and
publishes. Deploy, release, publish, and migrations never run automatically.
