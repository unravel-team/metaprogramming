#!/usr/bin/env python3
from __future__ import annotations

"""Fast repository checks for the scaffold catalog.

[ref:common_scaffold_make_contract]
[ref:generated_scaffold_docs]
"""

import sys

from render_scaffold_docs import expected_documents
from scaffold_tools import (
    ROOT,
    common_target_names,
    find_deprecated_conventions_usage,
    iter_scaffolds,
    language_names,
    load_manifest,
    parse_help_targets,
    required_doc_paths,
    required_scaffold_paths,
    run_make_help,
    stale_paths,
    workflow_path,
)

EXPECTED_LANGUAGES = {"typescript", "python", "clojure", "golang"}


def main() -> int:
    manifest = load_manifest()
    errors: list[str] = []

    if set(language_names(manifest)) != EXPECTED_LANGUAGES:
        errors.append(f"manifest languages are wrong: {sorted(language_names(manifest))}")

    for path in (*required_doc_paths(manifest), *required_scaffold_paths(manifest)):
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    if not workflow_path().exists():
        errors.append(f"missing CI workflow: {workflow_path().relative_to(ROOT)}")

    offenders = find_deprecated_conventions_usage(manifest)
    if offenders:
        errors.append("deprecated CONVENTIONS.md usage found: " + ", ".join(offenders))

    common_targets = common_target_names(manifest)
    for language, _, base in iter_scaffolds(manifest):
        targets = parse_help_targets(run_make_help(base))
        missing = [target for target in common_targets if target not in targets]
        if missing:
            errors.append(f"{language} is missing common targets: {', '.join(missing)}")

    stale = stale_paths(expected_documents(manifest))
    if stale:
        errors.append("generated docs are stale: " + ", ".join(stale))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("All scaffold checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
