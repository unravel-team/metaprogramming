from __future__ import annotations

"""Shared helpers for the scaffold repository.

[tag:common_scaffold_make_contract]
[tag:generated_scaffold_docs]
"""

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LANGUAGE_DIRS = ("typescript", "python", "clojure", "golang")
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


def load_manifest() -> dict[str, Any]:
    return json.loads((ROOT / "scaffolds.json").read_text())


def language_names(manifest: dict[str, Any]) -> list[str]:
    return list(manifest["languages"].keys())


def common_target_names(manifest: dict[str, Any]) -> tuple[str, ...]:
    return tuple(target["name"] for target in manifest["commonTargets"])


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
        target = name.strip().split()[0]
        targets[target] = description.strip()
    return targets


def iter_scaffold_files() -> list[Path]:
    files: list[Path] = []
    for language in LANGUAGE_DIRS:
        base = ROOT / language
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if any(part in SCAN_EXCLUDED for part in path.parts):
                continue
            if path.is_file():
                files.append(path)
    for extra in (ROOT / "README.md", ROOT / "AGENTS.md"):
        if extra.exists():
            files.append(extra)
    return files


def find_deprecated_conventions_usage() -> list[str]:
    deprecated_name = "CONVENTIONS.md"
    offenders: list[str] = []
    for path in iter_scaffold_files():
        if path.name == deprecated_name:
            offenders.append(str(path.relative_to(ROOT)))
            continue
        text = path.read_text(errors="ignore")
        if deprecated_name in text:
            offenders.append(str(path.relative_to(ROOT)))
    return offenders


def required_doc_paths(manifest: dict[str, Any]) -> list[Path]:
    paths = [ROOT / "README.md", ROOT / "AGENTS.md"]
    for metadata in manifest["languages"].values():
        base = ROOT / metadata["path"]
        paths.append(base / "README.md")
        paths.append(base / "AGENTS.md")
    return paths
