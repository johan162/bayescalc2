"""
Test error handling in the Bayesian network calculator.
This file contains tests for various error conditions.
"""

import unittest
import sys
import os

# Add src to path to allow importing bayescalc modules
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from bayescalc.network_model import BayesianNetwork
from bayescalc.lexer import Lexer
from bayescalc.inference import Inference
from bayescalc.queries import QueryParser
from tests.test_utils import parse_string


class TestErrorHandling(unittest.TestCase):

    def test_lexer_errors(self):
        """Test error handling in the lexer."""

        # Test invalid token
        lexer = Lexer("variable A { @#$ }")
        with self.assertRaises(Exception):
            while lexer.peek() is not None:
                lexer.next()

        # Test unclosed string
        lexer = Lexer('variable A { "unclosed string }')
        with self.assertRaises(Exception):
            while lexer.peek() is not None:
                lexer.next()

    def test_parser_errors(self):
        """Test error handling in the parser."""

        # Test syntax errors in variable declaration
        with self.assertRaises(Exception):
            parse_string(
                """
            variable {True, False}  # Missing variable name
            """
            )

        # Test invalid domain format
        with self.assertRaises(Exception):
            parse_string(
                """
            variable A True, False  # Missing curly braces
            """
            )

        # Test missing probability declaration
        with self.assertRaises(Exception):
            parse_string(
                """
            boolean A

            A {
                # No probability statements
            }
            """
            )

    def test_query_syntax_errors(self):
        """Test error handling for query syntax errors."""

        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))
        network.add_variable("B", ("True", "False"))
        network.add_factor("A", [], {("True",): 0.5, ("False",): 0.5})
        network.add_factor(
            "B",
            ["A"],
            {
                ("True", "True"): 0.8,
                ("False", "True"): 0.2,
                ("True", "False"): 0.3,
                ("False", "False"): 0.7,
            },
        )

        query_parser = QueryParser(network)

        # Test completely malformed query
        with self.assertRaises(Exception):
            query_parser.parse_and_execute("This is not a valid query")

        # Test missing variable in query
        with self.assertRaises(Exception):
            query_parser.parse_and_execute("P( | B=True)")

        # Test invalid variable name
        with self.assertRaises(Exception):
            query_parser.parse_and_execute("P(NonExistent=True)")

        # Test invalid value for variable
        with self.assertRaises(Exception):
            query_parser.parse_and_execute("P(A=InvalidValue)")

        # Test missing equals in condition
        with self.assertRaises(Exception):
            query_parser.parse_and_execute("P(A=True | B True)")

    def test_missing_variable_errors(self):
        """Test error handling when referencing non-existent variables."""

        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))

        # Add a valid factor first
        network.add_factor("A", [], {("True",): 0.5, ("False",): 0.5})

        # Try inference with non-existent query variables
        inference = Inference(network)
        try:
            inference.variable_elimination({"NonExistent": None}, {})
            self.fail(
                "Should have raised an exception for non-existent query variables"
            )
        except Exception:
            pass  # Expected exception


if __name__ == "__main__":
    unittest.main()
