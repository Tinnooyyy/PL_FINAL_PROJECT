"""
Checks that the two systems have the same server, that the comparison app has
no backend of its own, and that no app imports code from another app or from
the contract.
"""

import os
import re
import unittest

from shared_cases import PROJECT_ROOT
from system_files import comparable_text, list_files, read_text

APP_FOLDERS = ["system_oop", "system_imperative", "system_compare"]


class TestServersMatch(unittest.TestCase):
    """Both servers have the same routes and error handling; only name and ports differ."""

    def test_same_server_code(self):
        path = os.path.join("server", "app.py")
        self.assertEqual(comparable_text("system_oop", path),
                         comparable_text("system_imperative", path))

    def test_same_requirements(self):
        self.assertEqual(comparable_text("system_oop", "requirements.txt"),
                         comparable_text("system_imperative", "requirements.txt"))


class TestCompareAppHasNoBackend(unittest.TestCase):
    """system_compare only has a front end; it uses the two systems' servers."""

    def test_no_python_code(self):
        files = list_files(os.path.join(PROJECT_ROOT, "system_compare"))
        self.assertEqual([name for name in files if name.endswith(".py")], [])

    def test_only_a_frontend_folder(self):
        self.assertEqual(sorted(os.listdir(os.path.join(PROJECT_ROOT, "system_compare"))),
                         ["frontend"])


class TestNoSharedImports(unittest.TestCase):
    """An app may only import its own code and installed libraries."""

    def test_no_imports_of_other_apps_or_the_contract(self):
        for app in APP_FOLDERS:
            forbidden = [name for name in APP_FOLDERS if name != app] + ["contract"]
            folder = os.path.join(PROJECT_ROOT, app)
            for relative in list_files(folder):
                if not relative.endswith((".py", ".js", ".jsx")):
                    continue
                text = read_text(os.path.join(folder, relative))
                import_lines = [line for line in text.splitlines()
                                if re.match(r"\s*(import|from)\s", line)]
                with self.subTest(file=os.path.join(app, relative)):
                    for line in import_lines:
                        for name in forbidden:
                            self.assertNotIn(name, line)


if __name__ == "__main__":
    unittest.main()
