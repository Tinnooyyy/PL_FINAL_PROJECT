"""
Checks that the React front ends share one design.

* The two systems' front ends: the only allowed differences are the system
  name and server URL in src/api.js and the port in vite.config.js. Those
  files are compared after replacing the values with placeholders; every
  other file must be identical.
* The comparison app (system_compare): its copies of the components and the
  stylesheet must be identical to the systems' copies.
"""

import os
import unittest

from shared_cases import PROJECT_ROOT
from system_files import comparable_text, list_files, read_text

# Files the comparison app shares with the system front ends.
SHARED_WITH_COMPARE_APP = [
    "index.html",
    "package.json",
    "package-lock.json",
    os.path.join("src", "labels.js"),
    os.path.join("src", "styles.css"),
    os.path.join("src", "components", "MessageBanner.jsx"),
    os.path.join("src", "components", "TaskForm.jsx"),
    os.path.join("src", "components", "TaskItem.jsx"),
    os.path.join("src", "components", "TaskList.jsx"),
    os.path.join("src", "components", "Toolbar.jsx"),
]


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


class TestCompareAppMatches(unittest.TestCase):
    """system_compare/frontend reuses the systems' components and styles unchanged."""

    def test_same_components_and_styles(self):
        for relative in SHARED_WITH_COMPARE_APP:
            with self.subTest(file=relative):
                self.assertEqual(
                    read_text(os.path.join(PROJECT_ROOT, "system_oop", "frontend", relative)),
                    read_text(os.path.join(PROJECT_ROOT, "system_compare", "frontend",
                                           relative)))


if __name__ == "__main__":
    unittest.main()
