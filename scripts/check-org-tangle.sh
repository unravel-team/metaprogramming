#!/bin/sh
# Repository maintenance only; copied scaffolds do not depend on this verifier.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 - "$ROOT" "$@" <<'PY'
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

root = Path(sys.argv[1])
languages = sys.argv[2:] or ["python", "clojure"]
if any(language not in ("python", "clojure") for language in languages):
    sys.exit("usage: sh scripts/check-org-tangle.sh [python|clojure]")

# Only literal, existing outputs are supported. Reconstruct a document containing
# source blocks alone so inherited headers, CALLs and file-local forms are inert.
header = re.compile(r'^#\+begin_src ([\w+-]+) :tangle "([^"\n]+)"\s*$', re.I)
try:
    for language in languages:
        source_root = root / language
        org = source_root / f"{language}.org"
        if source_root.is_symlink() or org.is_symlink():
            raise ValueError(f"symlink source: {org}")
        blocks, outputs, body = [], {}, None
        for line in org.read_text().splitlines(keepends=True):
            if body is not None:
                body.append(line)
                if re.fullmatch(r'#\+end_src\s*', line, re.I):
                    blocks.append("".join(body))
                    body = None
                continue
            if not re.match(r'^#\+begin_src\b', line, re.I):
                continue
            match = header.fullmatch(line)
            if not match:
                raise ValueError(f"unsupported source header in {org}: {line.strip()}")
            destination = match[2]
            path = PurePosixPath(destination)
            if path.is_absolute() or ".." in path.parts or not path.parts or "\\" in destination:
                raise ValueError(f"unsafe destination: {destination}")
            candidate = source_root
            for part in path.parts:
                candidate /= part
                if candidate.is_symlink():
                    raise ValueError(f"symlink destination: {destination}")
            if not candidate.is_file():
                raise ValueError(f"unexpected destination: {destination}")
            outputs[destination] = candidate.read_bytes()
            body = [line]
        if body is not None or not outputs:
            raise ValueError(f"incomplete or empty source blocks: {org}")
        with tempfile.TemporaryDirectory(prefix="safe-org-tangle-") as directory:
            scratch = Path(directory)
            for destination in outputs:
                (scratch / destination).parent.mkdir(parents=True, exist_ok=True)
            (scratch / "source.org").write_text("\n".join(blocks))
            expression = '''(progn
              (setq enable-local-variables nil enable-local-eval nil)
              (require 'org) (require 'ob-tangle)
              (setq org-confirm-babel-evaluate t)
              (advice-add 'org-babel-execute-src-block :override
                (lambda (&rest _) (error "Source evaluation forbidden")))
              (org-babel-tangle-file "source.org"))'''
            for iteration in (1, 2):
                result = subprocess.run(
                    ["emacs", "-Q", "--batch", "--eval", expression],
                    cwd=scratch, capture_output=True, text=True, timeout=90,
                )
                if result.returncode:
                    raise ValueError(result.stderr)
                actual = {str(p.relative_to(scratch)) for p in scratch.rglob("*") if p.is_file()}
                if actual != set(outputs) | {"source.org"}:
                    raise ValueError(f"unexpected generated destinations: {actual - set(outputs)}")
                for destination, expected in outputs.items():
                    if (scratch / destination).read_bytes() != expected:
                        raise ValueError(f"{language}/{destination}: tangle drift on pass {iteration}")
        print(f"{language}: {len(outputs)} outputs match on both passes")
except (OSError, ValueError, subprocess.TimeoutExpired) as error:
    sys.exit(str(error))
PY
