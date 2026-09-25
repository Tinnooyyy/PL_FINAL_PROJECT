"""
Runs one long, scripted sequence of calls against both backends and checks
that every result (or error message) is identical.
"""

import os
import tempfile
import unittest

from shared_cases import PROJECT_ROOT  # noqa: F401  (puts the project root on sys.path)

import backend_imperative.service as imperative_service
import backend_oop.service as oop_service

# Each step is (function name, arguments).
SCRIPT = [
    ("add_task", ({"title": "  Buy milk ", "priority": "LOW",
                   "due_date": "2026-10-05 09:00", "category": "Personal"},)),
    ("add_task", ({"title": "Pay rent", "priority": "high", "due_date": "2026-10-01 18:00",
                   "description": "Landlord", "category": "personal"},)),
    ("add_task", ({"title": "Read book", "description": "milk chapter",
                   "category": "academic"},)),
    ("add_task", ({"title": "Plan trip", "priority": "high",
                   "due_date": "2026-10-01 07:30", "category": "work"},)),
    ("add_task", ({"title": "Team call", "due_date": "2026-10-01 18:00",
                   "category": "work"},)),
    ("add_task", ({"title": ""},)),
    ("add_task", ({"title": "x", "due_date": "2026-02-30 10:00", "category": "work"},)),
    ("add_task", ({"title": "x", "due_date": "2026-10-05 25:00", "category": "work"},)),
    ("add_task", ({"title": "x", "due_date": "2026-10-05", "category": "work"},)),
    ("add_task", ({"title": "x", "priority": "high", "category": "work"},)),
    ("add_task", ({"title": "x"},)),
    ("add_task", ({"title": "x", "category": "hobby"},)),
    ("add_task", ({"title": "x", "category": 7},)),
    ("add_task", ({"title": "x", "id": 9},)),
    ("add_task", ("not a dict",)),
    ("add_task", ({"title": None, "status": 3},)),
    ("update_task", (3, {"priority": "high"})),
    ("update_task", (3, {"priority": "high", "due_date": "2026-09-30 23:59"})),
    ("update_task", (3, {"category": "WORK"})),
    ("update_task", (3, {"category": "school"})),
    ("update_task", (3, {"due_date": "2026-09-30"})),
    ("update_task", (99, {"title": "a"})),
    ("update_task", (True, {"title": "a"})),
    ("complete_task", (1,)),
    ("complete_task", (1,)),
    ("delete_task", (42,)),
    ("get_task", ("1",)),
    ("search_tasks", ("MILK",)),
    ("search_tasks", (None,)),
    ("filter_tasks", ("pending", None)),
    ("filter_tasks", (None, "bogus")),
    ("filter_tasks", (None, None, "work")),
    ("filter_tasks", ("pending", "high", "work")),
    ("filter_tasks", (None, None, "hobby")),
    ("sort_tasks", ("due_date", False)),
    ("sort_tasks", ("due_date", "true")),
    ("sort_tasks", ("priority", False)),
    ("sort_tasks", ("priority", True)),
    ("sort_tasks", ("title",)),
    ("sort_tasks", ("priority", 1)),
    ("query_tasks", ("", "pending", "", "", "due_date", "false")),
    ("query_tasks", ("milk", None, None, None, None, False)),
    ("query_tasks", (None, None, None, "work", "due_date", True)),
    ("delete_task", (2,)),
    ("save_tasks", ()),
    ("load_tasks", ()),
    ("get_all_tasks", ()),
    ("get_options", ()),
]


def run_script(backend, data_file):
    """Run SCRIPT on one backend and return a list of results."""
    results = [backend.configure(data_file)]
    for function_name, args in SCRIPT:
        try:
            results.append(getattr(backend, function_name)(*args))
        except (ValueError, KeyError, OSError) as error:
            # Record which built-in family the error belongs to, plus its message.
            for family in (ValueError, KeyError, OSError):
                if isinstance(error, family):
                    results.append(("error", family.__name__, error.args[0]))
                    break
    return results


class TestParity(unittest.TestCase):
    """Both backends must behave identically, step by step."""

    def test_same_script_gives_same_results(self):
        with tempfile.TemporaryDirectory() as oop_dir, \
                tempfile.TemporaryDirectory() as imperative_dir:
            oop_results = run_script(oop_service, os.path.join(oop_dir, "tasks.json"))
            imperative_results = run_script(
                imperative_service, os.path.join(imperative_dir, "tasks.json"))

        self.assertEqual(len(oop_results), len(imperative_results))
        for step, (oop_result, imperative_result) in enumerate(
                zip(oop_results, imperative_results)):
            with self.subTest(step=step):
                self.assertEqual(oop_result, imperative_result)


if __name__ == "__main__":
    unittest.main()
