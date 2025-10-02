import unittest

from src.bayescalc.lexer import Lexer
from src.bayescalc.parser import Parser
from src.bayescalc.queries import QueryParser
from src.bayescalc.commands import CommandHandler


class TestBooleanSyntax(unittest.TestCase):
    def setUp(self):
        # Define a simple Bayesian network with Boolean variables
        network_str = """
        variable Rain
        variable Sprinkler
        variable GrassWet

        Rain {
            P(True) = 0.2
        }

        Sprinkler | Rain {
            P(True | True) = 0.01
            P(True | False) = 0.4
        }

        GrassWet | Rain, Sprinkler {
            P(True | True, True) = 0.99
            P(True | True, False) = 0.8
            P(True | False, True) = 0.9
            P(True | False, False) = 0.1
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        self.network = parser.parse()
        self.query_parser = QueryParser(self.network)
        self.command_handler = CommandHandler(self.network)

    def test_boolean_variable_declaration(self):
        """Test that variables are correctly recognized as Boolean."""
        for name in ["Rain", "Sprinkler", "GrassWet"]:
            var = self.network.variables[name]
            self.assertTrue(var.is_boolean)
            self.assertEqual(var.var_type, "Boolean")
            self.assertEqual(var.domain, ("True", "False"))

    def test_boolean_shorthand_queries(self):
        """Test that P(Var) is equivalent to P(Var=True)."""
        # P(Rain) should return P(Rain=True) = 0.2
        result_shorthand = self.query_parser.parse_and_execute("P(Rain)")
        result_explicit = self.query_parser.parse_and_execute("P(Rain=True)")
        self.assertEqual(result_shorthand.probabilities, result_explicit.probabilities)
        self.assertEqual(result_shorthand.probabilities[tuple()], 0.2)

    def test_boolean_negation(self):
        """Test that P(~Var) is equivalent to P(Var=False)."""
        # P(~Rain) should return P(Rain=False) = 0.8
        result_negation = self.query_parser.parse_and_execute("P(~Rain)")
        result_explicit = self.query_parser.parse_and_execute("P(Rain=False)")
        self.assertEqual(result_negation.probabilities, result_explicit.probabilities)
        self.assertEqual(result_negation.probabilities[tuple()], 0.8)

    def test_conditional_boolean_queries(self):
        """Test conditionals with boolean shorthand syntax."""
        # P(Rain | GrassWet) should be equal to P(Rain=True | GrassWet=True)
        result_shorthand = self.query_parser.parse_and_execute("P(Rain | GrassWet)")
        result_explicit = self.query_parser.parse_and_execute(
            "P(Rain=True | GrassWet=True)"
        )
        self.assertEqual(result_shorthand.probabilities, result_explicit.probabilities)

    def test_conditional_negation(self):
        """Test conditionals with negation syntax."""
        # P(Rain | ~GrassWet) should be equal to P(Rain=True | GrassWet=False)
        result_negation = self.query_parser.parse_and_execute("P(Rain | ~GrassWet)")
        result_explicit = self.query_parser.parse_and_execute(
            "P(Rain=True | GrassWet=False)"
        )
        self.assertEqual(result_negation.probabilities, result_explicit.probabilities)

    def test_ls_command_shows_type(self):
        """Test that the 'ls' command shows variable types."""
        result = self.command_handler.execute("ls")
        self.assertIn("Boolean", result)
        self.assertIn("Rain", result)
        self.assertIn("Sprinkler", result)
        self.assertIn("GrassWet", result)


if __name__ == "__main__":
    unittest.main()
