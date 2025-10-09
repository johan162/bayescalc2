"""
Tests for the boolean keyword functionality.
"""

import unittest
import sys
import os
import warnings


class TestBooleanKeyword(unittest.TestCase):
    """
    Test the boolean keyword for declaring boolean variables.
    """

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        sys.path.insert(
            0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        )

    def test_boolean_keyword_simple(self):
        """Test basic boolean keyword usage."""
        from bayescalc.lexer import Lexer, TokenType
        from bayescalc.parser import Parser

        net_str = """
        boolean Sick
        boolean Test

        Sick { P(True) = 0.1 }
        Test | Sick {
            P(True | True) = 0.9
            P(True | False) = 0.2
        }
        """

        lexer = Lexer(net_str)
        tokens = lexer.tokenize()

        # Check that BOOLEAN tokens are generated
        boolean_tokens = [t for t in tokens if t.type == TokenType.BOOLEAN]
        self.assertEqual(len(boolean_tokens), 2)

        parser = Parser(tokens)
        network = parser.parse()

        # Verify variables are boolean
        self.assertIn("Sick", network.variables)
        self.assertIn("Test", network.variables)
        self.assertTrue(network.variables["Sick"].is_boolean)
        self.assertTrue(network.variables["Test"].is_boolean)
        self.assertEqual(network.variables["Sick"].domain, ("True", "False"))
        self.assertEqual(network.variables["Test"].domain, ("True", "False"))

    def test_boolean_keyword_with_regular_variables(self):
        """Test mixing boolean keyword with regular variables."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        net_str = """
        boolean Rain
        variable Weather {Sunny, Cloudy, Rainy}
        boolean Umbrella

        Rain { P(True) = 0.3 }
        Weather {
            P(Sunny) = 0.5
            P(Cloudy) = 0.3
        }
        Umbrella | Rain {
            P(True | True) = 0.9
            P(True | False) = 0.1
        }
        """

        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        # Verify boolean variables
        self.assertTrue(network.variables["Rain"].is_boolean)
        self.assertTrue(network.variables["Umbrella"].is_boolean)

        # Verify non-boolean variable
        self.assertFalse(network.variables["Weather"].is_boolean)
        self.assertEqual(
            network.variables["Weather"].domain, ("Sunny", "Cloudy", "Rainy")
        )

    def test_deprecation_warning_explicit_true_false(self):
        """Test that explicit {True, False} triggers deprecation warning."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        net_str = """
        variable Sick {True, False}

        Sick { P(True) = 0.1 }
        """

        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            network = parser.parse()

            # Verify warning was issued
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("Sick", str(w[0].message))
            self.assertIn("boolean Sick", str(w[0].message))
            self.assertIn("explicit {True, False}", str(w[0].message))

        # But the network should still parse correctly
        self.assertIn("Sick", network.variables)
        self.assertTrue(network.variables["Sick"].is_boolean)

    def test_deprecation_warning_multiple_variables(self):
        """Test deprecation warnings for multiple explicit {True, False} declarations."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        net_str = """
        variable Sick {True, False}
        variable Test {True, False}
        variable Result { Positive, Negative }

        Sick { P(True) = 0.1 }
        Test | Sick {
            P(True | True) = 0.9
            P(True | False) = 0.2
        }
        Result | Test {
            P(Positive | True) = 0.95
            P(Positive | False) = 0.05
        }
        """

        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = parser.parse()

            # Should have 2 warnings (for Sick and Test, not Result)
            self.assertEqual(len(w), 2)
            warning_messages = [str(warning.message) for warning in w]
            self.assertTrue(any("Sick" in msg for msg in warning_messages))
            self.assertTrue(any("Test" in msg for msg in warning_messages))
            self.assertFalse(any("Result" in msg for msg in warning_messages))

    def test_no_warning_for_other_domains(self):
        """Test that non-boolean explicit domains don't trigger warnings."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        net_str = """
        variable Weather {Sunny, Rainy}
        variable Temperature {Hot, Cold}

        Weather { P(Sunny) = 0.7 }
        Temperature { P(Hot) = 0.5 }
        """

        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = parser.parse()

            # Should have no warnings
            self.assertEqual(len(w), 0)

    def test_boolean_keyword_preserves_functionality(self):
        """Test that boolean keyword produces same functionality as old syntax."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser
        from bayescalc.queries import QueryParser

        # Network with boolean keyword
        net_str_boolean = """
        boolean Rain
        boolean Sprinkler

        Rain { P(True) = 0.2 }
        Sprinkler | Rain {
            P(True | True) = 0.01
            P(True | False) = 0.4
        }
        """

        # Equivalent network with old syntax (should warn but work)
        net_str_old = """
        variable Rain {True, False}
        variable Sprinkler {True, False}

        Rain { P(True) = 0.2 }
        Sprinkler | Rain {
            P(True | True) = 0.01
            P(True | False) = 0.4
        }
        """

        # Parse both networks
        lexer1 = Lexer(net_str_boolean)
        tokens1 = lexer1.tokenize()
        parser1 = Parser(tokens1)
        network1 = parser1.parse()

        lexer2 = Lexer(net_str_old)
        tokens2 = lexer2.tokenize()
        parser2 = Parser(tokens2)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            network2 = parser2.parse()

        # Both should have same structure
        self.assertEqual(set(network1.variables.keys()), set(network2.variables.keys()))
        self.assertEqual(
            network1.variables["Rain"].domain, network2.variables["Rain"].domain
        )
        self.assertEqual(
            network1.variables["Sprinkler"].domain,
            network2.variables["Sprinkler"].domain,
        )

        # Both should give same query results
        qp1 = QueryParser(network1)
        qp2 = QueryParser(network2)

        result1 = qp1.parse_and_execute("P(Rain=True)")
        result2 = qp2.parse_and_execute("P(Rain=True)")

        self.assertAlmostEqual(
            list(result1.probabilities.values())[0],
            list(result2.probabilities.values())[0],
            places=6,
        )

    def test_boolean_keyword_case_sensitive(self):
        """Test that boolean keyword is case-sensitive."""
        from bayescalc.lexer import Lexer, TokenType

        # Lowercase 'boolean' should work
        net_str = "boolean Test"
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.BOOLEAN)

        # Uppercase 'Boolean' should be treated as identifier
        net_str = "Boolean Test"
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "Boolean")

    def test_lexer_boolean_token_generation(self):
        """Test that lexer correctly generates BOOLEAN tokens."""
        from bayescalc.lexer import Lexer, TokenType

        net_str = """
        boolean Sick
        variable Test {Positive, Negative}
        boolean Fever
        """

        lexer = Lexer(net_str)
        tokens = lexer.tokenize()

        # Filter out newline tokens
        tokens = [t for t in tokens if t.type != TokenType.NEWLINE]

        # Check token sequence
        self.assertEqual(tokens[0].type, TokenType.BOOLEAN)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "Sick")

        self.assertEqual(tokens[2].type, TokenType.VARIABLE)

        # Find the second boolean token
        boolean_tokens = [t for t in tokens if t.type == TokenType.BOOLEAN]
        self.assertEqual(len(boolean_tokens), 2)
        self.assertEqual(boolean_tokens[1].value, "boolean")

    def test_parser_boolean_declaration_method(self):
        """Test the _parse_boolean_declaration method directly."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        net_str = "boolean TestVar"

        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        # Check that variable was added correctly
        self.assertIn("TestVar", network.variables)
        self.assertEqual(network.variables["TestVar"].domain, ("True", "False"))
        self.assertTrue(network.variables["TestVar"].is_boolean)


if __name__ == "__main__":
    unittest.main()
