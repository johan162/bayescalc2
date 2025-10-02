"""
Tests for the lexer and parser modules.
"""

import unittest
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser


class TestParser(unittest.TestCase):

    def test_full_network_parsing(self):
        net_str = """
        variable Rain {True, False}
        variable Sprinkler {On, Off}
        variable GrassWet {Yes, No}

        Rain { P(True) = 0.2 }

        Sprinkler | Rain {
            P(On | True) = 0.01
            P(On | False) = 0.4
        }

        GrassWet | Rain, Sprinkler {
            P(Yes | True, On) = 0.99
            P(Yes | True, Off) = 0.8
            P(Yes | False, On) = 0.9
            P(Yes | False, Off) = 0.1
        }
        """
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        self.assertIn("Rain", network.variables)
        self.assertIn("Sprinkler", network.variables)
        self.assertIn("GrassWet", network.variables)

        self.assertIn("Rain", network.factors)
        self.assertIn("Sprinkler", network.factors)
        self.assertIn("GrassWet", network.factors)

        self.assertAlmostEqual(network.factors["Rain"].probabilities[("False",)], 0.8)
        self.assertAlmostEqual(
            network.factors["Sprinkler"].probabilities[("Off", "True")], 0.99
        )
        self.assertAlmostEqual(
            network.factors["GrassWet"].probabilities[("No", "False", "On")], 0.1
        )

    def test_syntax_error_variable(self):
        net_str = "variable Rain {True False}"  # Missing comma
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()

    def test_syntax_error_cpt(self):
        net_str = "Rain { P(True)  0.2 }"  # Missing equals
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()


if __name__ == "__main__":
    unittest.main()
