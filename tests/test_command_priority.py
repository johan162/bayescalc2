"""
Test for command vs expression parsing priority.
"""

import unittest
import tempfile
import os
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.commands import CommandHandler


class TestCommandPriority(unittest.TestCase):
    """Test that commands are recognized before expressions."""

    def test_is_command_method(self):
        """Test the is_command method correctly identifies commands."""
        network_str = """
        boolean A
        A { P(True) = 0.5 }
        """

        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        cmd_handler = CommandHandler(network)

        # Test commands with parentheses
        self.assertTrue(cmd_handler.is_command("load(somefile.net)"))
        self.assertTrue(cmd_handler.is_command("printCPT(A)"))
        self.assertTrue(cmd_handler.is_command("entropy(A)"))
        self.assertTrue(cmd_handler.is_command("parents(A)"))
        self.assertTrue(cmd_handler.is_command("help()"))
        self.assertTrue(cmd_handler.is_command("showGraph()"))

        # Test commands without parentheses
        self.assertTrue(cmd_handler.is_command("ls"))
        self.assertTrue(cmd_handler.is_command("vars"))
        self.assertTrue(cmd_handler.is_command("help"))

        # Test non-commands
        self.assertFalse(cmd_handler.is_command("P(A)"))
        self.assertFalse(cmd_handler.is_command("P(A|B)"))
        self.assertFalse(cmd_handler.is_command("log(0.5)"))
        self.assertFalse(cmd_handler.is_command("sqrt(2)"))
        self.assertFalse(cmd_handler.is_command("unknown_command(x)"))
        self.assertFalse(cmd_handler.is_command("1 + 2"))

    def test_load_command_not_treated_as_expression(self):
        """Test that load command is not treated as a mathematical expression."""
        network_str = """
        boolean A
        A { P(True) = 0.5 }
        """

        network2_str = """
        boolean X
        X { P(Yes) = 0.7 }
        """

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".net", delete=False) as f:
            f.write(network2_str)
            temp_file = f.name

        try:
            lexer = Lexer(network_str)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            network = parser.parse()

            cmd_handler = CommandHandler(network)

            # This should be recognized as a command, not an expression
            self.assertTrue(cmd_handler.is_command(f"load({temp_file})"))

            # Execute it - should work without expression parser errors
            result = cmd_handler.execute(f"load({temp_file})")

            # Verify it worked
            self.assertIn("Successfully loaded", result)
            self.assertIn("X", cmd_handler.network.variables)
            self.assertNotIn("A", cmd_handler.network.variables)
        finally:
            os.unlink(temp_file)

    def test_command_with_path_characters(self):
        """Test that commands with file paths (/, ., ~) are recognized."""
        network_str = """
        boolean A
        A { P(True) = 0.5 }
        """

        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        cmd_handler = CommandHandler(network)

        # Various path formats should be recognized as the load command
        self.assertTrue(cmd_handler.is_command("load(examples/network.net)"))
        self.assertTrue(cmd_handler.is_command("load(../other/network.net)"))
        self.assertTrue(cmd_handler.is_command("load(./network.net)"))
        self.assertTrue(cmd_handler.is_command("load(~/Documents/network.net)"))
        self.assertTrue(cmd_handler.is_command("load(/absolute/path/network.net)"))


if __name__ == "__main__":
    unittest.main()
