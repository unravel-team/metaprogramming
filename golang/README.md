# Golang scaffold

A Go starter with gofumpt, golangci-lint, gotestsum, air, and tagref.

## Quickstart

1. Run `make doctor` to verify the required toolchain is present.
2. Run `make init` to install dependencies and perform one-time setup.
3. Use `make format`, `make check`, `make test`, and `make build` as your normal development loop.

## Commands

```text
help                      # List the supported scaffold commands
doctor                    # Verify toolchain prerequisites and platform assumptions
init                      # Bootstrap dependencies and one-time setup
sync                      # Alias for init
install-air               # Install air for live reload
install-gofumpt           # Install gofumpt
install-golangci-lint     # Install golangci-lint
install-gotestsum         # Install gotestsum
install-gopls             # Install gopls
install-dev-tools         # Install optional development tools
check                     # Run linting and docs validation
format                    # Apply canonical formatting
test                      # Run the default test suite
build-air                 # Build the live-reload binary
build                     # Produce the default build artifact
dev                       # Run the starter project with live reload
server                    # Run the starter binary
upgrade-libs              # Upgrade scaffold dependencies
clean                     # Remove generated artifacts
```

## Starter shape

Support files:
- `AGENTS.md`
- `README.md`
- `.aider.conf.yml`
- `.air.toml`
- `.env.sample`
- `.gitignore`
- `.golangci.yml`
- `go.mod`
- `dev_tools/hooks/pre-push`
- `dev_tools/configuration/direnv.toml`

Starter code:
- `cmd/golang/main.go`
- `internal/mathx/mathx.go`
- `internal/mathx/mathx_test.go`

## Toolchain

- `go`
- `gofumpt`
- `golangci-lint`
- `gotestsum`
- `tagref`

## Provenance

- Source template: `metago`
- Imported from: `../metago`
- Source revision: `ef102b1d347701bb08b1b86a237b31c801aabd63`
