"""
Test the command argument completion functionality without requiring prompt_toolkit.
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


# Mock the prompt_toolkit imports to allow testing without the dependency
class MockCompletion:
    def __init__(self, text, start_position=0):
        self.text = text
        self.start_position = start_position


# Mock the completer base class
class MockCompleter:
    pass


# Replace the import in the completer module
import sys

mock_prompt_toolkit = type(sys)("prompt_toolkit")
mock_completion = type(sys)("completion")
mock_completion.Completer = MockCompleter
mock_completion.Completion = MockCompletion
mock_prompt_toolkit.completion = mock_completion
sys.modules["prompt_toolkit"] = mock_prompt_toolkit
sys.modules["prompt_toolkit.completion"] = mock_completion

from bayescalc.completer import PromptToolkitCompleter


class TestCommandArgumentCompletion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a test network with the running.net variables
        net_str = """
        variable Temp {low,high}
        variable JohnRun
        variable MaryRun
        variable Meet

        Temp {
            P(low) = 0.4
            P(high) = 0.6
        }

        JohnRun | Temp {
            P(True|high) = 0.7
            P(True|low) = 0.5
            P(False|high) = 0.3
            P(False|low) = 0.5
        }

        MaryRun | Temp {
            P(True|high) = 0.75
            P(True|low) = 0.4
            P(False|high) = 0.25
            P(False|low) = 0.6
        }

        Meet | JohnRun, MaryRun {
            P(True  | True, True) = 0.5
            P(True  | True, False) = 0.0
            P(True  | False, True) = 0.0
            P(True  | False, False) = 0.0
            P(False | False, True) = 1.0
            P(False | True, False) = 1.0
            P(False | False, False) = 1.0
            P(False | True, True) = 0.5
        }
        """
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        cls.network = parser.parse()
        cls.completer = PromptToolkitCompleter(cls.network)

    def get_completions_helper(self, text_before_cursor, word_before_cursor):
        """Helper to get completions without prompt_toolkit dependency."""

        class MockDocument:
            def __init__(self, text, word):
                self.text_before_cursor = text
                self.word = word

            def get_word_before_cursor(self, WORD=False):
                return self.word

        document = MockDocument(text_before_cursor, word_before_cursor)
        return [c.text for c in self.completer.get_completions(document, None)]

    def test_printCPT_completion(self):
        """Test completion for printCPT command arguments."""
        # Test completing "Ma" to "MaryRun"
        completions = self.get_completions_helper("printCPT(Ma", "Ma")
        self.assertEqual(completions, ["MaryRun"])

        # Test completing "Te" to "Temp"
        completions = self.get_completions_helper("printCPT(Te", "Te")
        self.assertEqual(completions, ["Temp"])

        # Test completing "Jo" to "JohnRun"
        completions = self.get_completions_helper("printCPT(Jo", "Jo")
        self.assertEqual(completions, ["JohnRun"])

        # Test completing "Me" to "Meet"
        completions = self.get_completions_helper("printCPT(Me", "Me")
        self.assertEqual(completions, ["Meet"])

    def test_other_commands_completion(self):
        """Test completion for other command arguments."""
        # Test parents command
        completions = self.get_completions_helper("parents(Ma", "Ma")
        self.assertEqual(completions, ["MaryRun"])

        # Test children command
        completions = self.get_completions_helper("children(Te", "Te")
        self.assertEqual(completions, ["Temp"])

        # Test entropy command
        completions = self.get_completions_helper("entropy(Jo", "Jo")
        self.assertEqual(completions, ["JohnRun"])

    def test_multiple_matches(self):
        """Test completion when multiple variables match the prefix."""
        # Test "M" should match both "MaryRun" and "Meet"
        completions = self.get_completions_helper("printCPT(M", "M")
        self.assertEqual(set(completions), {"MaryRun", "Meet"})

    def test_multiple_argument_completion(self):
        """Test completion for commands with multiple arguments."""
        # Test second argument completion for isindependent
        completions = self.get_completions_helper("isindependent(Temp, Ma", "Ma")
        self.assertEqual(completions, ["MaryRun"])

        # Test second argument for mutual_information - "Me" should only match "Meet"
        completions = self.get_completions_helper(
            "mutual_information(JohnRun, Me", "Me"
        )
        self.assertEqual(completions, ["Meet"])

        # Test with "M" prefix which should match both "MaryRun" and "Meet"
        completions = self.get_completions_helper("mutual_information(JohnRun, M", "M")
        self.assertEqual(set(completions), {"MaryRun", "Meet"})

    def test_conditional_argument_completion(self):
        """Test completion after pipe symbol in conditional commands."""
        # Test completion after | in iscondindependent
        completions = self.get_completions_helper(
            "iscondindependent(MaryRun, JohnRun | Te", "Te"
        )
        self.assertEqual(completions, ["Temp"])

        # Test completion after | in conditional_entropy
        completions = self.get_completions_helper("conditional_entropy(Meet | Ma", "Ma")
        self.assertEqual(completions, ["MaryRun"])

    def test_no_completion_for_non_variable_commands(self):
        """Test that commands not taking variable names don't get variable completion."""
        # marginals takes numbers, not variables
        completions = self.get_completions_helper("marginals(Ma", "Ma")
        self.assertEqual(completions, [])

        # condprobs takes numbers, not variables
        completions = self.get_completions_helper("condprobs(Te", "Te")
        self.assertEqual(completions, [])

    def test_command_name_completion(self):
        """Test that command names themselves complete properly."""
        completions = self.get_completions_helper("printCPT", "printCPT")
        self.assertIn("printCPT(", completions)

        completions = self.get_completions_helper("marg", "marg")
        self.assertIn("marginals(", completions)


if __name__ == "__main__":
    unittest.main()
