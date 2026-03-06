# Review findings

## Status

No blocking issues remain after the follow-up fixes.

## Findings addressed during implementation

1. **Duplicate contract authority**
   - Initial issue: the shared Make contract lived in both `scaffolds.json` and `scripts/scaffold_tools.py`.
   - Resolution: `scripts/scaffold_tools.py` now derives common target names from `scaffolds.json`.

2. **Smoke tests copied transient artifacts**
   - Initial issue: copied scaffolds could inherit local `node_modules`, `.venv`, `target`, or similar state.
   - Resolution: `scripts/smoke_scaffolds.py` now excludes transient directories when copying templates into temp directories.

3. **CI used unpinned tool versions**
   - Initial issue: workflow steps used floating `latest` versions for key tools.
   - Resolution: the workflow now pins Bun, uv, tagref, clj-kondo, Java, Node, and Go versions where practical.

## Remaining tradeoffs

1. **Clojure CLI version in CI is pinned to the currently validated version**
   - This improves reproducibility but means periodic maintenance is required.

2. **Go tool installation in CI still resolves the latest releases of gofumpt, golangci-lint, and gotestsum**
   - This is acceptable for now because the scaffold Makefile constrains the runtime behavior, but pinning these tools further would harden reproducibility even more.
