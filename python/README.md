# Python scaffold

A uv-managed Python starter with Ruff, Pytest, BasedPyright, Bandit, and tagref.

## Quickstart

1. Run `make doctor` to verify the required toolchain is present.
2. Run `make init` to install dependencies and perform one-time setup.
3. Use `make format`, `make check`, `make test`, and `make build` as your normal development loop.

## Commands

```text
help                      # List the supported scaffold commands
doctor                    # Verify toolchain prerequisites and platform assumptions
init                      # Bootstrap dependencies and one-time setup
venv                      # Alias for init
install-ruff              # Alias for init
install-pytest            # Alias for init
install-ty                # Alias for init
install-basedpyright      # Alias for init
install-bandit            # Alias for init
install-dev-tools         # Alias for init
check                     # Run linting, typing, security, and docs validation
format                    # Apply Ruff formatting
test                      # Run the default test suite
test-llm                  # Run only the llm tests
test-integration          # Run only the integration tests
build                     # Produce the default build artifact
upgrade-libs              # Upgrade scaffold dependencies
clean                     # Remove generated artifacts
```

## Starter shape

Support files:
- `AGENTS.md`
- `README.md`
- `.aider.conf.yml`
- `.bandit.yml`
- `.env.sample`
- `.gitignore`
- `pyproject.toml`
- `uv.lock`
- `dev_tools/hooks/pre-push`
- `dev_tools/configuration/direnv.toml`

Starter code:
- `src/python_scaffold/core.py`
- `tests/test_core.py`

## Toolchain

- `python3`
- `uv`
- `tagref`

## Provenance

- Source template: `metapy`
- Imported from: `../metapy`
- Source revision: `52366e8cc9205ee2a7ac674c3ff77c8b03dfa8a0`
