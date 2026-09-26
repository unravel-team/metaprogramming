"""Regression tests for Makefile cache and operational targets; no live services."""

from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_scaffold_contract import ROOT, fake_tool

CACHES = {
    "python": [".cache/uv", ".pytest_cache", ".ruff_cache"],
    "typescript": [".cache/pnpm/store", ".next/cache", "node_modules/.cache", "coverage/.tmp"],
    "golang": [".cache/go-build"],
    "clojure": [".cpcache", ".clj-kondo/.cache"],
}


@contextmanager
def fixture(language):
    with tempfile.TemporaryDirectory(prefix="make-operations-") as directory:
        base = Path(directory)
        root = base / language
        root.mkdir()
        shutil.copy2(ROOT / language / "Makefile", root / "Makefile")
        for name in ("src", "app", "test", "scripts"):
            (root / name).mkdir()
        tools = base / "tools"
        for tool in ("uv", "corepack", "go", "clojure"):
            fake_tool(tools, tool, 'printf "%s|%s|%s|%s|%s\\n" "$0 $*" "${UV_CACHE_DIR:-}" "${npm_config_store_dir:-}" "${GOCACHE:-}" "${GOLANGCI_LINT_CACHE:-}" >> "$CALLS"')
        env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}", CALLS=str(base / "calls"),
                   UV_CACHE_DIR=str(base / "shared"), npm_config_store_dir=str(base / "shared"),
                   GOCACHE=str(base / "shared"), GOLANGCI_LINT_CACHE=str(base / "shared"))
        yield root, env, base


def make(root, env, target, *arguments):
    return subprocess.run(["make", "-s", target, *arguments], cwd=root, env=env,
                          capture_output=True, text=True, timeout=30)


class MakefileCaches(unittest.TestCase):
    def test_commands_use_project_caches_even_with_external_environment(self):
        for language, field, path in (("python", 1, ".cache/uv"), ("typescript", 2, ".cache/pnpm/store"), ("golang", 3, ".cache/go-build")):
            with self.subTest(language=language), fixture(language) as (root, env, base):
                result = make(root, env, "test-unit")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                fields = (base / "calls").read_text().strip().rsplit("|", 4)
                if language == "typescript":
                    self.assertIn(f'--store-dir {(root / path).resolve()}', fields[0])
                else:
                    self.assertEqual(Path(fields[field]).resolve(), (root / path).resolve())

    def test_cleanup_preserves_shared_cache_and_noncache_data(self):
        for language, caches in CACHES.items():
            with self.subTest(language=language), fixture(language) as (root, env, base):
                for cache in caches:
                    (root / cache).mkdir(parents=True, exist_ok=True)
                    (root / cache / "cached").write_text("cache")
                preserved = [base / "shared/sentinel", root / "src/source", root / ".env", root / "node_modules/package/keep"]
                for path in preserved:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("keep")
                result = make(root, env, "clean-cache")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(all(not (root / cache).exists() for cache in caches))
                self.assertTrue(all(path.read_text() == "keep" for path in preserved))
                if language == "python":
                    self.assertFalse((base / "calls").exists(), "Cleanup must not invoke global UV cache maintenance")

    def test_symlink_roots_and_ancestors_refused_before_any_deletion(self):
        for language, caches in CACHES.items():
            for cache in caches:
                parts = Path(cache).parts
                for depth in range(1, len(parts) + 1):
                    with self.subTest(language=language, cache=cache, depth=depth), fixture(language) as (root, env, base):
                        outside = base / "outside"
                        outside.mkdir()
                        sentinel = outside / "keep"
                        sentinel.write_text("keep")
                        link = root.joinpath(*parts[:depth])
                        link.parent.mkdir(parents=True, exist_ok=True)
                        link.symlink_to(outside, target_is_directory=True)
                        result = make(root, env, "clean-cache")
                        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertIn("symlink", (result.stdout + result.stderr).lower())
                        self.assertEqual(sentinel.read_text(), "keep")
                        self.assertFalse((base / "calls").exists())
