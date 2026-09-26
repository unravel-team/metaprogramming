"""Hegel scaffold contracts; native acceptance tests opt in after make init."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HegelContracts(unittest.TestCase):
    def test_pinned_test_dependencies(self):
        package = json.loads((ROOT / "typescript/package.json").read_text())
        self.assertEqual(package["devDependencies"]["@hegeldev/hegel"], "0.4.7")
        self.assertNotIn("fast-check", package["devDependencies"])
        self.assertNotIn("@hegeldev/hegel", package["dependencies"])
        module = (ROOT / "golang/go.mod").read_text()
        self.assertIn("hegel.dev/go/hegel v0.9.9", module)
        self.assertNotIn("pgregory.net/rapid", module)

    def test_native_setup_is_explicit_and_local(self):
        result = subprocess.run(["make", "-s", "-C", str(ROOT / "golang"),
                                 "-f", "Makefile", "-f", "-", "pilot-env"],
                                input="pilot-env:\n\t@printf '%s' \"$$HEGEL_LIBHEGEL_PATH\"\n",
                                env={**os.environ, "HEGEL_LIBHEGEL_PATH": "/outside/libhegel"},
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(result.stdout).resolve(), (ROOT / "golang/.tools/libhegel").resolve())
        setup = (ROOT / "golang/scripts/setup-hegel.sh").read_text()
        self.assertNotIn("curl", setup)
        self.assertNotIn("wget", setup)
        self.assertIn("scripts/setup-hegel.sh", (ROOT / "golang/Makefile").read_text())

    def test_native_setup_copies_module_asset_and_rejects_symlinks(self):
        with tempfile.TemporaryDirectory(prefix="hegel-setup-") as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            shutil.copy2(ROOT / "golang/scripts/setup-hegel.sh", root / "scripts/setup-hegel.sh")
            binary = root / "module/internal/libhegel/libs/libhegel-darwin-arm64.dylib"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"fixture-native-library")
            (root / "bin").mkdir()
            go = root / "bin/go"
            go.write_text('#!/bin/sh\ncase "$*" in\n"env GOOS") echo darwin;;\n"env GOARCH") echo "${TEST_ARCH:-arm64}";;\n"list "*) echo "$PWD/module";;\n*) exit 19;;\nesac\n')
            go.chmod(0o755)
            env = {**os.environ, "PATH": f"{root / 'bin'}:{os.environ['PATH']}"}
            command = ["sh", "scripts/setup-hegel.sh"]
            result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / ".tools/libhegel").read_bytes(), binary.read_bytes())
            unsupported = subprocess.run(command, cwd=root, env={**env, "TEST_ARCH": "amd64"}, capture_output=True, text=True)
            self.assertEqual(unsupported.returncode, 2)
            self.assertIn("no bundled native engine", unsupported.stderr)
            (root / ".tools/libhegel").unlink()
            outside = root / "outside"
            outside.write_text("keep")
            (root / ".tools/libhegel").symlink_to(outside)
            refused = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(outside.read_text(), "keep")

    def test_typescript_native_build_policy_is_available_in_container(self):
        policy = (ROOT / "typescript/pnpm-workspace.yaml").read_text()
        self.assertIn("koffi: true", policy)
        self.assertIn("COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./",
                      (ROOT / "typescript/Dockerfile").read_text())

    def test_replay_databases_ignored_in_git_and_docker(self):
        for language in ("typescript", "golang"):
            with self.subTest(language=language):
                self.assertIn(".hegel/", (ROOT / language / ".gitignore").read_text().splitlines())
                self.assertIn("**/.hegel/", (ROOT / language / ".dockerignore").read_text().splitlines())


@unittest.skipUnless(os.environ.get("HEGEL_PILOT") == "1", "Set HEGEL_PILOT=1 after TypeScript/Go setup")
class HegelNativePilot(unittest.TestCase):
    def check_failure_replay_and_fix(self, command, cwd, env, success_marker="pilot-executed"):
        for _ in range(2):
            result = subprocess.run(command, cwd=cwd, env=env, text=True,
                                    capture_output=True, timeout=120)
            self.assertNotEqual(result.returncode, 0, "False property silently passed")
            output = result.stdout + result.stderr
            self.assertIn("pilot-counterexample:50", output, output)
        fixed = subprocess.run(command, cwd=cwd, env={**env, "FIX_PILOT": "1"},
                               text=True, capture_output=True, timeout=120)
        self.assertEqual(fixed.returncode, 0, fixed.stdout + fixed.stderr)
        self.assertIn(success_marker, fixed.stdout + fixed.stderr)

    def test_typescript_detects_shrinks_replays_and_passes_fix(self):
        entry = (ROOT / "typescript/node_modules/@hegeldev/hegel/dist/index.js").as_uri()
        generators = (ROOT / "typescript/node_modules/@hegeldev/hegel/dist/generators/index.js").as_uri()
        with tempfile.TemporaryDirectory(prefix="hegel-ts-") as directory:
            root = Path(directory)
            script = root / "pilot.property.test.mjs"
            vitest = ROOT / "typescript/node_modules/vitest"
            (root / "vitest.config.mjs").write_text('export default {test: {include: ["*.property.test.mjs"]}};')
            script.write_text(f'''import {{test}} from {json.dumps((vitest / "dist/index.js").as_uri())};
import * as h from {json.dumps(entry)};
import * as gs from {json.dumps(generators)};
test("native pilot", () => {{
let calls = 0;
h.test((tc) => {{
  calls++;
  const n = tc.draw(gs.integers({{minValue: 0, maxValue: 1000}}));
  if (!process.env.FIX_PILOT && n >= 50) throw new Error(`pilot-counterexample:${{n}}`);
  if (n < 0 || n > 1000) throw new Error("generator out of bounds");
}}, {{seed: 2026, testCases: 100, database: h.Database.disabled}});
if (calls < 2) throw new Error("property never explored");
console.log("pilot-executed");
}});
''')
            env = {**os.environ, "HOME": str(root / "home"), "XDG_CACHE_HOME": str(root / "home/cache")}
            env.pop("HEGEL_LIBHEGEL_PATH", None)
            env.pop("FIX_PILOT", None)
            self.check_failure_replay_and_fix(["node", str(vitest / "vitest.mjs"), "run",
                                               "--config", str(root / "vitest.config.mjs")], root, env, "1 passed")
            # Vitest writes its own secret token under HOME; only engine caches are forbidden.
            home_paths = [str(p.relative_to(root / "home")) for p in (root / "home").rglob("*")]
            self.assertFalse(any("hegel" in p.lower() or "koffi" in p.lower() for p in home_paths),
                             f"Native loader wrote a home cache: {home_paths}")

    def test_go_detects_shrinks_replays_and_passes_fix(self):
        with tempfile.TemporaryDirectory(prefix="hegel-go-") as directory:
            root = Path(directory)
            for name in ("go.mod", "go.sum", "Makefile"):
                shutil.copy2(ROOT / "golang" / name, root / name)
            (root / ".tools").mkdir()
            shutil.copy2(ROOT / "golang/.tools/libhegel", root / ".tools/libhegel")
            (root / "pilot_test.go").write_text('''package pilot
import (
    "os"
    "testing"
    "hegel.dev/go/hegel"
)
func TestPropertyPilot(t *testing.T) {
    calls := 0
    hegel.Test(t, func(ht *hegel.T) {
        calls++
        n := hegel.Draw(ht, hegel.Integers(0, 1000))
        if os.Getenv("FIX_PILOT") == "" && n >= 50 { ht.Fatalf("pilot-counterexample:%d", n) }
        if n < 0 || n > 1000 { ht.Fatal("generator out of bounds") }
    }, hegel.WithSeed(2026), hegel.WithTestCases(100), hegel.WithDatabase(""))
    if calls < 2 { t.Fatal("property never explored") }
    t.Log("pilot-executed")
}
''')
            modules = subprocess.check_output(["go", "env", "GOMODCACHE"], text=True).strip()
            env = {**os.environ, "HOME": str(root / "home"), "GOMODCACHE": modules,
                   "GOPROXY": "off", "GOSUMDB": "off", "GOTELEMETRY": "off",
                   "XDG_CACHE_HOME": str(root / "home/cache"), "GOTOOLCHAIN": "local"}
            env.pop("FIX_PILOT", None)
            self.check_failure_replay_and_fix(["make", "-s", "test-property", "TEST_ARGS=-count=1 -v"], root, env)
            self.assertFalse((root / "home/cache/hegel-go").exists())
            self.assertFalse((root / "home/Library/Caches/hegel-go").exists())


if __name__ == "__main__":
    unittest.main()
