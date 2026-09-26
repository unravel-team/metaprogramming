"""Offline contract tests for independently copied language scaffolds.

Run all: python3 -m unittest discover -s tests -v
One lane: SCAFFOLD_LANG=python python3 -m unittest discover -s tests -v
External commands are faked; these tests never deploy or remove real volumes.
"""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = tuple(os.environ.get("SCAFFOLD_LANG", "python typescript golang clojure").split())
TARGETS = {
    "help", "doctor", "init", "check", "check-format", "check-deps", "audit-deps",
    "format", "test", "test-unit", "test-property", "test-integration", "test-llm",
    "test-all", "test-coverage", "build", "ci", "dev", "clean", "clean-cache",
    "infra-build", "infra-up", "infra-down", "infra-logs", "infra-down-clean",
    "migrate", "migrate-create", "deploy", "version", "major", "minor", "patch", "release",
}
IGNORE = shutil.ignore_patterns(
    "node_modules", ".venv", ".tools", ".cache", ".hegel", ".cpcache", ".clj-kondo", "__pycache__",
    ".pytest_cache", ".ruff_cache", ".next", "coverage", "target", "dist", "bin", "tmp", ".env",
)


def run(args, cwd, **kwargs):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=90, **kwargs)


@contextmanager
def scaffold(language):
    with tempfile.TemporaryDirectory(prefix=f"scaffold-{language}-") as folder:
        dest = Path(folder) / language
        shutil.copytree(ROOT / language, dest, ignore=IGNORE)
        yield dest


def rules(text):
    return {
        match[1]: set(match[2].split())
        for match in re.finditer(r"^([a-zA-Z][\w-]*):([^\n#;]*)", text, re.M)
    }


def fake_tool(path, name, body):
    path.mkdir(parents=True, exist_ok=True)
    executable = path / name
    executable.write_text("#!/bin/sh\nset -eu\n" + body + "\n")
    executable.chmod(0o755)


