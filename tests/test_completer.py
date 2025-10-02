"""
Tests for the autocompletion logic.
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
from bayescalc.completer import PromptToolkitCompleter


# Test adapter for the PromptToolkitCompleter
class Completer:
    def __init__(self, network):
        self.completer = PromptToolkitCompleter(network)

    def get_completions(self, text_before_cursor, word_before_cursor):
        # Create a mock document object that has the required properties
        class MockDocument:
            def __init__(self, text, word):
                self.text_before_cursor = text
                self.word = word

            def get_word_before_cursor(self, WORD=False):
                return self.word

        document = MockDocument(text_before_cursor, word_before_cursor)

        # Convert generator to list for easier testing
        return [c.text for c in self.completer.get_completions(document, None)]


class TestCompleter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        net_str = """
        variable Rain {True, False}
        variable Sprinkler {On, Off}
        variable GrassWet {Yes, No}
        """
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()
        cls.completer = Completer(network)

    def test_command_completion(self):
        completions = self.completer.get_completions("prin", "prin")
        self.assertIn("printCPT(", completions)
        self.assertIn("printJPT()", completions)

    def test_variable_name_completion_non_boolean(self):
        completions = self.completer.get_completions("P(Gr", "Gr")
        self.assertEqual(completions, ["GrassWet="])

    def test_variable_name_completion_boolean(self):
        completions = self.completer.get_completions("P(Ra", "Ra")
        self.assertEqual(completions, ["Rain"])

    def test_value_completion(self):
        completions = self.completer.get_completions("P(GrassWet=Y", "Y")
        self.assertEqual(completions, ["Yes"])

        completions = self.completer.get_completions("P(Sprinkler=O", "O")
        self.assertEqual(completions, ["On", "Off"])

    def test_no_completion(self):
        completions = self.completer.get_completions("P(GrassWet=Yes, ", "")
        self.assertEqual(completions, ["Rain", "Sprinkler=", "GrassWet="])

    def test_completion_with_pipe(self):
        """Test completion after a pipe symbol."""
        completions = self.completer.get_completions("P(GrassWet=Yes | Ra", "Ra")
        self.assertEqual(completions, ["Rain"])

        # Test with a longer expression
        completions = self.completer.get_completions("P(GrassWet=Yes | Rain, Sp", "Sp")
        self.assertEqual(completions, ["Sprinkler="])

        # Test with negation
        completions = self.completer.get_completions("P(GrassWet=Yes | ~Ra", "~Ra")
        self.assertEqual(completions, ["~Rain"])

        # Test with multiple conditioning variables
        completions = self.completer.get_completions(
            "P(GrassWet=Yes | Rain, Sprinkler=On, G", "G"
        )
        self.assertEqual(completions, ["GrassWet="])

        # Test with spaces after pipe
        completions = self.completer.get_completions("P(GrassWet=Yes |     Ra", "Ra")
        self.assertEqual(completions, ["Rain"])

        # Test with complex conditions
        completions = self.completer.get_completions(
            "P(GrassWet=Yes | Rain=True, ~Sprinkler=On, G", "G"
        )
        self.assertEqual(completions, ["GrassWet="])

    def test_command_argument_completion(self):
        """Test completion inside command arguments."""
        # Test printCPT command argument completion
        completions = self.completer.get_completions("printCPT(Ra", "Ra")
        self.assertEqual(completions, ["Rain"])

        completions = self.completer.get_completions("printCPT(Gr", "Gr")
        self.assertEqual(completions, ["GrassWet"])

        # Test parents command argument completion
        completions = self.completer.get_completions("parents(Sp", "Sp")
        self.assertEqual(completions, ["Sprinkler"])

        # Test children command argument completion
        completions = self.completer.get_completions("children(Ra", "Ra")
        self.assertEqual(completions, ["Rain"])

        # Test entropy command argument completion
        completions = self.completer.get_completions("entropy(Gr", "Gr")
        self.assertEqual(completions, ["GrassWet"])

    def test_command_multiple_arguments_completion(self):
        """Test completion for commands with multiple arguments."""
        # Test isindependent with two arguments
        completions = self.completer.get_completions("isindependent(Rain, Sp", "Sp")
        self.assertEqual(completions, ["Sprinkler"])

        # Test mutual_information with two arguments
        completions = self.completer.get_completions(
            "mutual_information(GrassWet, Ra", "Ra"
        )
        self.assertEqual(completions, ["Rain"])

    def test_command_conditional_argument_completion(self):
        """Test completion for commands with conditional syntax (|)."""
        # Test iscondindependent command
        completions = self.completer.get_completions(
            "iscondindependent(Rain, Sprinkler | Gr", "Gr"
        )
        self.assertEqual(completions, ["GrassWet"])

        # Test conditional_entropy command
        completions = self.completer.get_completions(
            "conditional_entropy(GrassWet | Ra", "Ra"
        )
        self.assertEqual(completions, ["Rain"])


if __name__ == "__main__":
    unittest.main()
