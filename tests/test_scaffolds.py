from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from scaffold_tools import (  # noqa: E402
    common_target_names,
    find_deprecated_conventions_usage,
    language_names,
    load_manifest,
    parse_help_targets,
    run_make_help,
)


class ScaffoldRepositoryTests(unittest.TestCase):
    def test_manifest_exists_and_lists_all_languages(self) -> None:
        manifest = load_manifest()
        self.assertEqual(
            set(language_names(manifest)),
            {"typescript", "python", "clojure", "golang"},
        )

    def test_ci_workflow_exists(self) -> None:
        self.assertTrue((ROOT / ".github" / "workflows" / "scaffolds.yml").exists())

    def test_each_language_has_canonical_docs(self) -> None:
        manifest = load_manifest()
        for language in language_names(manifest):
            with self.subTest(language=language):
                base = ROOT / manifest["languages"][language]["path"]
                self.assertTrue((base / "README.md").exists())
                self.assertTrue((base / "AGENTS.md").exists())
                self.assertTrue((base / "Makefile").exists())

    def test_manifest_files_exist(self) -> None:
        manifest = load_manifest()
        for language in language_names(manifest):
            metadata = manifest["languages"][language]
            base = ROOT / metadata["path"]
            for rel_path in metadata["supportFiles"] + metadata["sampleFiles"]:
                with self.subTest(language=language, path=rel_path):
                    self.assertTrue((base / rel_path).exists())

    def test_common_make_targets_exist_in_every_scaffold(self) -> None:
        manifest = load_manifest()
        common_targets = set(common_target_names(manifest))
        for language in language_names(manifest):
            with self.subTest(language=language):
                base = ROOT / manifest["languages"][language]["path"]
                targets = parse_help_targets(run_make_help(base))
                self.assertTrue(
                    common_targets.issubset(targets),
                    f"missing common targets in {language}: {sorted(common_targets - set(targets))}",
                )

    def test_repo_does_not_use_deprecated_conventions_doc(self) -> None:
        offenders = find_deprecated_conventions_usage()
        self.assertEqual(offenders, [], f"found deprecated doc usage: {offenders}")

    def test_generated_docs_are_current(self) -> None:
        script = ROOT / "scripts" / "render_scaffold_docs.py"
        subprocess.check_call(["python3", str(script), "--check"], cwd=ROOT)


if __name__ == "__main__":
    unittest.main()
