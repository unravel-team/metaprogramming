"""Safety and parity checks for the repository-only Org verifier."""

from contextlib import contextmanager
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_scaffold_contract import IGNORE, ROOT


@contextmanager
def checkout():
    with tempfile.TemporaryDirectory(prefix="org-check-") as directory:
        root = Path(directory)
        (root / "scripts").mkdir()
        script = ROOT / "scripts/check-org-tangle.sh"
        if script.exists():
            shutil.copy2(script, root / "scripts/check-org-tangle.sh")
        for language in ("python", "clojure"):
            shutil.copytree(ROOT / language, root / language, ignore=IGNORE)
        yield root


def check(root, *arguments):
    return subprocess.run(
        ["sh", "scripts/check-org-tangle.sh", *arguments], cwd=root,
        capture_output=True, text=True, timeout=90,
    )


@unittest.skipUnless(shutil.which("emacs"), "Emacs required")
class OrgTangleSafety(unittest.TestCase):
    def test_clean_sources_pass_without_changes(self):
        with checkout() as root:
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            result = check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_drift_fails(self):
        with checkout() as root:
            path = root / "python/Makefile"
            path.write_text(path.read_text() + "\n# drift\n")
            result = check(root, "python")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Makefile", result.stdout + result.stderr)

    def test_unsafe_destinations_fail_without_writing(self):
        for destination in ("../outside", "/tmp/org-check-forbidden", "new-unexpected-output"):
            with self.subTest(destination=destination), checkout() as root:
                path = root / "python/python.org"
                path.write_text(path.read_text().replace(':tangle "Makefile"', f':tangle "{destination}"', 1))
                result = check(root, "python")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("destination", result.stdout + result.stderr)
                self.assertFalse((root / "outside").exists())
                self.assertFalse((root / "python/new-unexpected-output").exists())

    def test_symlink_destination_is_rejected(self):
        with checkout() as root:
            outside = root / "outside"
            outside.write_text("preserve me\n")
            path = root / "python/Makefile"
            path.unlink()
            path.symlink_to(outside)
            result = check(root, "python")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stdout + result.stderr)
            self.assertEqual(outside.read_text(), "preserve me\n")

    def test_local_eval_never_runs(self):
        with checkout() as root:
            path = root / "python/python.org"
            with path.open("a") as stream:
                stream.write('\n# Local Variables:\n# eval: (write-region "oops" nil "EVAL-RAN")\n# End:\n')
            result = check(root, "python")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(list(root.rglob("EVAL-RAN")))

    def test_dynamic_block_headers_are_rejected(self):
        with checkout() as root:
            path = root / "python/python.org"
            path.write_text(path.read_text().replace(':tangle "Makefile"', ':tangle "Makefile" :var x=(shell-command "touch EVAL-RAN")', 1))
            result = check(root, "python")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("header", result.stdout + result.stderr)
            self.assertFalse(list(root.rglob("EVAL-RAN")))
