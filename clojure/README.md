# Clojure scaffold

A minimal Clojure starter with tools.build, test-runner, zprint via alias, clj-kondo, and tagref.

## Quickstart

1. Run `make doctor` to verify the required toolchain is present.
2. Run `make init` to install dependencies and perform one-time setup.
3. Use `make format`, `make check`, `make test`, and `make build` as your normal development loop.

## Commands

```text
help                      # List the supported scaffold commands
doctor                    # Verify toolchain prerequisites and platform assumptions
install-kondo-configs     # Download clj-kondo configs from project dependencies
install-zprint-config     # Confirm the committed zprint configuration
install-gitignore         # Confirm the committed gitignore
init                      # Bootstrap dependencies and one-time setup
install                   # Alias for init
install-dev-tools         # Alias for init
check                     # Run linting, formatting checks, and docs validation
format                    # Apply canonical formatting
test                      # Run the default test suite
build                     # Produce the default build artifact
repl                      # Launch a REPL using the Clojure CLI
upgrade-libs              # Update scaffold dependencies interactively
clean                     # Remove generated artifacts
```

## Starter shape

Support files:
- `AGENTS.md`
- `README.md`
- `.aider.conf.yml`
- `.gitignore`
- `.zprint.edn`
- `.dir-locals.el`
- `deps.edn`
- `build.clj`
- `dev_tools/hooks/pre-push`
- `dev_tools/configuration/direnv.toml`

Starter code:
- `src/metaprogramming/core.clj`
- `test/metaprogramming/core_test.clj`

## Toolchain

- `clojure`
- `clj-kondo`
- `tagref`

## Provenance

- Source template: `metaclj`
- Imported from: `../metaclj`
- Source revision: `1abfdf91e7ebf2b61c5e53703602c4dc42014180`
