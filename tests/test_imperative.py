"""Runs the shared test cases against the imperative backend."""

import unittest

from shared_cases import SharedBackendTests  # also puts the project root on sys.path

import backend_imperative.service as imperative_service
from backend_imperative.query_ops import merge_sort


class TestImperativeBackend(SharedBackendTests, unittest.TestCase):
    """The shared cases, with `backend` set to the imperative service module."""

    backend = imperative_service


class TestImperativeSpecificFeatures(unittest.TestCase):
    """Extra checks for features only the imperative version has."""

    def test_merge_sort_sorts_with_the_given_compare_function(self):
        numbers = [5, 3, 9, 1, 3]
        self.assertEqual(merge_sort(numbers, lambda a, b: a - b), [1, 3, 3, 5, 9])
        self.assertEqual(merge_sort(numbers, lambda a, b: b - a), [9, 5, 3, 3, 1])

    def test_merge_sort_does_not_change_its_input(self):
        numbers = [2, 1]
        merge_sort(numbers, lambda a, b: a - b)
        self.assertEqual(numbers, [2, 1])

    def test_errors_are_builtin_exception_types(self):
        with self.assertRaises(KeyError) as context:
            imperative_service.get_task(12345)
        self.assertIs(type(context.exception), KeyError)


if __name__ == "__main__":
    unittest.main()
