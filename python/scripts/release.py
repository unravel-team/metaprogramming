"""Local semantic-version operations for the copied scaffold."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
UV_LOCK = ROOT / "uv.lock"
PYTHON_ORG = ROOT / "python.org"
VERSION_PATTERN = re.compile(r'(?m)^version = "(\d+)\.(\d+)\.(\d+)"$')
ORG_VERSION_PATTERN = re.compile(
    r'(?ms)(^#\+begin_src toml :tangle "pyproject\.toml"\n.*?^version = )"\d+\.\d+\.\d+"$'
)


def read_version() -> tuple[int, int, int]:
    """Read project version, rejecting metadata outside plain semantic versioning."""
    match = VERSION_PATTERN.search(PYPROJECT.read_text())
    if match is None:
        raise ValueError("pyproject.toml must contain plain semantic project.version")
    return tuple(map(int, match.groups()))


def format_version(version: tuple[int, int, int]) -> str:
    """Format semantic version tuple."""
    return ".".join(map(str, version))


def replace_one(
    pattern: re.Pattern[str], source: str, replacement: str, label: str
) -> str:
    """Replace exactly one version declaration or reject inconsistent metadata."""
    updated, count = pattern.subn(replacement, source, count=1)
    if count != 1:
        raise ValueError(f"expected exactly one {label} version declaration")
    return updated


def bump(part: str) -> str:
    """Atomically update semantic version metadata without resolving dependencies."""
    source = PYPROJECT.read_text()
    project_name = tomllib.loads(source)["project"]["name"]
    major, minor, patch = read_version()
    if part == "major":
        next_version = (major + 1, 0, 0)
    elif part == "minor":
        next_version = (major, minor + 1, 0)
    elif part == "patch":
        next_version = (major, minor, patch + 1)
    else:
        raise ValueError(f"unsupported version component: {part}")

    version = format_version(next_version)
    metadata_replacement = rf'\g<1>"{version}"'
    lock_pattern = re.compile(
        rf'(?m)^(\[\[package\]\]\nname = "{re.escape(project_name)}"\nversion = )"\d+\.\d+\.\d+"$'
    )
    updated_project = replace_one(
        VERSION_PATTERN, source, f'version = "{version}"', "project"
    )
    updated_lock = replace_one(
        lock_pattern, UV_LOCK.read_text(), metadata_replacement, "lock"
    )
    updated_org = replace_one(
        ORG_VERSION_PATTERN,
        PYTHON_ORG.read_text(),
        metadata_replacement,
        "literate project",
    )
    PYPROJECT.write_text(updated_project)
    UV_LOCK.write_text(updated_lock)
    PYTHON_ORG.write_text(updated_org)
    return version


def main(arguments: list[str]) -> int:
    """Run requested version action."""
    if len(arguments) != 1 or arguments[0] not in {
        "version",
        "major",
        "minor",
        "patch",
    }:
        print("usage: release.py {version|major|minor|patch}", file=sys.stderr)
        return 2
    try:
        if arguments[0] == "version":
            print(format_version(read_version()))
        else:
            print(bump(arguments[0]))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
