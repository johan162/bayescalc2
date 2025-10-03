"""
Test for boolean shorthand notation (T/F) support.
"""

import unittest
import sys
import os

# Add src to path to allow importing bayescalc modules
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.queries import QueryParser
from bayescalc.network_model import BayesianNetwork


class TestBooleanShorthandSyntax(unittest.TestCase):

    def test_boolean_shorthand_in_net_file(self):
        """Test that T/F shorthand works in network definitions."""
        network_str = """
        boolean Rain
        boolean Sprinkler

        Rain {
            P(T) = 0.2
        }

        Sprinkler | Rain {
            P(T | T) = 0.01
            P(T | F) = 0.4
        }
        """

        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        # Check that the network was parsed correctly
        self.assertIn("Rain", network.variables)
        self.assertIn("Sprinkler", network.variables)

        # Check that Rain is a boolean variable
        self.assertTrue(network.variables["Rain"].is_boolean)

        # Check that the CPT entries were parsed correctly
        rain_factor = network.factors["Rain"]
        self.assertAlmostEqual(rain_factor.probabilities[("True",)], 0.2)
        self.assertAlmostEqual(rain_factor.probabilities[("False",)], 0.8)

        sprinkler_factor = network.factors["Sprinkler"]
        self.assertAlmostEqual(sprinkler_factor.probabilities[("True", "True")], 0.01)
        self.assertAlmostEqual(sprinkler_factor.probabilities[("False", "True")], 0.99)
        self.assertAlmostEqual(sprinkler_factor.probabilities[("True", "False")], 0.4)
        self.assertAlmostEqual(sprinkler_factor.probabilities[("False", "False")], 0.6)

    def test_boolean_shorthand_in_queries(self):
        """Test that T/F shorthand works in queries."""
        # First create a simple network
        network = BayesianNetwork()
        network.add_variable("Sick", ("True", "False"))
        network.add_variable("Test", ("True", "False"))

        # Add CPT entries
        sick_cpt = {("True",): 0.01, ("False",): 0.99}
        network.add_factor("Sick", [], sick_cpt)

        test_cpt = {
            ("True", "True"): 0.95,
            ("False", "True"): 0.05,
            ("True", "False"): 0.06,
            ("False", "False"): 0.94,
        }
        network.add_factor("Test", ["Sick"], test_cpt)

        # Create a query parser
        query_parser = QueryParser(network)

        # Test queries with T/F shorthand
        result1 = query_parser.parse_and_execute("P(Sick=T|Test=T)")
        result2 = query_parser.parse_and_execute("P(Sick=True|Test=True)")

        # Both queries should give the same result
        for key1, prob1 in result1.probabilities.items():
            for key2, prob2 in result2.probabilities.items():
                self.assertAlmostEqual(prob1, prob2)

        # Test simple form for boolean variables
        result3 = query_parser.parse_and_execute("P(Sick|Test=T)")
        for key1, prob1 in result1.probabilities.items():
            for key3, prob3 in result3.probabilities.items():
                self.assertAlmostEqual(prob1, prob3)


if __name__ == "__main__":
    unittest.main()
