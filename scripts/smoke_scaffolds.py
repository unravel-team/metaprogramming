#!/usr/bin/env python3
from __future__ import annotations

"""Run end-to-end smoke commands for scaffold directories.

The smoke test copies each scaffold to a temporary directory first so the
commands run in the same shape that downstream users will copy.
"""

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from scaffold_tools import ROOT, language_names, load_manifest

SMOKE_TARGETS = ("doctor", "init", "check", "format", "test", "build")


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


def copy_scaffold(source: Path, destination: Path) -> Path:
    target = destination / source.name
    shutil.copytree(
        source,
        target,
        symlinks=False,
        ignore=shutil.ignore_patterns(*TRANSIENT_DIRS),
    )
    return target


def run_target(language_path: Path, target: str) -> None:
    subprocess.check_call(["make", "-C", str(language_path), target])


def main() -> int:
    manifest = load_manifest()
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", choices=tuple(language_names(manifest)))
    args = parser.parse_args()

    languages = [args.language] if args.language else language_names(manifest)

    with tempfile.TemporaryDirectory(prefix="scaffold-smoke-") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        for language in languages:
            source = ROOT / manifest["languages"][language]["path"]
            scaffold_path = copy_scaffold(source, tmp_dir)
            print(f"==> {language}")
            for target in SMOKE_TARGETS:
                run_target(scaffold_path, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
