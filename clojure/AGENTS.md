## Lessons

- Code reviews should look for opportunities to reduce verbosity without sacrificing clarity - shorter code is often more maintainable.

## Clojure scaffold notes

- Run `make init` after copying this scaffold; normal workflow targets resolve dependencies but never run explicit installers.
- Use `make test` for unit and property tests, `make check` for reproducible dependency, format, and lint checks, and `make build` for the library JAR.
- This base scaffold is not a Polylith workspace. Add `workspace.edn` and components before invoking `make poly`.
- Keep tests tagged with `^:unit`, `^:property`, `^:integration`, or `^:llm` so selector targets remain reliable.
