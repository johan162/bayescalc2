"""
This test simulates user input to test the REPL's tab-completion.
It uses direct testing of the PromptToolkitCompleter class rather
than trying to simulate a full PTY environment which is prone to
hanging in CI environments.
"""

import unittest
import sys
import os
from unittest.mock import MagicMock


class TestReplCompletion(unittest.TestCase):
    """
    Test the REPL's completion functionality by directly using the completer
    objects rather than trying to simulate a full terminal session.
    """

    def setUp(self):
        # Setup the test environment
        sys.path.insert(
            0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        )

        # Create a Bayesian network for testing
        from bayescalc.network_model import BayesianNetwork

        self.network = BayesianNetwork()

        # Add the same variables as in the rain_sprinkler_grass.net example
        self.network.add_variable(
            "Rain", ("True", "False")
        )  # This will be a boolean variable
        self.network.add_variable("Sprinkler", ("On", "Off"))
        self.network.add_variable("GrassWet", ("Yes", "No"))

        # Import the completer we want to test
        from bayescalc.completer import PromptToolkitCompleter

        self.completer = PromptToolkitCompleter(self.network)

    def test_variable_completion(self):
        """Test completion of variable names in probability expressions"""
        # Create a mock document for testing
        doc = MagicMock()
        doc.text_before_cursor = "P(R"
        doc.get_word_before_cursor = MagicMock(return_value="R")

        # Get completions
        completions = list(self.completer.get_completions(doc, None))

        # Check the completions
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0].text, "Rain")

    def test_value_completion(self):
        """Test completion of variable values in probability expressions"""
        # Create a mock document for testing
        doc = MagicMock()
        doc.text_before_cursor = "P(GrassWet=Y"
        doc.get_word_before_cursor = MagicMock(return_value="Y")

        # Get completions
        completions = list(self.completer.get_completions(doc, None))

        # Check the completions
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0].text, "Yes")

    def test_completion_with_pipe(self):
        """Test completion after a conditional pipe symbol"""
        # Create a mock document for testing
        doc = MagicMock()
        doc.text_before_cursor = "P(GrassWet=Yes | R"
        doc.get_word_before_cursor = MagicMock(return_value="R")

        # Get completions
        completions = list(self.completer.get_completions(doc, None))

        # Check the completions
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0].text, "Rain")


if __name__ == "__main__":
    unittest.main()
