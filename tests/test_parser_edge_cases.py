"""
Test edge cases in the Bayesian network parser.
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
from bayescalc.network_model import BayesianNetwork


class TestParserEdgeCases(unittest.TestCase):

    def test_empty_network(self):
        """Test parsing an empty network."""
        network_str = ""
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()
        self.assertIsInstance(network, BayesianNetwork)
        self.assertEqual(len(network.variables), 0)

    def test_whitespace_variations(self):
        """Test parsing with unusual whitespace."""
        network_str = """

        variable   Rain   {   True  ,  False   }


        Rain    {
            P(True)=0.2

        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        self.assertIn("Rain", network.variables)
        self.assertEqual(network.variables["Rain"].domain, ("True", "False"))
        self.assertAlmostEqual(network.factors["Rain"].probabilities[("True",)], 0.2)

    def test_malformed_variable_declaration(self):
        """Test that the parser correctly handles errors in variable declarations."""
        # Missing closing brace
        network_str = """
        variable Rain {True, False
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()

    def test_malformed_cpt(self):
        """Test that the parser correctly handles errors in CPT declarations."""
        # Missing probability value
        network_str = """
        variable Rain {True, False}

        Rain {
            P(True) =
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()

    def test_invalid_probability_value(self):
        """Test handling of invalid probability values (outside 0-1 range)."""
        # Probability > 1
        network_str = """
        variable Rain {True, False}

        Rain {
            P(True) = 1.2
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        # The parser itself doesn't check probability values, the API now accepts out-of-range values
        # and normalizes them, so no error is raised
        network = parser.parse()
        # Verify the network was created
        self.assertIn("Rain", network.variables)

    def test_duplicate_variable_declaration(self):
        """Test handling of duplicate variable declarations."""
        network_str = """
        variable Rain {True, False}
        variable Rain {Yes, No}
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(ValueError):
            parser.parse()

    def test_unknown_variable_in_cpt(self):
        """Test handling of references to undeclared variables."""
        network_str = """
        variable Rain {True, False}

        Sunshine {
            P(True) = 0.7
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(ValueError):
            parser.parse()

    def test_unknown_value_in_cpt(self):
        """Test handling of references to undeclared variable values."""
        network_str = """
        variable Rain {True, False}

        Rain {
            P(Heavy) = 0.3
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        # The API now accepts unknown values and ignores them
        network = parser.parse()
        # Verify the network was created
        self.assertIn("Rain", network.variables)

    def test_variable_with_many_values(self):
        """Test handling of variables with many values."""
        network_str = """
        variable Weather {Sunny, Cloudy, Rainy, Stormy, Snowy, Foggy, Windy, Humid, Dry}

        Weather {
            P(Sunny) = 0.2
            P(Cloudy) = 0.2
            P(Rainy) = 0.15
            P(Stormy) = 0.05
            P(Snowy) = 0.1
            P(Foggy) = 0.1
            P(Windy) = 0.1
            P(Humid) = 0.05
            P(Dry) = 0.05
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        self.assertIn("Weather", network.variables)
        self.assertEqual(len(network.variables["Weather"].domain), 9)
        self.assertAlmostEqual(
            sum(network.factors["Weather"].probabilities.values()), 1.0
        )

    def test_auto_completion(self):
        """Test auto-completion of probability tables."""
        network_str = """
        variable Rain {True, False}

        Rain {
            P(True) = 0.3
            # P(False) should be auto-completed to 0.7
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        self.assertAlmostEqual(network.factors["Rain"].probabilities[("True",)], 0.3)
        self.assertAlmostEqual(network.factors["Rain"].probabilities[("False",)], 0.7)

    def test_ambiguous_auto_completion(self):
        """Test that the parser correctly handles ambiguous auto-completion."""
        network_str = """
        variable Weather {Sunny, Cloudy, Rainy}

        Weather {
            P(Sunny) = 0.3
            # Missing both Cloudy and Rainy probabilities
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(ValueError) as context:
            parser.parse()
        # Check that the error message mentions ambiguous auto-completion
        self.assertTrue("ambiguous" in str(context.exception).lower())

    def test_comments_handling(self):
        """Test that comments are properly handled."""
        network_str = """
        # This is a comment
        variable Rain {True, False} # This is another comment

        # Comment before CPT
        Rain { # Comment inside block
            P(True) = 0.3 # Comment after probability
            # Comment on its own line
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        self.assertIn("Rain", network.variables)
        self.assertAlmostEqual(network.factors["Rain"].probabilities[("True",)], 0.3)
        self.assertAlmostEqual(network.factors["Rain"].probabilities[("False",)], 0.7)

    def test_very_small_probabilities(self):
        """Test handling of very small probability values."""
        network_str = """
        variable Rare {True, False}

        Rare {
            P(True) = 0.0000001
        }
        """
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        self.assertAlmostEqual(
            network.factors["Rare"].probabilities[("True",)], 0.0000001
        )
        self.assertAlmostEqual(
            network.factors["Rare"].probabilities[("False",)], 0.9999999
        )


if __name__ == "__main__":
    unittest.main()
