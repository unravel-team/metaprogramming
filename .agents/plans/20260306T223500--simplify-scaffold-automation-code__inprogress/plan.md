# Plan

1. Inspect the changed scaffold automation files and identify duplication or unnecessary complexity.
2. Prioritize behavior-preserving simplifications in the root scripts and tests first, then simplify per-language files only where it improves maintainability without reducing standalone usefulness.
3. Keep the scaffold contract and generated-document flow intact.
4. Run `make format`, `make test`, `make check`, and `make smoke` after simplification.
5. Commit the simplification as a single logical JJ commit.
