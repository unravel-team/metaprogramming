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

from scaffold_tools import TRANSIENT_DIRS, iter_scaffolds, load_manifest

SMOKE_TARGETS = ("doctor", "init", "check", "format", "test", "build")


def copy_scaffold(source: Path, destination: Path) -> Path:
    target = destination / source.name
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(*TRANSIENT_DIRS))
    return target


def run_target(language_path: Path, target: str) -> None:
    subprocess.check_call(["make", "-C", str(language_path), target])


def main() -> int:
    manifest = load_manifest()
    scaffolds = {language: base for language, _, base in iter_scaffolds(manifest)}

    parser = argparse.ArgumentParser()
    parser.add_argument("--language", choices=tuple(scaffolds))
    args = parser.parse_args()

    selected_languages = (args.language,) if args.language else tuple(scaffolds)

    with tempfile.TemporaryDirectory(prefix="scaffold-smoke-") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        for language in selected_languages:
            scaffold_path = copy_scaffold(scaffolds[language], tmp_dir)
            print(f"==> {language}")
            for target in SMOKE_TARGETS:
                run_target(scaffold_path, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
