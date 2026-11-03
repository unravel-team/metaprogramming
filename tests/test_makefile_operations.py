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


class MakefileOperations(unittest.TestCase):
    def test_migration_rollback_and_status_call_native_tools(self):
        for language, rollback, status in (
            ("python", "alembic downgrade -1", "alembic current"),
            ("typescript", "dbmate --migrations-dir db/migrations down", "dbmate --migrations-dir db/migrations status"),
            ("golang", "postgres fixture-url down", "postgres fixture-url status"),
            ("clojure", "migratus.core/rollback", "migratus.core/pending-list"),
        ):
            with self.subTest(language=language), fixture(language) as (root, env, base):
                env["DATABASE_URL"] = "fixture-url"
                fake_tool(root / ".tools/bin", "goose", 'printf "%s\\n" "$*" >> "$CALLS"')
                for target, expected in (("migrate-rollback", rollback), ("migrate-status", status)):
                    result = make(root, env, target)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    calls = (base / "calls").read_text()
                    self.assertIn(expected, calls)
                    self.assertNotIn("install", calls)
                    (base / "calls").unlink()

    def test_operational_targets_propagate_tool_failure(self):
        for language in CACHES:
            with self.subTest(language=language), fixture(language) as (root, env, base):
                env["DATABASE_URL"] = "fixture-url"
                for tool in ("uv", "corepack", "clojure"):
                    fake_tool(base / "tools", tool, "exit 19")
                fake_tool(root / ".tools/bin", "goose", "exit 19")
                for target in ("migrate-rollback", "migrate-status"):
                    result = make(root, env, target)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Error 19", result.stderr)

    def test_init_prepares_actual_clojure_alias_combinations(self):
        with fixture("clojure") as (root, env, base):
            (root / ".env.example").write_text("fixture")
            result = make(root, env, "init")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            calls = (base / "calls").read_text()
            for command in ("-P -X:test:coverage", "-P -M:antq", "-P -M:sync-deps"):
                self.assertIn(command, calls)

    @unittest.skipUnless(shutil.which("clojure"), "Clojure required")
    def test_clojure_migration_expressions_reuse_environment_parser(self):
        with fixture("clojure") as (root, env, base):
            actual_clojure = shutil.which("clojure")
            fake_tool(base / "tools", "clojure", f'exec "{actual_clojure}" "$@"')
            (root / "deps.edn").write_text('{:deps {org.clojure/clojure {:mvn/version "1.12.0"}} :aliases {:migratus {:extra-paths ["scripts"]}}}')
            shutil.copy2(ROOT / "clojure/scripts/migratus_run.clj", root / "scripts/migratus_run.clj")
            (root / "migratus.edn").write_text('{}')
            (root / "scripts/migratus").mkdir()
            (root / "scripts/migratus/core.clj").write_text('''(ns migratus.core)
(defn migrate [_])
(defn create [& _])
(defn rollback [config] (println (get-in config [:db :connection-uri])))
(defn completed-list [config] [(get-in config [:db :connection-uri])])
(defn pending-list [_] ["pending-fixture"])
''')
            env["DATABASE_URL"] = "jdbc:fixture-override"
            (root / ".env").write_text("DATABASE_URL=jdbc:fixture-file\n")
            for target in ("migrate-rollback", "migrate-status"):
                result = make(root, env, target)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("jdbc:fixture-override", result.stdout)
                self.assertNotIn("jdbc:fixture-file", result.stdout)
                if target == "migrate-status":
                    self.assertIn("pending-fixture", result.stdout)

    def test_lock_check_disables_scripts(self):
        with fixture("typescript") as (root, env, base):
            result = make(root, env, "check-deps")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("--ignore-scripts", (base / "calls").read_text())


class MakefileInstallation(unittest.TestCase):
    @contextmanager
    def go_installation(self):
        with fixture("golang") as (root, env, base):
            env["HOME"] = str(base / "temporary home")
            fake_tool(base / "tools", "go", '''
if [ "${FAIL_GATE:-}" = 1 ] && [ "$*" = "mod verify" ]; then exit 19; fi
printf '%s\\n' "$*" >> "$CALLS"
if [ "$1" = build ]; then
    while [ "$1" != -o ]; do shift; done
    shift
    printf '#!/bin/sh\\nprintf installed-cli\\n' > "$1"
fi
''')
            fake_tool(base / "tools", "gofmt", "exit 0")
            fake_tool(base / "tools", "tagref", "exit 0")
            fake_tool(root / ".tools/bin", "golangci-lint", "exit 0")
            yield root, env, base

    def test_go_install_and_uninstall_destinations(self):
        for mode in ("default", "prefix", "bindir"):
            with self.subTest(mode=mode), self.go_installation() as (root, env, base):
                arguments = []
                destination = Path(env["HOME"]) / ".local/bin"
                if mode == "prefix":
                    destination = base / "custom prefix/bin"
                    arguments = [f"PREFIX={destination.parent}"]
                elif mode == "bindir":
                    destination = base / "custom bin"
                    arguments = [f"PREFIX={base / 'unused'}", f"BINDIR={destination}"]
                result = make(root, env, "install", *arguments)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                installed = destination / "golang"
                self.assertEqual(installed.read_bytes(), (root / "bin/golang").read_bytes())
                self.assertEqual(installed.stat().st_mode & 0o777, 0o755)
                execution = subprocess.run([str(installed)], capture_output=True, text=True, timeout=5)
                self.assertEqual((execution.returncode, execution.stdout), (0, "installed-cli"))
                sentinel = destination / "unrelated"
                sentinel.write_text("preserve")
                (base / "calls").unlink()
                for _ in range(2):
                    result = make(root, env, "uninstall", *arguments)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(installed.exists())
                self.assertEqual(sentinel.read_text(), "preserve")
                self.assertFalse((base / "calls").exists(), "Uninstall must not build or test")
                help_result = make(root, env, "help")
                self.assertEqual(help_result.returncode, 0, help_result.stderr)
                for target in ("install", "uninstall"):
                    self.assertTrue(any(line.split()[0] == target for line in help_result.stdout.splitlines()))

    def test_go_failed_build_gate_preserves_existing_installation(self):
        with self.go_installation() as (root, env, base):
            destination = Path(env["HOME"]) / ".local/bin/golang"
            destination.parent.mkdir(parents=True)
            destination.write_text("existing installation")
            env["FAIL_GATE"] = "1"
            result = make(root, env, "install")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Error 19", result.stderr)
            self.assertEqual(destination.read_text(), "existing installation")
            self.assertFalse((root / "bin/golang").exists())


class MakefileCaches(unittest.TestCase):
    def test_project_caches_are_excluded_from_docker_contexts(self):
        for language in ("python", "typescript", "golang"):
            with self.subTest(language=language):
                patterns = (ROOT / language / ".dockerignore").read_text().splitlines()
                self.assertIn(".cache/", patterns)
                self.assertFalse(any(line.startswith("!") for line in patterns),
                                 "Re-inclusion patterns require checking cache exclusion precedence")

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
