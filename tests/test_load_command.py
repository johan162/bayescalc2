"""
Tests for the load command.
"""

import unittest
import os
import tempfile
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.commands import CommandHandler


class TestLoadCommand(unittest.TestCase):

    def test_load_network_from_file(self):
        """Test loading a network from a file."""
        # Create a temporary network file
        network1 = """
        boolean A
        boolean B

        A { P(True) = 0.3 }
        B | A {
            P(True | True) = 0.8
            P(True | False) = 0.2
        }
        """

        network2 = """
        variable X {Yes, No}
        variable Y {On, Off}

        X { P(Yes) = 0.5 }
        Y | X {
            P(On | Yes) = 0.7
            P(On | No) = 0.3
        }
        """

        # Create temporary files
        with tempfile.NamedTemporaryFile(mode="w", suffix=".net", delete=False) as f1:
            f1.write(network1)
            temp_file1 = f1.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".net", delete=False) as f2:
            f2.write(network2)
            temp_file2 = f2.name

        try:
            # Parse initial network
            lexer = Lexer(network1)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            network = parser.parse()

            # Track if reload callback was called
            reload_called = [False]
            new_network_ref = [None]

            def reload_callback(new_network):
                reload_called[0] = True
                new_network_ref[0] = new_network

            # Create command handler
            cmd_handler = CommandHandler(network, reload_callback=reload_callback)

            # Verify initial network
            self.assertIn("A", cmd_handler.network.variables)
            self.assertIn("B", cmd_handler.network.variables)
            self.assertNotIn("X", cmd_handler.network.variables)

            # Load new network
            result = cmd_handler.load_network(temp_file2)

            # Verify callback was called
            self.assertTrue(reload_called[0])
            self.assertIsNotNone(new_network_ref[0])

            # Verify new network is loaded
            self.assertIn("X", cmd_handler.network.variables)
            self.assertIn("Y", cmd_handler.network.variables)
            self.assertNotIn("A", cmd_handler.network.variables)
            self.assertNotIn("B", cmd_handler.network.variables)

            # Verify result message
            self.assertIn("Successfully loaded", result)
            self.assertIn(temp_file2, result)
            self.assertIn("X", result)
            self.assertIn("Y", result)

        finally:
            # Clean up temporary files
            os.unlink(temp_file1)
            os.unlink(temp_file2)

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        network_str = """
        boolean A
        A { P(True) = 0.5 }
        """

        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        cmd_handler = CommandHandler(network)

        # Try to load non-existent file
        with self.assertRaises(FileNotFoundError):
            cmd_handler.load_network("/nonexistent/path/to/network.net")

    def test_load_invalid_network_file(self):
        """Test loading a file with invalid network syntax."""
        # Create a temporary file with invalid content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".net", delete=False) as f:
            f.write("This is not a valid network file!!!")
            temp_file = f.name

        try:
            network_str = """
            boolean A
            A { P(True) = 0.5 }
            """

            lexer = Lexer(network_str)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            network = parser.parse()

            cmd_handler = CommandHandler(network)

            # Try to load invalid file
            with self.assertRaises(ValueError):
                cmd_handler.load_network(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_command_via_execute(self):
        """Test load command through the execute method."""
        network_str = """
        boolean A
        A { P(True) = 0.5 }
        """

        network2 = """
        variable X {Yes, No}
        X { P(Yes) = 0.7 }
        """

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".net", delete=False) as f:
            f.write(network2)
            temp_file = f.name

        try:
            lexer = Lexer(network_str)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            network = parser.parse()

            cmd_handler = CommandHandler(network)

            # Execute load command
            result = cmd_handler.execute(f"load({temp_file})")

            # Verify new network is loaded
            self.assertIn("X", cmd_handler.network.variables)
            self.assertNotIn("A", cmd_handler.network.variables)
            self.assertIn("Successfully loaded", result)
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    unittest.main()
