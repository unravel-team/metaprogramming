#!/usr/bin/env python3
from __future__ import annotations

"""Fast repository checks for the scaffold catalog.

[ref:common_scaffold_make_contract]
[ref:generated_scaffold_docs]
"""

import subprocess
import sys

from scaffold_tools import ROOT, common_target_names, find_deprecated_conventions_usage, language_names, load_manifest, parse_help_targets, required_doc_paths, run_make_help


def main() -> int:
    manifest = load_manifest()
    errors: list[str] = []

    expected_languages = set(language_names(manifest))
    if expected_languages != {"typescript", "python", "clojure", "golang"}:
        errors.append(f"manifest languages are wrong: {sorted(expected_languages)}")

    for path in required_doc_paths(manifest):
        if not path.exists():
            errors.append(f"missing canonical doc: {path.relative_to(ROOT)}")

    workflow_path = ROOT / ".github" / "workflows" / "scaffolds.yml"
    if not workflow_path.exists():
        errors.append(f"missing CI workflow: {workflow_path.relative_to(ROOT)}")

    for language in language_names(manifest):
        metadata = manifest["languages"][language]
        base = ROOT / metadata["path"]
        for rel_path in metadata["supportFiles"] + metadata["sampleFiles"]:
            if not (base / rel_path).exists():
                errors.append(f"missing scaffold file: {(base / rel_path).relative_to(ROOT)}")

    offenders = find_deprecated_conventions_usage()
    if offenders:
        errors.append("deprecated CONVENTIONS.md usage found: " + ", ".join(offenders))

    common_targets = common_target_names(manifest)
    for language in language_names(manifest):
        base = ROOT / manifest["languages"][language]["path"]
        targets = parse_help_targets(run_make_help(base))
        missing = [target for target in common_targets if target not in targets]
        if missing:
            errors.append(f"{language} is missing common targets: {', '.join(missing)}")

    render_script = ROOT / "scripts" / "render_scaffold_docs.py"
    doc_check = subprocess.run(["python3", str(render_script), "--check"], cwd=ROOT)
    if doc_check.returncode != 0:
        errors.append("generated docs are stale")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("All scaffold checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
