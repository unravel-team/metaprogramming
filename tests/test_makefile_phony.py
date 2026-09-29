"""Keep action targets and their PHONY declarations together."""
import re
import unittest

from test_scaffold_contract import LANGUAGES, ROOT, run, scaffold


class AdjacentPhony(unittest.TestCase):
    def test_each_action_rule_has_its_own_adjacent_declaration(self):
        for language in LANGUAGES:
            lines = (ROOT / language / "Makefile").read_text().splitlines()
            declarations = 0
            rules = 0
            for index, line in enumerate(lines):
                if line.startswith(".PHONY:"):
                    declarations += 1
                match = re.match(r"^([A-Za-z][\w-]*(?: [A-Za-z][\w-]*)*):(?:\s|$)", line)
                if match:
                    rules += 1
                    with self.subTest(language=language, target=match[1]):
                        self.assertGreater(index, 0)
                        self.assertEqual(lines[index - 1], f".PHONY: {match[1]}")
            self.assertGreater(rules, 0)
            self.assertEqual(declarations, rules, language)

    def test_existing_help_file_does_not_suppress_action(self):
        for language in LANGUAGES:
            with self.subTest(language=language), scaffold(language) as root:
                (root / "help").write_text("ordinary file, not a build artifact\n")
                result = run(["make", "-s", "help"], root)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Show scaffold workflow targets", result.stdout)


if __name__ == "__main__":
    unittest.main()
