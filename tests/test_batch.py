"""
Tests for batch mode execution of the Bayesian Network calculator.
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import patch
from io import StringIO


class TestBatchExecution(unittest.TestCase):
    """
    Test the batch execution functionality including execute_commands and run_batch.
    """

    @classmethod
    def setUpClass(cls):
        """Set up the test environment with a sample network."""
        # Setup path
        sys.path.insert(
            0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        )

        # Create a sample Bayesian network
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        cls.example_net_str = """
        boolean Rain
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
        lexer = Lexer(cls.example_net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        cls.network = parser.parse()

    def setUp(self):
        """Set up test fixtures for each test."""
        from bayescalc.batch import execute_commands, run_batch

        self.execute_commands = execute_commands
        self.run_batch = run_batch

    def test_execute_commands_with_query(self):
        """Test executing a probability query command."""
        commands = ["P(Rain=True)"]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        self.assertIn(">> P(Rain=True)", output)
        self.assertIn("P() = 0.200000", output)
        self.assertIn("-" * 20, output)

    def test_execute_commands_with_conditional_query(self):
        """Test executing a conditional probability query."""
        commands = ["P(Rain=True | GrassWet=Yes)"]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        self.assertIn(">> P(Rain=True | GrassWet=Yes)", output)
        self.assertIn("P() =", output)
        self.assertIn("-" * 20, output)

    def test_execute_commands_with_entropy(self):
        """Test executing entropy command."""
        commands = ["entropy(Rain)"]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        self.assertIn(">> entropy(Rain)", output)
        self.assertIn("-" * 20, output)
        # Should have some output (entropy value)

    def test_execute_commands_with_comment(self):
        """Test that comments are skipped."""
        commands = ["# This is a comment", "P(Rain=True)"]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        # Comment should not appear in output
        self.assertNotIn("# This is a comment", output)
        # But the actual command should
        self.assertIn(">> P(Rain=True)", output)

    def test_execute_commands_with_empty_lines(self):
        """Test that empty lines are skipped."""
        commands = ["", "   ", "P(Rain=True)", ""]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        # Should only see one command executed
        self.assertEqual(output.count(">>"), 1)
        self.assertIn(">> P(Rain=True)", output)

    def test_execute_commands_with_exit(self):
        """Test that exit command stops execution."""
        commands = ["P(Rain=True)", "exit", "P(Sprinkler=On)"]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        # First command should execute
        self.assertIn(">> P(Rain=True)", output)
        # Exit should be processed
        self.assertIn(">> exit", output)
        # Command after exit should NOT execute
        self.assertNotIn(">> P(Sprinkler=On)", output)

    def test_execute_commands_with_case_insensitive_exit(self):
        """Test that EXIT (uppercase) also stops execution."""
        commands = ["P(Rain=True)", "EXIT", "P(Sprinkler=On)"]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        # First command should execute
        self.assertIn(">> P(Rain=True)", output)
        # Exit should be processed
        self.assertIn(">> EXIT", output)
        # Command after exit should NOT execute
        self.assertNotIn(">> P(Sprinkler=On)", output)

    def test_execute_commands_with_multiple_queries(self):
        """Test executing multiple probability queries."""
        commands = [
            "P(Rain=True)",
            "P(Sprinkler=On)",
            "P(GrassWet=Yes)",
        ]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        # All commands should execute
        self.assertIn(">> P(Rain=True)", output)
        self.assertIn(">> P(Sprinkler=On)", output)
        self.assertIn(">> P(GrassWet=Yes)", output)
        # Should have three separator lines
        self.assertEqual(output.count("-" * 20), 3)

    def test_execute_commands_with_error_handling(self):
        """Test that errors are caught and execution continues."""
        commands = [
            "P(Rain=True)",
            "P(InvalidVariable=Yes)",  # This should cause an error
            "P(Sprinkler=On)",  # This should still execute
        ]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            with patch("sys.stderr", new=StringIO()) as fake_err:
                self.execute_commands(self.network, commands)
                stdout_output = fake_out.getvalue()
                stderr_output = fake_err.getvalue()

        # First command should succeed
        self.assertIn(">> P(Rain=True)", stdout_output)
        # Error should be captured
        self.assertIn("Error processing command", stderr_output)
        self.assertIn("InvalidVariable", stderr_output)
        # Third command should still execute despite the error
        self.assertIn(">> P(Sprinkler=On)", stdout_output)

    def test_execute_commands_with_invalid_syntax(self):
        """Test handling of syntax errors."""
        commands = [
            "P(Rain=True)",
            "P(Rain",  # Invalid syntax
            "P(Sprinkler=On)",
        ]

        # with patch("sys.stdout", new=StringIO()) as fake_out:
        with patch("sys.stderr", new=StringIO()) as fake_err:
            self.execute_commands(self.network, commands)
            stderr_output = fake_err.getvalue()

        # Error should be reported
        self.assertIn("Error processing command", stderr_output)

    def test_execute_commands_mixed_commands_and_queries(self):
        """Test mixing different types of commands."""
        commands = [
            "P(Rain=True)",
            "entropy(Rain)",
            "P(Sprinkler=On | Rain=True)",
            "marginals(GrassWet)",
        ]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        # All commands should be processed
        self.assertEqual(output.count(">>"), 4)
        self.assertIn(">> P(Rain=True)", output)
        self.assertIn(">> entropy(Rain)", output)
        self.assertIn(">> P(Sprinkler=On | Rain=True)", output)
        self.assertIn(">> marginals(GrassWet)", output)

    def test_run_batch_with_valid_file(self):
        """Test run_batch with a valid commands file."""
        # Create a temporary file with commands
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp.write("P(Rain=True)\n")
            tmp.write("# Comment line\n")
            tmp.write("entropy(Rain)\n")
            tmp.write("P(Sprinkler=On)\n")
            tmp_path = tmp.name

        try:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.run_batch(self.network, tmp_path)
                output = fake_out.getvalue()

            # Check that commands were executed
            self.assertIn(">> P(Rain=True)", output)
            self.assertIn(">> entropy(Rain)", output)
            self.assertIn(">> P(Sprinkler=On)", output)
            # Comment should not appear
            self.assertNotIn("# Comment line", output)

        finally:
            # Clean up
            os.unlink(tmp_path)

    def test_run_batch_with_nonexistent_file(self):
        """Test run_batch with a file that doesn't exist."""
        nonexistent_file = "/tmp/this_file_does_not_exist_123456789.txt"

        with patch("sys.stderr", new=StringIO()) as fake_err:
            self.run_batch(self.network, nonexistent_file)
            error_output = fake_err.getvalue()

        # Should report file not found error
        self.assertIn("Error: Commands file not found", error_output)
        self.assertIn(nonexistent_file, error_output)

    def test_run_batch_with_empty_file(self):
        """Test run_batch with an empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            # Write nothing
            tmp_path = tmp.name

        try:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.run_batch(self.network, tmp_path)
                output = fake_out.getvalue()

            # Should complete without output (no commands to execute)
            self.assertEqual(output, "")

        finally:
            os.unlink(tmp_path)

    def test_run_batch_with_only_comments(self):
        """Test run_batch with a file containing only comments."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp.write("# Comment 1\n")
            tmp.write("# Comment 2\n")
            tmp.write("# Comment 3\n")
            tmp_path = tmp.name

        try:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.run_batch(self.network, tmp_path)
                output = fake_out.getvalue()

            # Should complete without executing any commands
            self.assertNotIn(">>", output)

        finally:
            os.unlink(tmp_path)

    def test_run_batch_with_whitespace_handling(self):
        """Test run_batch handles leading/trailing whitespace correctly."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp.write("  P(Rain=True)  \n")
            tmp.write("\t\tentropy(Rain)\t\n")
            tmp.write("   \n")  # Empty line with spaces
            tmp.write("P(Sprinkler=On)\n")
            tmp_path = tmp.name

        try:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.execute_commands(
                    self.network,
                    [
                        "  P(Rain=True)  ",
                        "\t\tentropy(Rain)\t",
                        "   ",
                        "P(Sprinkler=On)",
                    ],
                )
                output = fake_out.getvalue()

            # All non-empty commands should execute
            self.assertIn(">> P(Rain=True)", output)
            self.assertIn(">> entropy(Rain)", output)
            self.assertIn(">> P(Sprinkler=On)", output)
            # Should have exactly 3 commands (empty line skipped)
            self.assertEqual(output.count(">>"), 3)

        finally:
            os.unlink(tmp_path)

    def test_run_batch_stops_at_exit(self):
        """Test that run_batch stops processing at exit command."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp.write("P(Rain=True)\n")
            tmp.write("exit\n")
            tmp.write("P(Sprinkler=On)\n")
            tmp.write("entropy(GrassWet)\n")
            tmp_path = tmp.name

        try:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.run_batch(self.network, tmp_path)
                output = fake_out.getvalue()

            # First command should execute
            self.assertIn(">> P(Rain=True)", output)
            # Exit should be processed
            self.assertIn(">> exit", output)
            # Commands after exit should NOT execute
            self.assertNotIn(">> P(Sprinkler=On)", output)
            self.assertNotIn(">> entropy(GrassWet)", output)

        finally:
            os.unlink(tmp_path)

    def test_execute_commands_with_joint_probability(self):
        """Test executing joint probability query."""
        commands = ["P(Rain=True, Sprinkler=On)"]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        self.assertIn(">> P(Rain=True, Sprinkler=On)", output)
        self.assertIn("P(", output)
        self.assertIn("-" * 20, output)

    def test_execute_commands_with_marginal_query(self):
        """Test executing a marginal probability query (without specific value)."""
        commands = ["P(Rain)"]

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.execute_commands(self.network, commands)
            output = fake_out.getvalue()

        self.assertIn(">> P(Rain)", output)
        # For boolean variables, P(Rain) returns P(Rain=True) by default
        self.assertIn("P() =", output)
        self.assertIn("0.200000", output)

    def test_run_batch_integration(self):
        """Integration test with realistic batch file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
            tmp.write("# Rain-Sprinkler-Grass Network Analysis\n")
            tmp.write("\n")
            tmp.write("# Prior probability of rain\n")
            tmp.write("P(Rain=True)\n")
            tmp.write("\n")
            tmp.write("# Conditional probability\n")
            tmp.write("P(Rain=True | GrassWet=Yes)\n")
            tmp.write("\n")
            tmp.write("# Information theory\n")
            tmp.write("entropy(Rain)\n")
            tmp.write("entropy(Sprinkler)\n")
            tmp.write("\n")
            tmp.write("# Marginals\n")
            tmp.write("marginals(GrassWet)\n")
            tmp_path = tmp.name

        try:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.run_batch(self.network, tmp_path)
                output = fake_out.getvalue()

            # Verify all non-comment commands executed
            self.assertIn(">> P(Rain=True)", output)
            self.assertIn(">> P(Rain=True | GrassWet=Yes)", output)
            self.assertIn(">> entropy(Rain)", output)
            self.assertIn(">> entropy(Sprinkler)", output)
            self.assertIn(">> marginals(GrassWet)", output)
            # Should have exactly 5 command executions
            self.assertEqual(output.count(">>"), 5)

        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
