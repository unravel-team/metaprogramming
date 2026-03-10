# metago
Getting started quickly in Golang projects, inspired by [unravel/metaclj](https://github.com/unravel-team/metaclj)

## How to use me
Copy the Makefile into your Golang project

Running the `make` command will show you the following (below). **Follow this list** from top to bottom, for fun and profit.

```
help                      # A brief listing of all available commands
sync                      # Download dependencies
install-dev-tools         # Install all development tools
build                     # Build the deployment artifact
dev                       # Run in development mode with auto-reload, using air
server                    # Run the server binary
check                     # Check that the code is well linted, well typed, well documented
format                    # Format the code using gofumpt
test                      # Run the unit tests for the code
upgrade-libs              # Install all the deps to their latest versions
clean                     # Clean build artifacts
```

## Recommended tooling:

### Direnv: For loading and unloading `.env` files correctly.

[direnv](https://direnv.net/) is a fantastic tool for managing environment variables correctly.

The standard configuration for it is available at: [direnv.toml](dev_tools/configuration/direnv.toml). Copy this file to: `~/.config/direnv/direnv.toml`
