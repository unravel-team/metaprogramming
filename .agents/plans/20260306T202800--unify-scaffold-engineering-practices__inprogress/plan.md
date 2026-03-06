# Plan

1. Inspect the imported language scaffolds and identify all files and targets that must be standardized.
2. Design a root-level contract for this repository: documentation, local automation, smoke tests, and CI.
3. Implement tests first for root-level scaffold validation and documentation consistency.
4. Add root-level tooling (`Makefile`, scripts, CI, docs manifest) that standardizes scaffold operations across languages.
5. Update per-language scaffolds to adopt the common outer contract (`init`, `doctor`, `check`, `format`, `test`, `build`) while preserving useful language-specific targets.
6. Remove `CONVENTIONS.md` usage and replace it with modern shared documentation focused on agent + human onboarding.
7. Run `make test`, `make check`, and `make format` at the repo root, fix failures, and commit in logically separated JJ commits.
8. Summarize the resulting system and any remaining tradeoffs.
