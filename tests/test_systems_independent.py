"""
Checks that the two systems have the same server, and that no system imports
code from another system or from the contract.
"""

import os
import re
import unittest

from shared_cases import PROJECT_ROOT
from system_files import comparable_text, list_files, read_text

SYSTEM_FOLDERS = ["system_oop", "system_imperative"]


class TestServersMatch(unittest.TestCase):
    """Both servers have the same routes and error handling; only name and ports differ."""

    def test_same_server_code(self):
        path = os.path.join("server", "app.py")
        self.assertEqual(comparable_text("system_oop", path),
                         comparable_text("system_imperative", path))

    def test_same_requirements(self):
        self.assertEqual(comparable_text("system_oop", "requirements.txt"),
                         comparable_text("system_imperative", "requirements.txt"))


class TestNoSharedImports(unittest.TestCase):
    """A system may only import its own code and installed libraries."""

    def test_no_imports_of_other_systems_or_the_contract(self):
        for system in SYSTEM_FOLDERS:
            forbidden = [name for name in SYSTEM_FOLDERS if name != system] + ["contract"]
            folder = os.path.join(PROJECT_ROOT, system)
            for relative in list_files(folder):
                if not relative.endswith((".py", ".js", ".jsx")):
                    continue
                text = read_text(os.path.join(folder, relative))
                import_lines = [line for line in text.splitlines()
                                if re.match(r"\s*(import|from)\s", line)]
                with self.subTest(file=os.path.join(system, relative)):
                    for line in import_lines:
                        for name in forbidden:
                            self.assertNotIn(name, line)


if __name__ == "__main__":
    unittest.main()
