# metats
Getting started quickly in Typescript projects, inspired by
[unravel/metaclj](https://github.com/unravel-team/metaclj)

## DISCLAIMER
This is an alpha project, the tooling, configuration and how these
tools work with each other are not yet fully fleshed out. Please help
me by contributing fixes where you can!

## How to use me
Copy the Makefile into your Typescript project

Running the `make` command will show you the following (below).
**Follow this list** from top to bottom, for fun and profit.

```
help                      # A brief listing of all available commands
install                   # Install dependencies and create node_modules
install-dev-tools         # Install all development tools (ESLint, Jest, Prettier, Typescript)
upgrade-libs              # Upgrade all dependencies to their latest versions
check                     # Check that the code is well linted, well typed, well documented
format                    # Format code with Prettier and fix ESLint issues
test                      # Run all the tests for the code
test-watch                # Run tests in watch mode
dev                       # Run the Next.js development server with Turbopack
build                     # Build the Next.js application for production
start                     # Start the production server
docker-compose-build      # Build all the local infra (docker-compose)
up                        # Bring up all the local infra (docker-compose)
down                      # Bring down all the local infra (docker-compose)
logs                      # Show all the logs (docker-compose)
deploy                    # Deploy the current code to production
clean-cache               # Clean bun cache and Next.js cache
clean                     # Delete any existing artifacts
```

## Recommended tooling:

### Direnv: For loading and unloading `.env` files correctly.

[direnv](https://direnv.net/) is a fantastic tool for managing
environment variables correctly.

The standard configuration for it is available at:
[direnv.toml](dev_tools/configuration/direnv.toml). Copy this file to:
`~/.config/direnv/direnv.toml`
