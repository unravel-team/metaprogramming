from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from render_scaffold_docs import expected_documents  # noqa: E402
from scaffold_tools import (  # noqa: E402
    common_target_names,
    find_deprecated_conventions_usage,
    iter_scaffolds,
    language_names,
    load_manifest,
    parse_help_targets,
    required_doc_paths,
    required_scaffold_paths,
    run_make_help,
    stale_paths,
    workflow_path,
)

MANIFEST = load_manifest()


class ScaffoldRepositoryTests(unittest.TestCase):
    def test_manifest_exists_and_lists_all_languages(self) -> None:
        self.assertEqual(
            set(language_names(MANIFEST)),
            {"typescript", "python", "clojure", "golang"},
        )

    def test_ci_workflow_exists(self) -> None:
        self.assertTrue(workflow_path().exists())

    def test_scaffold_directories_exist(self) -> None:
        for language, _, base in iter_scaffolds(MANIFEST):
            with self.subTest(language=language):
                self.assertTrue(base.exists())

    def test_canonical_docs_exist(self) -> None:
        for path in required_doc_paths(MANIFEST):
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.exists())

    def test_manifest_files_exist(self) -> None:
        for path in required_scaffold_paths(MANIFEST):
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.exists())

    def test_common_make_targets_exist_in_every_scaffold(self) -> None:
        common_targets = set(common_target_names(MANIFEST))
        for language, _, base in iter_scaffolds(MANIFEST):
            with self.subTest(language=language):
                targets = parse_help_targets(run_make_help(base))
                self.assertTrue(
                    common_targets.issubset(targets),
                    f"missing common targets in {language}: {sorted(common_targets - set(targets))}",
                )

    def test_repo_does_not_use_deprecated_conventions_doc(self) -> None:
        offenders = find_deprecated_conventions_usage(MANIFEST)
        self.assertEqual(offenders, [], f"found deprecated doc usage: {offenders}")

    def test_generated_docs_are_current(self) -> None:
        self.assertEqual(stale_paths(expected_documents(MANIFEST)), [])


if __name__ == "__main__":
    unittest.main()
