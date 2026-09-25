"""Runs the shared test cases against the object-oriented backend."""

import unittest

from shared_cases import SharedBackendTests  # also puts the project root on sys.path

import backend_oop.service as oop_service
from backend_oop.exceptions import (
    TaskNotFoundError,
    TaskStorageError,
    TaskValidationError,
)
from backend_oop.task import Task, UrgentTask, create_task


class TestOOPBackend(SharedBackendTests, unittest.TestCase):
    """The shared cases, with `backend` set to the OOP service module."""

    backend = oop_service


class TestOOPSpecificFeatures(unittest.TestCase):
    """Extra checks for features only the OOP version has (classes, custom exceptions)."""

    def test_high_priority_creates_an_urgent_task(self):
        task = create_task(1, {"title": "A", "priority": "high", "due_date": "2026-10-01"})
        self.assertIsInstance(task, UrgentTask)
        self.assertIsInstance(task, Task)  # an UrgentTask IS a Task (inheritance)

    def test_other_priorities_create_a_plain_task(self):
        task = create_task(1, {"title": "A", "priority": "low"})
        self.assertIs(type(task), Task)

    def test_properties_are_read_only(self):
        task = create_task(1, {"title": "A"})
        with self.assertRaises(AttributeError):
            task.title = "B"

    def test_custom_exceptions_are_raised(self):
        with self.assertRaises(TaskValidationError):
            create_task(1, {"title": ""})
        with self.assertRaises(TaskNotFoundError):
            oop_service.get_task(12345)

    def test_custom_exceptions_inherit_from_builtin_types(self):
        self.assertTrue(issubclass(TaskValidationError, ValueError))
        self.assertTrue(issubclass(TaskNotFoundError, KeyError))
        self.assertTrue(issubclass(TaskStorageError, OSError))


if __name__ == "__main__":
    unittest.main()
