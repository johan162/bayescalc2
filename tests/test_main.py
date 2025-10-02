"""
Tests for the main entry point and command-line arguments.
"""

import unittest
import sys
from io import StringIO
from unittest.mock import patch

from bayescalc.main import main


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.net_file = "examples/rain_sprinkler_grass.net"
        # In a real scenario, you'd use a temporary file.
        # For this project, the file should exist.

    def test_cmd_argument_execution(self):
        """
        Tests if the --cmd argument correctly executes commands.
        """
        cmd_string = "P(Rain|GrassWet);showGraph()"

        # Use patch to simulate command-line arguments
        with patch.object(
            sys, "argv", ["bayescalc/main.py", self.net_file, "--cmd", cmd_string]
        ):

            # Redirect stdout to capture the output
            captured_output = StringIO()
            original_stdout = sys.stdout
            sys.stdout = captured_output

            try:
                main()
            finally:
                # Restore stdout
                sys.stdout = original_stdout

            output = captured_output.getvalue()

            # Verify the output of the probability query
            self.assertIn(">> P(Rain|GrassWet)", output)
            self.assertIn("P() = 0.323099", output)

            # # Verify the output of the graph command
            self.assertIn(">> showGraph()", output)
            self.assertIn("Bayesian Network Graph:", output)
            # # Check for connections without being too strict on order
            # The format has changed to show parents first, then children
            # The order of children might be different, so we check for both possibilities
            self.assertTrue(
                "Rain -> {Sprinkler, GrassWet}" in output
                or "Rain -> {GrassWet, Sprinkler}" in output
            )
            self.assertIn("Sprinkler -> {GrassWet}", output)


if __name__ == "__main__":
    unittest.main()

# '>> P(Rain|GrassWet)\n  P() = 0.323099\n--------------------\n>> showGraph()\nBayesian Network Graph:\n  Rain -> {Sprinkler, GrassWet}\n  Sprinkler -> {GrassWet}\n--------------------\n'
