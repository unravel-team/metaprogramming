# Plan

1. Inspect each language template repository to determine which top-level files and directories constitute the shared scaffolding.
2. For each language, copy the Makefile and supporting documents into a matching top-level folder in this repo without modification.
3. Verify every copied file with `diff` against the source template.
4. Run repository validation commands as applicable (`make test`, `make check`, `make format`) and record any gaps.
5. Create one JJ commit per language using conventional commit messages.
6. Review the copied scaffolds and provide recommendations for stronger, repeatable software engineering practices.