class ScaffoldContract(unittest.TestCase):
    def test_targets_and_setup_boundary(self):
        for language in LANGUAGES:
            with self.subTest(language=language):
                text = (ROOT / language / "Makefile").read_text()
                table = rules(text)
                self.assertFalse(TARGETS - table.keys(), TARGETS - table.keys())
                self.assertNotRegex(text.lower(), r"dafny|install-hooks|pre-push|\.git/hooks")
                self.assertFalse({n for n in table if n.startswith(("install-", "ensure-"))})
                self.assertFalse({"install", "sync", "venv", "localinstall", "deploy-lib"} & table.keys())
                self.assertTrue({"check", "test"} <= table["build"])
                self.assertNotIn("build-air", table["build"], "Sibling prerequisites can build before gates finish")
                self.assertIn("check-format", table["check"])
                self.assertIn("check-deps", table["check"])
                self.assertTrue({"test-unit", "test-property"} <= table["test"])
                for target in ("check", "test", "build", "dev", "migrate"):
                    pending = [target]
                    seen = set()
                    while pending:
                        name = pending.pop()
                        if name in seen:
                            continue
                        seen.add(name)
                        pending.extend(table.get(name, ()))
                    self.assertNotIn("init", seen, target)
                publish = {"python": "deploy-pypi", "typescript": "deploy-npm", "golang": "deploy-go", "clojure": "deploy-clojars"}[language]
                self.assertIn(publish, table)
                result = run(["make", "--no-print-directory", "help"], ROOT / language)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertGreaterEqual(len(result.stdout.splitlines()), len(TARGETS))

    def test_volume_removal_requires_explicit_yes(self):
        for language in LANGUAGES:
            for answer in ("", "no\n", "YES\n", "yes\n"):
                with self.subTest(language=language, answer=answer), scaffold(language) as dest:
                    tools = dest / "fake-bin"
                    fake_tool(tools, "docker", 'printf "%s\\n" "$*" >> "$PWD/docker.calls"')
                    env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}")
                    result = run(["make", "--no-print-directory", "infra-down-clean"], dest, env=env, input=answer)
                    calls = (dest / "docker.calls").read_text() if (dest / "docker.calls").exists() else ""
                    if answer == "yes\n":
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn("compose down", calls)
                        self.assertRegex(calls, r"(?:-v|--volumes)")
                    else:
                        self.assertEqual(calls, "", result.stdout + result.stderr)
                    self.assertRegex(result.stdout + result.stderr, r"(?i)(volume|data)")

    def test_build_never_runs_after_a_failed_gate(self):
        for language in LANGUAGES:
            for gate in ("check", "test"):
                with self.subTest(language=language, gate=gate), scaffold(language) as dest:
                    text = (dest / "Makefile").read_text()
                    table = rules(text)
                    # Replace gate definitions entirely, retaining production build recipe.
                    for name in table:
                        if name in ("check", "test") or name.startswith(("check-", "test-")):
                            pattern = rf"^{re.escape(name)}:[^\n]*\n(?:\t[^\n]*\n|\n)*"
                            command = "exit 19" if name == gate else "true"
                            text = re.sub(pattern, f"{name}:\n\t@{command}\n", text, flags=re.M)
                    (dest / "Makefile").write_text(text)
                    tools = dest / "fake-bin"
                    for tool in ("uv", "pnpm", "go", "clojure", "docker"):
                        fake_tool(tools, tool, 'echo "$0 $*" >> "$PWD/build.calls"')
                    env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}")
                    result = run(["make", "--no-print-directory", "-j4", "build"], dest, env=env)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse((dest / "build.calls").exists(), "Artifact command ran despite failed gate")

    def test_version_bumps_are_local_and_consistent(self):
        for language in LANGUAGES:
            with self.subTest(language=language), scaffold(language) as dest:
                initial = run(["make", "-s", "version"], dest)
                self.assertEqual(initial.returncode, 0, initial.stderr)
                self.assertRegex(initial.stdout.strip(), r"^\d+\.\d+\.\d+$")
                major, minor, patch = map(int, initial.stdout.strip().split("."))
                for target, expected in (("patch", f"{major}.{minor}.{patch + 1}"), ("minor", f"{major}.{minor + 1}.0")):
                    result = run(["make", "-s", target], dest)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    version = run(["make", "-s", "version"], dest)
                    self.assertEqual(version.stdout.strip(), expected)
                    if language == "typescript":
                        self.assertEqual(json.loads((dest / "package.json").read_text())["version"], expected)
                # A nested, uninitialized scaffold must not tag the containing repo.
                result = run(["make", "-s", "release"], dest)
                self.assertNotEqual(result.returncode, 0, "Release must reject non-repository copies")

    def test_python_bump_updates_lock_metadata(self):
        if "python" not in LANGUAGES:
            self.skipTest("Python lane only")
        with scaffold("python") as dest:
            result = run(["make", "-s", "patch"], dest)
            self.assertEqual(result.returncode, 0, result.stderr)
            project = tomllib.loads((dest / "pyproject.toml").read_text())["project"]
            locked = tomllib.loads((dest / "uv.lock").read_text())
            package = next(p for p in locked["package"] if p["name"] == project["name"])
            self.assertEqual(package["version"], project["version"], "Bump must keep UV lock consistent")

    @unittest.skipUnless(shutil.which("emacs"), "Emacs required")
    def test_bumps_survive_tangling(self):
        for language in (name for name in LANGUAGES if name in ("python", "clojure")):
            with self.subTest(language=language), scaffold(language) as dest:
                result = run(["make", "-s", "patch"], dest)
                self.assertEqual(result.returncode, 0, result.stderr)
                before = run(["make", "-s", "version"], dest).stdout.strip()
                expression = f'(progn (require \'org) (require \'ob-tangle) (setq org-confirm-babel-evaluate nil) (org-babel-tangle-file "{dest / (language + ".org")}"))'
                result = run(["emacs", "--batch", "-Q", "--eval", expression], dest)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(run(["make", "-s", "version"], dest).stdout.strip(), before)

    def test_pypi_refuses_stale_tags_and_untracked_files(self):
        if "python" not in LANGUAGES:
            self.skipTest("Python lane only")
        for dirty in (False, True):
            with self.subTest(untracked=dirty), scaffold("python") as dest:
                pyproject = dest / "pyproject.toml"
                pyproject.write_text(pyproject.read_text().replace('name = "python-scaffold"', 'name = "contract-fixture-only"'))
                makefile = dest / "Makefile"
                # Exercise publication guard without running expensive build gates.
                makefile.write_text(re.sub(r"^build:[^\n]*\n(?:\t[^\n]*\n|\n)*", "build:\n\t@true\n", makefile.read_text(), flags=re.M))
                def git(*args):
                    result = run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *args], dest)
                    self.assertEqual(result.returncode, 0, result.stderr)
                git("init", "-q")
                git("config", "user.email", "fixture@example.invalid")
                git("config", "user.name", "Fixture")
                git("add", ".")
                git("commit", "-qm", "fixture")
                version = run(["make", "-s", "version"], dest).stdout.strip()
                git("tag", "-a", f"v{version}", "-m", "fixture release")
                readme = dest / "README.md"
                if dirty:
                    (dest / "untracked-source.txt").write_text("not released")
                else:
                    readme.write_text(readme.read_text() + "\nUnreleased change.\n")
                    git("add", "README.md")
                    git("commit", "-qm", "unreleased change")
                # Fake executable lives outside repository cleanliness check.
                with tempfile.TemporaryDirectory() as tools:
                    fake_tool(Path(tools), "uv", 'echo "$*" > "$PUBLISH_LOG"')
                    calls = Path(tools) / "publish.calls"
                    env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}", UV_PUBLISH_TOKEN="test-only-not-a-token", PUBLISH_LOG=str(calls))
                    result = run(["make", "-s", "deploy-pypi"], dest, env=env)
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertFalse(calls.exists(), "Publication escaped release-state guard")

    @unittest.skipUnless(shutil.which("go"), "Go required for selector integration")
    def test_go_selectors_keep_ordinary_tests(self):
        if "golang" not in LANGUAGES:
            self.skipTest("Go lane only")
        with scaffold("golang") as dest:
            setup = run(["sh", "scripts/setup-hegel.sh"], dest)
            self.assertEqual(setup.returncode, 0, setup.stdout + setup.stderr)
            fixture = dest / "internal/mathx/selectors_test.go"
            fixture.write_text('''package mathx
import "testing"
func TestParse(t *testing.T) { t.Log("ORDINARY_PARSE") }
func TestInsert(t *testing.T) { t.Log("ORDINARY_INSERT") }
func TestLogin(t *testing.T) { t.Log("ORDINARY_LOGIN") }
func TestPropertyIncluded(t *testing.T) { t.Log("PROPERTY_INCLUDED") }
func TestIntegrationExcluded(t *testing.T) { t.Fatal("integration escaped") }
func TestLLMExcluded(t *testing.T) { t.Fatal("LLM escaped") }
''')
            for target in ("test-unit", "test-coverage"):
                with self.subTest(target=target):
                    result = run(["make", "-s", target, "TEST_ARGS=-v"], dest)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    for marker in ("ORDINARY_PARSE", "ORDINARY_INSERT", "ORDINARY_LOGIN"):
                        self.assertIn(marker, result.stdout)
                    if target == "test-coverage":
                        self.assertIn("PROPERTY_INCLUDED", result.stdout)
                    else:
                        self.assertNotIn("PROPERTY_INCLUDED", result.stdout)

    def test_existing_static_analysis_is_preserved(self):
        if "golang" in LANGUAGES:
            text = (ROOT / "golang/Makefile").read_text()
            self.assertIn("golangci-lint", text)
            self.assertIn("check-lint", rules(text)["check"])
        if "clojure" in LANGUAGES:
            text = (ROOT / "clojure/Makefile").read_text()
            self.assertIn("check-cljkondo", rules(text)["check"])

    def test_go_cache_target_clears_actual_go_caches(self):
        if "golang" not in LANGUAGES:
            self.skipTest("Go lane only")
        with scaffold("golang") as dest:
            tools = dest / "fake-bin"
            fake_tool(tools, "go", 'echo "$*" >> "$PWD/go.calls"')
            env = dict(os.environ, PATH=f"{tools}:{os.environ['PATH']}")
            result = run(["make", "-s", "clean-cache"], dest, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            calls = (dest / "go.calls").read_text() if (dest / "go.calls").exists() else ""
            self.assertIn("clean", calls)
            self.assertIn("-cache", calls)
            self.assertIn("-testcache", calls)
            self.assertNotIn("-modcache", calls)

    def test_required_templates(self):
        expected = {
            "python": (".env.example", ".coveragerc", "README.md", "Dockerfile", "fly.toml", "alembic.ini", "alembic/env.py", "src/python_scaffold/api.py"),
            "typescript": ("pnpm-lock.yaml", "vitest.config.ts", "Dockerfile", "fly.toml", "src/app/page.tsx", "src/app/layout.tsx"),
            "golang": (".air.toml", "go.sum", "Dockerfile", "fly.toml"),
            "clojure": ("deps.edn", "build.clj", "Dockerfile", "fly.toml"),
        }
        for language in LANGUAGES:
            with self.subTest(language=language):
                for filename in expected[language]:
                    self.assertTrue((ROOT / language / filename).is_file(), filename)
                self.assertFalse((ROOT / language / ".env.sample").exists())
        if "typescript" in LANGUAGES:
            package = json.loads((ROOT / "typescript/package.json").read_text())
            self.assertTrue(package["packageManager"].startswith("pnpm@"))
            self.assertTrue({"knip", "jscpd", "@hegeldev/hegel", "@vitest/coverage-v8", "vitest"} <= package["devDependencies"].keys())
            self.assertEqual(package["devDependencies"]["vitest"], package["devDependencies"]["@vitest/coverage-v8"])
            self.assertTrue({"react", "react-dom", "next"} <= package["dependencies"].keys())
            self.assertFalse((ROOT / "typescript/bun.lock").exists())

    @unittest.skipUnless(shutil.which("emacs"), "Emacs required for real org-babel parity")
    def test_org_tangles_exactly(self):
        for language in (name for name in LANGUAGES if name in ("python", "clojure")):
            with self.subTest(language=language), scaffold(language) as dest:
                before = {p.relative_to(dest): p.read_bytes() for p in dest.rglob("*") if p.is_file()}
                org = dest / f"{language}.org"
                expression = f'(progn (require \'org) (require \'ob-tangle) (setq org-confirm-babel-evaluate nil) (org-babel-tangle-file "{org}"))'
                result = run(["emacs", "--batch", "-Q", "--eval", expression], dest)
                self.assertEqual(result.returncode, 0, result.stderr)
                after = {p.relative_to(dest): p.read_bytes() for p in dest.rglob("*") if p.is_file()}
                changed = {str(p) for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
                self.assertEqual(changed, set(), f"Tangle drift: {changed}")


if __name__ == "__main__":
    unittest.main()
