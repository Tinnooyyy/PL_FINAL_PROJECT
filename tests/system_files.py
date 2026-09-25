"""
Helpers for comparing files between the system folders
(used by test_frontends_match.py and test_systems_independent.py).
"""

import os

from shared_cases import PROJECT_ROOT

# The values that are ALLOWED to differ between the two systems, and the
# placeholder each one is replaced with before comparing.
SYSTEM_VALUES = {
    "system_oop": {
        "system_oop": "<system folder>",
        "OOP System": "<system name>",
        "5001": "<server port>",
        "5173": "<front end port>",
    },
    "system_imperative": {
        "system_imperative": "<system folder>",
        "Imperative System": "<system name>",
        "5002": "<server port>",
        "5174": "<front end port>",
    },
}

# Files (relative to a system folder) that may contain the values above.
FILES_WITH_ALLOWED_DIFFERENCES = {
    os.path.join("frontend", "src", "api.js"),
    os.path.join("frontend", "vite.config.js"),
    os.path.join("server", "app.py"),
}

SKIPPED_FOLDERS = {"node_modules", "dist", "__pycache__"}


def list_files(folder):
    """Return every file path under `folder`, relative to it, skipping build output."""
    found = []
    for current, subfolders, files in os.walk(folder):
        subfolders[:] = [name for name in subfolders if name not in SKIPPED_FOLDERS]
        for name in files:
            found.append(os.path.relpath(os.path.join(current, name), folder))
    return sorted(found)


def read_text(path):
    """Read a text file, ignoring Windows/Unix line-ending differences."""
    with open(path, encoding="utf-8") as file:
        return file.read().replace("\r\n", "\n")


def comparable_text(system, relative_path):
    """
    Return a system file's text, ready to compare with the other system.

    Files that are allowed to differ get their system-specific values
    replaced with placeholders; all other files are returned unchanged.
    """
    text = read_text(os.path.join(PROJECT_ROOT, system, relative_path))
    if relative_path in FILES_WITH_ALLOWED_DIFFERENCES:
        for value, placeholder in SYSTEM_VALUES[system].items():
            text = text.replace(value, placeholder)
    return text
