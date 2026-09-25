"""Checks that both backends expose exactly the functions defined in the contract."""

import inspect
import unittest

from shared_cases import PROJECT_ROOT  # noqa: F401  (puts the project root on sys.path)

import system_imperative.backend.service as imperative_service
import system_oop.backend.service as oop_service
from contract.backend_contract import CONTRACT

BACKENDS = {"oop": oop_service, "imperative": imperative_service}


class TestContract(unittest.TestCase):
    """Every contract function must exist with the exact same parameters."""

    def test_every_contract_function_exists(self):
        for backend_name, backend in BACKENDS.items():
            for function_name in CONTRACT:
                with self.subTest(backend=backend_name, function=function_name):
                    self.assertTrue(callable(getattr(backend, function_name, None)))

    def test_parameters_match_the_contract(self):
        for backend_name, backend in BACKENDS.items():
            for function_name, expected in CONTRACT.items():
                with self.subTest(backend=backend_name, function=function_name):
                    actual = str(inspect.signature(getattr(backend, function_name)))
                    self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
