# Agent playbook

Use this repository as a catalog of language starter templates. Each language directory is intended to be copyable as a standalone starter while still conforming to a shared repo contract.

## Shared workflow

1. Run `make doctor` inside the target scaffold before changing code.
2. Use `make init` to materialize local dependencies and one-time setup.
3. Keep the common contract (`help`, `doctor`, `init`, `check`, `format`, `test`, `build`) intact across all scaffolds. [ref:common_scaffold_make_contract]
4. Run `make format`, `make check`, and `make test` before finalizing changes in any scaffold.
5. If you change a Makefile or manifest entry, regenerate docs with `make format`. [ref:generated_scaffold_docs]

## Repository guardrails

- Do not reintroduce the old conventions-document pattern; the canonical human+agent guidance now lives in `AGENTS.md` files.
- Keep provenance in `scaffolds.json` current when syncing from external template repositories.
- Preserve the per-language starter samples so smoke tests exercise a real project shape.

## Language quick references

### TypeScript
- Prefer Bun over npm or yarn inside this scaffold.
- Use Biome for both linting and formatting.
- Keep library code in `src/` and tests in `tests/`.

### Python
- Use `uv run` for project-local tooling instead of relying on global installs.
- Keep application code inside `src/python_scaffold/`.
- Classify tests with pytest markers so unit, integration, and LLM suites stay separable.

### Clojure
- Use the `:zprint` alias instead of a platform-global formatter binary.
- Keep namespaces mirrored between `src/` and `test/`.
- Run `clj-kondo` and `zprint` before reaching for heavier tooling.

### Golang
- Keep command entrypoints under `cmd/` and reusable logic under `internal/`.
- Use `gofumpt` plus `gofmt` for formatting and `golangci-lint` for static analysis.
- Prefer `gotestsum` for readable CI output.
