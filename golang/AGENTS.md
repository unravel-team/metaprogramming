# Golang scaffold agent guide

This scaffold follows the shared Make contract: `help`, `doctor`, `init`, `check`, `format`, `test`, `build`.

## Working rules

1. Start with `make doctor` and `make init`.
2. Keep the starter sample code compiling and tested.
3. Regenerate docs after Makefile changes with the repository root `make format`.
4. Treat this directory as a copyable standalone template, not just a docs folder.

## Language-specific guidance

- Keep command entrypoints under `cmd/` and reusable logic under `internal/`.
- Use `gofumpt` plus `gofmt` for formatting and `golangci-lint` for static analysis.
- Prefer `gotestsum` for readable CI output.
