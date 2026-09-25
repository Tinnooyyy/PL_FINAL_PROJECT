"""
Checks that the two systems' React front ends are the same.

The only allowed differences are the system name and server URL in
src/api.js and the port in vite.config.js. Those files are compared after
replacing the values with placeholders; every other file must be identical.
"""

import os
import unittest

from shared_cases import PROJECT_ROOT
from system_files import comparable_text, list_files


class TestFrontEndsMatch(unittest.TestCase):
    """system_oop/frontend and system_imperative/frontend must not drift apart."""

    def test_same_files(self):
        oop_files = list_files(os.path.join(PROJECT_ROOT, "system_oop", "frontend"))
        imperative_files = list_files(
            os.path.join(PROJECT_ROOT, "system_imperative", "frontend"))
        self.assertEqual(oop_files, imperative_files)

    def test_same_content(self):
        for relative in list_files(os.path.join(PROJECT_ROOT, "system_oop", "frontend")):
            path = os.path.join("frontend", relative)
            with self.subTest(file=path):
                self.assertEqual(comparable_text("system_oop", path),
                                 comparable_text("system_imperative", path))


if __name__ == "__main__":
    unittest.main()
