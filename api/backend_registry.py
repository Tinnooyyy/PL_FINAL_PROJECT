"""
Knows which backends exist, where each one saves its data, and which HTTP
status code each kind of backend error should become.

There is no task logic here: validation, rules and file handling all live in
the backends.
"""

import os
import sys

# Make the project root importable so `backend_oop` and `backend_imperative`
# can be found when the API is started with `python api/app.py`.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import backend_imperative.service as imperative_service  # noqa: E402
import backend_oop.service as oop_service  # noqa: E402

# The name the front end sends  ->  the backend's service module.
BACKENDS = {
    "oop": oop_service,
    "imperative": imperative_service,
}

# Each backend gets its own save file, so their data never mixes.
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATA_FILES = {
    "oop": os.path.join(DATA_DIR, "tasks_oop.json"),
    "imperative": os.path.join(DATA_DIR, "tasks_imperative.json"),
}


def configure_all_backends():
    """Point every backend at its save file and load it. Returns {name: result}."""
    results = {}
    for name, backend in BACKENDS.items():
        results[name] = backend.configure(DATA_FILES[name])
    return results


def get_backend(name):
    """Return the service module for this name, or None if there is no such backend."""
    return BACKENDS.get(name)


def status_code_for(error):
    """
    Map a backend error to an HTTP status code.

    Both backends raise (subclasses of) these three built-in types; see
    contract/backend_contract.py.
    """
    if isinstance(error, KeyError):
        return 404  # task not found
    if isinstance(error, ValueError):
        return 400  # invalid input
    return 500      # OSError: the save file could not be read or written
