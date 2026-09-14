# Clojure scaffold

Copy this directory into its own Git repository, set a unique Clojars library
identity in `build.clj`, and replace Fly `app` in `fly.toml`. Host prerequisites
are JDK 21+, Clojure CLI, Docker Compose for local PostgreSQL, `tagref`, and
Fly CLI only when deploying. Run `make init` once: it copies `.env.example` only
when `.env` is absent and prefetches every pinned project alias. Host tools are
not installed by this scaffold.

Clojure CLI has no native lockfile. Every normal Clojure command uses `-Srepro`,
which ignores user-level aliases and resolves only checked-in project metadata.
`make init` explicitly prefetches pinned aliases; runtime CLI commands still use
native implicit cache/network resolution when a dependency is absent. Therefore
`make check-deps` verifies reproducible project-classpath resolution, not a
frozen or offline lock guarantee. `make upgrade-deps` is deliberate metadata
maintenance.

## Checks, tests, and coverage

`make check` runs reproducible dependency resolution, pinned zprint checking,
pinned JVM clj-kondo analysis, and tag references. `make format` uses the `:zprint` alias, never macOS
`/usr/bin/zprint`. Default `make test` runs `^:unit` and `^:property` tests.
Property tests use `test.check`; failing generated cases shrink automatically.
`make test-integration` and `make test-llm` invoke Cognitect metadata selectors;
an empty selector succeeds under Cognitect test-runner policy. `make test-all`
runs every test category.

`make test-coverage` runs unit and property tests through Clofidence and writes
HTML coverage to `coverage/`. Clofidence instruments production namespaces under
`metaprogramming` and skips test namespaces. Coverage is diagnostic: no arbitrary
percentage gate. Integration and LLM paths remain uncovered until those external
systems are supplied.

`make build` waits for `check` and default tests, then creates a library JAR in
`target/`; it never installs into local Maven. Only `src/` enters that JAR. The
runnable Fly HTTP app is in `app/`, binds `0.0.0.0:8080`, and exposes
`GET /health` [ref:health-route].

## Database, audit, release, and deployment

`compose.yaml` provides PostgreSQL with a named volume. `make migrate` applies
real Migratus migrations and requires `DATABASE_URL`; `make migrate-create
NAME='add widgets'` creates migration files without contacting a database.
`make infra-down-clean` always prompts and removes volumes only after exact
`yes`.

`make audit-deps` runs clj-watson with `--cvss-fail-threshold 0`, so reported
vulnerabilities fail the target. It requires network access and
`CLJ_WATSON_NVD_API_KEY`; optional OSS Index analysis is explicitly disabled
unless a project chooses to configure credentials. `make ci` includes this
networked audit after offline checks and default tests.

`make version` prints plain semantic version from `VERSION`. `make major`,
`make minor`, and `make patch` change only that metadata with normal semver reset
rules; they never commit, tag, or push. `make release` validates and creates only
a local annotated `vVERSION` tag when this copied directory is clean standalone
Git root. It rejects nested scaffold copies, preventing tags in a containing
repository. `make deploy-clojars` additionally requires a unique library
identity, current exact-HEAD tag, and Clojars credentials. `make deploy` similarly
requires unique Fly app identity before local build and Fly deployment.

The `:poly` alias is pinned for teams that adopt Polylith, but this starter is not
a workspace. `make poly` explains required `workspace.edn` guard rather than
pretending a Polylith command passed. `repl-enrich` uses pinned
`mx.cider/tools.deps.enrich-classpath`, validates its generated Clojure command,
and launches that enriched REPL; no global user aliases are assumed.

`clojure.org` is source of generated workflow, config, and source files. After
editing its blocks, run Org Babel tangle and require byte-for-byte parity before
committing. `VERSION` is intentionally outside Org so version bumps survive
tangling.
