from __future__ import annotations

"""Shared helpers for the scaffold repository.

[tag:common_scaffold_make_contract]
[tag:generated_scaffold_docs]
"""

import json
import subprocess
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCAN_EXCLUDED = {
    ".git",
    ".github",
    ".jj",
    ".agents",
    "__pycache__",
    "node_modules",
    ".venv",
    "dist",
    "target",
    "tmp",
    "bin",
}
TRANSIENT_DIRS = {
    "node_modules",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    ".basedpyright",
    ".clj-kondo",
    "coverage",
    "dist",
    "target",
    "bin",
    "tmp",
}


def load_manifest() -> dict[str, Any]:
    return json.loads((ROOT / "scaffolds.json").read_text())


def language_names(manifest: dict[str, Any]) -> tuple[str, ...]:
    return tuple(manifest["languages"])


def iter_scaffolds(
    manifest: dict[str, Any],
) -> Iterator[tuple[str, dict[str, Any], Path]]:
    for language, metadata in manifest["languages"].items():
        yield language, metadata, ROOT / language


def common_target_names(manifest: dict[str, Any]) -> tuple[str, ...]:
    return tuple(target["name"] for target in manifest["commonTargets"])


def workflow_path() -> Path:
    return ROOT / ".github" / "workflows" / "scaffolds.yml"


def run_make_help(language_path: Path) -> str:
    return subprocess.check_output(
        ["make", "-s", "-C", str(language_path), "help"],
        text=True,
    )


def parse_help_targets(help_output: str) -> dict[str, str]:
    targets: dict[str, str] = {}
    for line in help_output.splitlines():
        if "#" not in line:
            continue
        name, description = line.split("#", 1)
        targets[name.strip().split()[0]] = description.strip()
    return targets


def required_doc_paths(manifest: dict[str, Any]) -> tuple[Path, ...]:
    paths = [ROOT / "README.md", ROOT / "AGENTS.md"]
    for _, _, base in iter_scaffolds(manifest):
        paths.extend((base / "README.md", base / "AGENTS.md"))
    return tuple(paths)


def required_scaffold_paths(manifest: dict[str, Any]) -> tuple[Path, ...]:
    paths: list[Path] = []
    for _, metadata, base in iter_scaffolds(manifest):
        for rel_path in metadata["supportFiles"] + metadata["sampleFiles"]:
            paths.append(base / rel_path)
    return tuple(paths)


def iter_scaffold_files(manifest: dict[str, Any] | None = None) -> Iterator[Path]:
    active_manifest = load_manifest() if manifest is None else manifest
    for _, _, base in iter_scaffolds(active_manifest):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if any(part in SCAN_EXCLUDED for part in path.parts):
                continue
            if path.is_file():
                yield path
    for path in (ROOT / "README.md", ROOT / "AGENTS.md"):
        if path.exists():
            yield path


def find_deprecated_conventions_usage(
    manifest: dict[str, Any] | None = None,
) -> list[str]:
    offenders: list[str] = []
    for path in iter_scaffold_files(manifest):
        if path.name == "CONVENTIONS.md":
            offenders.append(str(path.relative_to(ROOT)))
            continue
        if "CONVENTIONS.md" in path.read_text(errors="ignore"):
            offenders.append(str(path.relative_to(ROOT)))
    return offenders


def stale_paths(expected_files: Mapping[Path, str]) -> list[str]:
    stale: list[str] = []
    for path, expected_content in expected_files.items():
        current_content = path.read_text() if path.exists() else None
        if current_content != expected_content:
            stale.append(str(path.relative_to(ROOT)))
    return stale
