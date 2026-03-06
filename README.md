# Metaprogramming scaffolds

This repository consolidates four language-specific starter scaffolds into one place and validates them with a single repeatable workflow.

## Common contract

Every scaffold exposes the same outer Make contract:

- `make help` — List the supported scaffold commands
- `make doctor` — Verify toolchain prerequisites and platform assumptions
- `make init` — Bootstrap local dependencies and one-time project setup
- `make check` — Run static analysis, linting, typing, and documentation validation
- `make format` — Apply the canonical formatter for the language
- `make test` — Run the default automated test suite
- `make build` — Produce the default build artifact

## Included scaffolds

- [`TypeScript`](./typescript/README.md) — A Bun-powered TypeScript starter with Biome, Vitest, and tagref checks.
- [`Python`](./python/README.md) — A uv-managed Python starter with Ruff, Pytest, BasedPyright, Bandit, and tagref.
- [`Clojure`](./clojure/README.md) — A minimal Clojure starter with tools.build, test-runner, zprint via alias, clj-kondo, and tagref.
- [`Golang`](./golang/README.md) — A Go starter with gofumpt, golangci-lint, gotestsum, air, and tagref.

## Repository automation

- `make format` regenerates canonical documentation.
- `make check` validates the manifest, Makefile contracts, and deprecated-doc removal.
- `make test` runs the repository test suite.
- `make smoke` runs the end-to-end scaffold checks across the language folders.

## Provenance

The source template revision for each language is recorded in `scaffolds.json` so updates stay auditable.
