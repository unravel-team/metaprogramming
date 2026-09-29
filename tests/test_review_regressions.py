"""Semantic regressions from full-set review; publishing is always faked."""

import json
import os
from pathlib import Path
import re
import shutil
import tarfile
import tempfile
import tomllib
import unittest

from test_scaffold_contract import LANGUAGES, ROOT, fake_tool, run, scaffold


def git_fixture(folder):
    for arguments in (
        ["init", "-q"], ["config", "user.name", "Fixture"],
        ["config", "user.email", "fixture@example.invalid"],
        ["add", "."], ["commit", "-qm", "fixture"],
        ["tag", "-a", "v0.1.0", "-m", "fixture"],
    ):
        result = run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *arguments], folder)
        if result.returncode:
            raise AssertionError(result.stderr)


def tangle(folder, language):
    expression = f'(progn (require \'org) (require \'ob-tangle) (setq org-confirm-babel-evaluate nil) (org-babel-tangle-file "{folder / (language + ".org")}"))'
    result = run(["emacs", "--batch", "-Q", "--eval", expression], folder)
    if result.returncode:
        raise AssertionError(result.stderr)


class ReviewRegressions(unittest.TestCase):
    def test_go_toolchain_floor(self):
        if "golang" not in LANGUAGES:
            self.skipTest("Go only")
        version = re.search(r"(?m)^go (\d+)\.(\d+)", (ROOT / "golang/go.mod").read_text())
        self.assertIsNotNone(version)
        # Pinned golangci-lint v2.13.2 itself requires Go 1.26.0.
        self.assertGreaterEqual(tuple(map(int, version.groups())), (1, 26))
        self.assertIn("Go 1.26+", (ROOT / "golang/README.md").read_text())
        self.assertIn("FROM golang:1.26", (ROOT / "golang/Dockerfile").read_text())

    def test_live_conventions_match_targets(self):
        for language in (name for name in LANGUAGES if name in ("python", "clojure")):
            with self.subTest(language=language):
                text = (ROOT / language / "CONVENTIONS.md").read_text()
                self.assertNotIn("make install", text)
                self.assertIn("make init", text)
                self.assertIn("make test-all", text)
                if language == "clojure":
                    self.assertNotIn(":only", text)
                    self.assertIn(":vars", text)

    def test_python_normalized_identity_bump(self):
        if "python" not in LANGUAGES:
            self.skipTest("Python only")
        with scaffold("python") as dest:
            for name in ("pyproject.toml", "python.org"):
                path = dest / name
                path.write_text(path.read_text().replace('name = "python-scaffold"', 'name = "Acme.Widget"'))
            lock = dest / "uv.lock"
            lock.write_text(lock.read_text().replace('name = "python-scaffold"', 'name = "acme-widget"'))
            result = run(["make", "-s", "patch"], dest)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            packages = tomllib.loads(lock.read_text())["package"]
            self.assertEqual(next(p for p in packages if p["name"] == "acme-widget")["version"], "0.1.1")

    def test_python_publish_normalizes_name(self):
        if "python" not in LANGUAGES:
            self.skipTest("Python only")
        for name in ("python_scaffold", "Acme.Widget"):
            with self.subTest(name=name), scaffold("python") as dest:
                project = dest / "pyproject.toml"
                project.write_text(project.read_text().replace('name = "python-scaffold"', f'name = "{name}"'))
                makefile = dest / "Makefile"
                build = 'build:\n\t@mkdir -p dist; touch dist/acme_widget-0.1.0.tar.gz dist/acme_widget-0.1.0-py3-none-any.whl\n'
                makefile.write_text(re.sub(r"^build:[^\n]*\n(?:\t[^\n]*\n|\n)*", build, makefile.read_text(), flags=re.M))
                git_fixture(dest)
                with tempfile.TemporaryDirectory() as tools:
                    calls = Path(tools) / "calls"
                    fake_tool(Path(tools), "uv", 'printf "%s\\n" "$*" > "$PUBLISH_LOG"')
                    env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}", UV_PUBLISH_TOKEN="fixture-not-token", PUBLISH_LOG=str(calls))
                    result = run(["make", "-s", "deploy-pypi"], dest, env=env)
                    if name == "python_scaffold":
                        self.assertNotEqual(result.returncode, 0)
                        self.assertRegex(result.stdout + result.stderr, r"(?i)(unique|placeholder)")
                        self.assertFalse(calls.exists())
                    else:
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertEqual(calls.read_text().strip(), "publish dist/acme_widget-0.1.0.tar.gz dist/acme_widget-0.1.0-py3-none-any.whl")

    def test_python_doctor_reports_every_missing_tool(self):
        if "python" not in LANGUAGES:
            self.skipTest("Python only")
        with scaffold("python") as dest, tempfile.TemporaryDirectory() as tools:
            fake_tool(Path(tools), "uv", "exit 127")
            env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}")
            result = run(["make", "-s", "doctor"], dest, env=env)
            for tool in ("ruff", "pytest", "basedpyright", "ty", "bandit"):
                self.assertIn(tool, result.stdout + result.stderr)

    @unittest.skipUnless(os.environ.get("RUN_ENV_FIXTURES") == "1", "Env fixture execution requires explicit opt-in")
    @unittest.skipUnless(shutil.which("uv") and (ROOT / "python/.venv").exists(), "Python init required")
    def test_python_migration_uses_env_file(self):
        if "python" not in LANGUAGES:
            self.skipTest("Python only")
        for override in (False, True):
            with self.subTest(override=override), scaffold("python") as dest:
                (dest / ".env").write_text("DATABASE_URL='file-url-$(touch should-not-exist)'\n")
                makefile = dest / "Makefile"
                # Retain real environment setup/uv flags, replace DB operation only.
                makefile.write_text(makefile.read_text().replace("alembic upgrade head", "python -c 'import os; print(os.environ.get(\"DATABASE_URL\", \"\"))'"))
                env = dict(os.environ, UV_PROJECT_ENVIRONMENT=str(ROOT / "python/.venv"))
                env.pop("DATABASE_URL", None)
                if override:
                    env["DATABASE_URL"] = "exported-url"
                result = run(["make", "-s", "migrate"], dest, env=env)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stdout.strip(), "exported-url" if override else "file-url-$(touch should-not-exist)")
                self.assertFalse((dest / "should-not-exist").exists())

    @unittest.skipUnless(shutil.which("uv") and (ROOT / "python/.venv").exists(), "Python init required")
    def test_python_alembic_accepts_percent_encoded_password(self):
        if "python" not in LANGUAGES:
            self.skipTest("Python only")
        with scaffold("python") as dest:
            env = dict(os.environ, UV_PROJECT_ENVIRONMENT=str(ROOT / "python/.venv"), DATABASE_URL="postgresql+psycopg://fixture:p%25ss@localhost/fixture")
            result = run(["uv", "run", "--no-sync", "alembic", "upgrade", "head", "--sql"], dest, env=env)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(os.environ.get("RUN_ENV_FIXTURES") == "1", "Env fixture execution requires explicit opt-in")
    @unittest.skipUnless(shutil.which("clojure"), "Clojure required")
    def test_clojure_migration_uses_env_file(self):
        if "clojure" not in LANGUAGES:
            self.skipTest("Clojure only")
        for override in (False, True):
            with self.subTest(override=override), scaffold("clojure") as dest:
                (dest / ".env").write_text("DATABASE_URL=jdbc:file-url-$(touch should-not-exist)\n")
                env = dict(os.environ)
                env.pop("DATABASE_URL", None)
                if override:
                    env["DATABASE_URL"] = "jdbc:exported-url"
                expression = "(require 'migratus-run) (println (get-in (#'migratus-run/database-config) [:db :connection-uri]))"
                result = run(["clojure", "-Srepro", "-M:migratus", "-e", expression], dest, env=env)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stdout.strip(), "jdbc:exported-url" if override else "jdbc:file-url-$(touch should-not-exist)")
                self.assertFalse((dest / "should-not-exist").exists())

    def test_clojure_checks_and_audit_include_migrations(self):
        if "clojure" not in LANGUAGES:
            self.skipTest("Clojure only")
        with scaffold("clojure") as dest, tempfile.TemporaryDirectory() as tools:
            fake_tool(Path(tools), "clojure", 'printf "%s\\n" "$*" >> "$PWD/cli.calls"')
            env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}", CLJ_WATSON_NVD_API_KEY="fixture-not-key")
            for target in ("check-deps", "audit-deps"):
                result = run(["make", "-s", target], dest, env=env)
                self.assertEqual(result.returncode, 0, result.stderr)
                calls = (dest / "cli.calls").read_text()
                self.assertIn("migratus", calls, target)
                (dest / "cli.calls").unlink()

    @unittest.skipUnless(shutil.which("emacs") and shutil.which("clojure"), "Clojure and Emacs required")
    def test_clojure_upgrade_survives_tangle(self):
        if "clojure" not in LANGUAGES:
            self.skipTest("Clojure only")
        with scaffold("clojure") as dest, tempfile.TemporaryDirectory() as tools:
            actual_clojure = shutil.which("clojure")
            fake_tool(Path(tools), "clojure", f'''case "$*" in
  *:antq*) sed '1s/^/; upgrade-fixture\\n/' deps.edn > deps.edn.tmp; mv deps.edn.tmp deps.edn ;;
  *) exec "{actual_clojure}" "$@" ;;
esac''')
            env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}")
            result = run(["make", "-s", "upgrade-deps"], dest, env=env)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            before = (dest / "deps.edn").read_bytes()
            self.assertIn(b"upgrade-fixture", before)
            tangle(dest, "clojure")
            self.assertEqual((dest / "deps.edn").read_bytes(), before)

    @unittest.skipUnless(shutil.which("emacs"), "Emacs required")
    def test_editor_selects_user_zprint_formatter(self):
        if "clojure" not in LANGUAGES:
            self.skipTest("Clojure only")
        result = run(["emacs", "--batch", "-Q", "--eval", '''
(with-temp-buffer
  (insert-file-contents ".dir-locals.el")
  (let ((settings (read (current-buffer))))
    (dolist (mode '(clojure-mode clojure-ts-mode clojurec-mode
                    clojurec-ts-mode clojurescript-mode clojurescript-ts-mode
                    clojure-dart-ts-mode clojure-jank-ts-mode))
      (unless (equal (cdr (assq 'apheleia-formatter (cdr (assq mode settings))))
                     '(zprint))
        (error "Missing zprint formatter for %s" mode)))))
'''], ROOT / "clojure")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("clojure"), "Clojure required")
    def test_coverage_names_deployed_clojure_app(self):
        if "clojure" not in LANGUAGES:
            self.skipTest("Clojure only")
        result = run(["make", "-s", "test-coverage"], ROOT / "clojure")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = (ROOT / "clojure/coverage/index.html").read_text()
        self.assertIn("metaprogramming.server", report)

    @unittest.skipUnless(shutil.which("clojure"), "Clojure required")
    def test_clofidence_propagates_instrumented_test_failure(self):
        if "clojure" not in LANGUAGES:
            self.skipTest("Clojure only")
        with scaffold("clojure") as dest:
            (dest / "test/metaprogramming/server_test.clj").unlink(missing_ok=True)
            (dest / "test/metaprogramming/instrumentation_test.clj").write_text('''(ns metaprogramming.instrumentation-test
  (:require [clojure.test :refer [deftest is]]))
(deftest ^:unit instrumentation-failure
  (is (nil? (System/getProperty "clojure.storm.instrumentOnlyPrefixes"))))
''')
            result = run(["make", "-s", "test-coverage"], dest)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("instrumentation-failure", result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("corepack") and (ROOT / "typescript/node_modules").exists(), "TypeScript init required")
    def test_staged_npm_library_has_library_only_metadata(self):
        if "typescript" not in LANGUAGES:
            self.skipTest("TypeScript only")
        result = run(["make", "-s", "build"], ROOT / "typescript")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = ROOT / "typescript/dist/package.json"
        self.assertTrue(manifest.is_file(), "Build must stage library-only package metadata")
        data = json.loads(manifest.read_text())
        source = json.loads((ROOT / "typescript/package.json").read_text())
        self.assertEqual(data["name"], source["name"])
        self.assertEqual(data["version"], source["version"])
        self.assertFalse(data.get("dependencies"))
        self.assertFalse(data.get("scripts"))
        self.assertTrue(source["private"], "Root app must not be accidentally published")
        with tempfile.TemporaryDirectory() as folder:
            result = run(["corepack", "pnpm", "--dir", "dist", "pack", "--pack-destination", folder], ROOT / "typescript")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            archives = list(Path(folder).glob("*.tgz"))
            self.assertEqual(len(archives), 1)
            with tarfile.open(archives[0]) as archive:
                packed = json.load(archive.extractfile("package/package.json"))
                self.assertEqual(packed, data)
                self.assertFalse(any("src/app" in name or ".env" in name for name in archive.getnames()))
                readme = archive.extractfile("package/README.md").read().decode()
                self.assertNotIn("make dev", readme)
                self.assertNotIn("src/app", readme)
