"""Native Clojure version tasks remain metadata-only and safe to tangle."""
import shutil
import unittest

from test_scaffold_contract import ROOT, run, scaffold


class ClojureVersionRouting(unittest.TestCase):
    def test_shell_version_implementation_removed(self):
        self.assertFalse((ROOT / "clojure/scripts/release.sh").exists())
        makefile = (ROOT / "clojure/Makefile").read_text()
        self.assertNotIn("VERSION_SCRIPT", makefile)
        self.assertNotIn("scripts/release.sh", (ROOT / "clojure/clojure.org").read_text())
        for task in ("version", "major", "minor", "patch"):
            self.assertIn(f"@$(CLOJURE) -T:build {task}\n", makefile)
        self.assertEqual(makefile.count("version=$$($(CLOJURE) -T:build version)"), 2)


@unittest.skipUnless(shutil.which("clojure"), "Clojure required")
class ClojureVersionTasks(unittest.TestCase):
    def test_native_tasks_reset_components_and_only_change_version(self):
        with scaffold("clojure") as root:
            (root / "VERSION").write_text("2.3.9\n")
            original = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            for task, expected in (("version", "2.3.9"), ("patch", "2.3.10"),
                                   ("minor", "2.4.0"), ("major", "3.0.0")):
                result = run(["clojure", "-Srepro", "-T:build", task], root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stdout, expected + "\n")
                self.assertEqual((root / "VERSION").read_text(), expected + "\n")
            for path, content in original.items():
                if str(path) != "VERSION":
                    self.assertEqual((root / path).read_bytes(), content, str(path))
            self.assertFalse((root / "target").exists(), "Version operation built an artifact")
            artifact = run(["clojure", "-Srepro", "-T:build", "artifact-path"], root)
            self.assertEqual(artifact.returncode, 0, artifact.stderr)
            self.assertEqual(artifact.stdout, "target/clojure-scaffold-3.0.0.jar\n")

    def test_invalid_metadata_fails_without_modification(self):
        with scaffold("clojure") as root:
            for value in ("1.2\n", "1.2.3-SNAPSHOT\n", "1. 2.3\n"):
                (root / "VERSION").write_text(value)
                for task in ("version", "major", "minor", "patch"):
                    with self.subTest(value=value, task=task):
                        result = run(["clojure", "-Srepro", "-T:build", task], root)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("VERSION must contain plain semantic version", result.stderr)
                        self.assertEqual((root / "VERSION").read_text(), value)

    def test_make_major_uses_native_task(self):
        with scaffold("clojure") as root:
            (root / "VERSION").write_text("4.8.12\n")
            result = run(["make", "-s", "major"], root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "5.0.0\n")
            self.assertFalse((root / "target").exists())


if __name__ == "__main__":
    unittest.main()
