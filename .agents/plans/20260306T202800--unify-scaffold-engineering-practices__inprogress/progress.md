# Progress

- 2026-03-06 20:28 IST: Created task folder and implementation plan for scaffold standardization.
- 2026-03-06 20:39 IST: Added repo-level tests that encode the desired scaffold contract, canonical docs, manifest, and removal of `CONVENTIONS.md`.
- 2026-03-06 22:15 IST: Reworked all four language folders into minimal self-validating starter scaffolds with a shared `make` contract and canonical generated docs.
- 2026-03-06 22:22 IST: Completed scaffold-standardization review and wrote severity-ordered findings to `review.md`.
- 2026-03-06 22:26 IST: Added GitHub Actions smoke-test matrix, hardened the smoke-copy path, and reran `make format`, `make test`, `make check`, and `make smoke` successfully.
- 2026-03-06 22:29 IST: Folded the review feedback back into the implementation by deriving the common contract from `scaffolds.json`, excluding transient directories from smoke copies, and pinning CI tool versions more aggressively.
