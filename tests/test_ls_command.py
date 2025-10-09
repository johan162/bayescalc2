import unittest
import sys
from io import StringIO
from unittest.mock import patch

from bayescalc.main import main


class TestLsCommand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.net_file = "examples/rain_sprinkler_grass.net"

    def test_ls_command(self):
        """
        Tests if the 'ls' command correctly lists variables.
        """
        with patch.object(
            sys, "argv", ["bayescalc/main.py", self.net_file, "--cmd", "ls"]
        ):
            captured_output = StringIO()
            with patch("sys.stdout", captured_output):
                main()
            output = captured_output.getvalue()
            # boolean Rain
            # boolean GrassWet
            # ariable Sprinkler {True, False}
            self.assertIn("Variable    | Type       | States", output)
            self.assertIn("Rain        | Boolean    | True, False", output)
            self.assertIn("GrassWet    | Boolean    | True, False", output)
            self.assertIn("Sprinkler   | Boolean    | True, False", output)

    def test_vars_command_alias(self):
        """
        Tests if the 'vars' alias for 'ls' works correctly.
        """
        with patch.object(
            sys, "argv", ["bayescalc/main.py", self.net_file, "--cmd", "vars"]
        ):
            captured_output = StringIO()
            with patch("sys.stdout", captured_output):
                main()
            output = captured_output.getvalue()

            self.assertIn("Variable    | Type       | States", output)
            self.assertIn("Rain        | Boolean    | True, False", output)
            self.assertIn("GrassWet    | Boolean    | True, False", output)
            self.assertIn("Sprinkler   | Boolean    | True, False", output)


if __name__ == "__main__":
    unittest.main()
