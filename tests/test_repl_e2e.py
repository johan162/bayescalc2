"""
This test simulates user input to test the REPL's tab-completion and execution.
It uses direct testing of the PromptToolkitCompleter class rather
than trying to simulate a full PTY environment which is prone to
hanging in CI environments.
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch, Mock
from io import StringIO


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


class TestReplLoop(unittest.TestCase):
    """Test the REPL loop execution with simulated user input."""

    def setUp(self):
        """Set up test environment with a Bayesian network."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser
        from bayescalc.repl import REPL

        # Create a simple test network
        net_str = """
        boolean A
        boolean B

        A {
            P(True) = 0.6
        }

        B | A {
            P(True | True) = 0.8
            P(True | False) = 0.3
        }
        """

        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        self.network = parser.parse()
        self.repl = REPL(self.network)

    def test_repl_initialization(self):
        """Test that REPL initializes correctly with a network."""
        self.assertIsNotNone(self.repl)
        self.assertIsNotNone(self.repl.network)
        self.assertIsNotNone(self.repl.query_parser)
        self.assertIsNotNone(self.repl.command_handler)
        self.assertIsNotNone(self.repl.expression_parser)

    def test_repl_help_command(self):
        """Test that help command prints without errors."""
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.repl.print_help()
            output = fake_out.getvalue()

        # Verify help text contains expected content
        self.assertIn("Available commands", output)
        self.assertIn("P(A, B | C=c, D=d)", output)
        self.assertIn("entropy", output)
        self.assertIn("exit", output)

    def test_repl_run_without_prompt_toolkit(self):
        """Test that REPL raises error when prompt_toolkit is not available."""
        # REPL session is None when PROMPT_TOOLKIT_AVAILABLE is False
        self.assertIsNone(self.repl.session)

        with self.assertRaises(RuntimeError) as context:
            self.repl.run()

        self.assertIn("prompt_toolkit", str(context.exception).lower())

    def test_repl_run_with_exit_command(self):
        """Test REPL loop with exit command."""
        # Mock the session to simulate user input
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            # Temporarily set PROMPT_TOOLKIT_AVAILABLE to True
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Verify welcome message was printed
        self.assertIn("Bayesian Network Calculator", output)

    def test_repl_run_with_help_command(self):
        """Test REPL loop with help command followed by exit."""
        # Mock the session to simulate user input: help, then exit
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["help", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Verify help was displayed
        self.assertIn("Available commands", output)
        self.assertIn("entropy", output)

    def test_repl_run_with_query(self):
        """Test REPL loop with probability query."""
        # Mock the session to simulate user input: query, then exit
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["P(A)", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Verify probability result was printed
        self.assertIn("0.6", output)  # P(A=True) = 0.6

    def test_repl_run_with_command(self):
        """Test REPL loop with command execution."""
        # Mock the session to simulate user input: entropy command, then exit
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["entropy(A)", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Verify entropy was computed and printed
        self.assertIn("0.9", output)  # H(A) for p=0.6 is approximately 0.97

    def test_repl_run_with_expression(self):
        """Test REPL loop with mathematical expression."""
        # Mock the session to simulate user input: expression, then exit
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["log10(0.5)", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Verify expression result was printed
        # log10(0.5) ≈ -0.301030
        self.assertIn("-0.3", output)

    def test_repl_run_with_error_handling(self):
        """Test REPL loop handles errors gracefully."""
        # Mock the session to simulate invalid command, then exit
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["invalid_command(xyz)", "exit"])

        self.repl.session = mock_session

        # Capture stderr
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()):
                import bayescalc.repl

                original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
                try:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                    self.repl.run()
                finally:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
                error_output = fake_err.getvalue()

        # Verify error was printed to stderr
        self.assertIn("Error", error_output)

    def test_repl_run_with_keyboard_interrupt(self):
        """Test REPL loop handles KeyboardInterrupt gracefully."""
        # Mock the session to simulate Ctrl+C
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=KeyboardInterrupt())

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Verify graceful exit message
        self.assertIn("Exiting", output)

    def test_repl_run_with_eof(self):
        """Test REPL loop handles EOF (Ctrl+D) gracefully."""
        # Mock the session to simulate EOF
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=EOFError())

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Verify graceful exit message
        self.assertIn("Exiting", output)

    def test_repl_run_with_empty_input(self):
        """Test REPL loop skips empty input lines."""
        # Mock the session to simulate empty lines then exit
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["", "  ", "\t", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Should only see welcome message, no errors
        self.assertIn("Bayesian Network Calculator", output)
        # Empty lines should be skipped without output

    def test_repl_run_with_multiple_commands(self):
        """Test REPL loop with multiple commands in sequence."""
        # Mock the session with multiple commands
        mock_session = Mock()
        mock_session.prompt = Mock(
            side_effect=["entropy(A)", "entropy(B)", "isindependent(A, B)", "exit"]
        )

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Verify all commands executed
        self.assertIn("0.9", output)  # Entropy results
        # Should have multiple numerical outputs

    def test_repl_conditional_probability_query(self):
        """Test REPL with conditional probability query."""
        # Mock the session with conditional query
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["P(B=True | A=True)", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # P(B=True | A=True) = 0.8 from the network definition
        self.assertIn("0.8", output)

    def test_repl_probability_expression(self):
        """Test REPL with probability arithmetic expression."""
        # Mock the session with probability expression
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["P(A=True) + P(A=False)", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # P(A=True) + P(A=False) = 0.6 + 0.4 = 1.0
        self.assertIn("1.0", output)

    def test_repl_has_history_file(self):
        """Test that REPL configures history file."""
        self.assertEqual(self.repl.history_file, ".bayescalc_history")

    def test_repl_query_parser_initialized(self):
        """Test that REPL has query parser initialized with network."""
        self.assertIsNotNone(self.repl.query_parser)
        self.assertEqual(self.repl.query_parser.network, self.network)

    def test_repl_command_handler_initialized(self):
        """Test that REPL has command handler initialized with network."""
        self.assertIsNotNone(self.repl.command_handler)
        self.assertEqual(self.repl.command_handler.network, self.network)

    def test_repl_expression_parser_initialized(self):
        """Test that REPL has expression parser initialized."""
        self.assertIsNotNone(self.repl.expression_parser)
        self.assertIsNotNone(self.repl.expression_parser.query_parser)

    def test_repl_run_expression_returns_factor(self):
        """Test REPL with expression that returns a Factor (probability distribution)."""
        # Mock the session - P(A) returns a Factor with probabilities
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["P(A)", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Should print probability distribution
        self.assertIn("P(", output)
        self.assertIn("=", output)
        self.assertIn("0.", output)

    def test_repl_run_expression_evaluation_error(self):
        """Test REPL handles ValueError during expression evaluation."""
        # Mock the session with an expression that will cause ValueError
        mock_session = Mock()
        # Division by zero or invalid probability expression
        mock_session.prompt = Mock(side_effect=["P(A=True) / 0", "exit"])

        self.repl.session = mock_session

        # Capture stderr for error
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()):
                import bayescalc.repl

                original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
                try:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                    self.repl.run()
                finally:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
                error_output = fake_err.getvalue()

        # Should print error but continue running
        self.assertIn("Error", error_output)

    def test_repl_run_command_value_error(self):
        """Test REPL handles ValueError from command execution."""
        # Mock the session with command that raises ValueError
        mock_session = Mock()
        # marginals(0) raises ValueError
        mock_session.prompt = Mock(side_effect=["marginals(0)", "exit"])

        self.repl.session = mock_session

        # Capture stderr
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()):
                import bayescalc.repl

                original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
                try:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                    self.repl.run()
                finally:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
                error_output = fake_err.getvalue()

        # Should catch and print ValueError
        self.assertIn("Error", error_output)
        self.assertIn("positive", error_output.lower())

    def test_repl_run_command_syntax_error(self):
        """Test REPL handles SyntaxError from command execution."""
        # Mock the session with command that causes SyntaxError
        mock_session = Mock()
        # Malformed command
        mock_session.prompt = Mock(side_effect=["printCPT((((", "exit"])

        self.repl.session = mock_session

        # Capture stderr
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()):
                import bayescalc.repl

                original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
                try:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                    self.repl.run()
                finally:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
                error_output = fake_err.getvalue()

        # Should catch and print error
        self.assertIn("Error", error_output)

    def test_repl_run_command_key_error(self):
        """Test REPL handles errors from command execution gracefully."""
        # Mock the session with command that will cause an error
        mock_session = Mock()
        # Try to access non-existent variable - will be handled as error
        mock_session.prompt = Mock(side_effect=["P(NonExistent=True)", "exit"])

        self.repl.session = mock_session

        # Capture stderr - should have error output
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                import bayescalc.repl

                original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
                try:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                    self.repl.run()
                finally:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
                error_output = fake_err.getvalue()
                std_output = fake_out.getvalue()

        # Should handle error gracefully and continue (exit command works)
        self.assertIn("Bayesian Network Calculator", std_output)
        # Error should be printed (might be to stderr or as part of normal flow)
        self.assertTrue(
            len(error_output) > 0
            or "Error" in std_output
            or "error" in std_output.lower()
        )

    def test_repl_run_outer_exception_value_error(self):
        """Test REPL handles ValueError in outer try-except block."""
        # Mock the session - simulate ValueError being raised
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["entropy(A)", "exit"])

        self.repl.session = mock_session

        # Temporarily make prompt raise ValueError on second call
        call_count = [0]

        def prompt_with_error(prompt_str):
            call_count[0] += 1
            if call_count[0] == 1:
                return "entropy(A)"
            elif call_count[0] == 2:
                # Raise ValueError from prompt itself
                raise ValueError("Simulated prompt error")
            return "exit"

        self.repl.session.prompt = Mock(side_effect=prompt_with_error)

        # Capture stderr
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()):
                import bayescalc.repl

                original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
                try:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                    self.repl.run()
                finally:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
                error_output = fake_err.getvalue()

        # Should catch ValueError in outer exception handler
        self.assertIn("Error", error_output)

    def test_repl_run_query_with_multiple_values(self):
        """Test REPL query returning probability distribution."""
        # Mock the session with a query that returns a distribution
        mock_session = Mock()
        # Query without specifying value returns distribution
        mock_session.prompt = Mock(side_effect=["P(A)", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # P(A) returns marginal distribution with probabilities
        # Should have probability values in output
        self.assertIn("P(", output)
        self.assertIn("0.6", output)  # P(A=True) = 0.6
        # Query result is printed with format "  P() = 0.600000"
        self.assertIn("=", output)

    def test_repl_run_case_insensitive_exit(self):
        """Test that exit command is case-insensitive."""
        # Test uppercase EXIT
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["EXIT"])

        self.repl.session = mock_session

        # Should exit cleanly
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        self.assertIn("Bayesian Network Calculator", output)

    def test_repl_run_case_insensitive_help(self):
        """Test that help command is case-insensitive."""
        # Test mixed case HeLp
        mock_session = Mock()
        mock_session.prompt = Mock(side_effect=["HeLp", "exit"])

        self.repl.session = mock_session

        # Should show help
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        self.assertIn("Available commands", output)

    def test_repl_run_mixed_commands_and_queries(self):
        """Test REPL with mix of commands, queries, and expressions."""
        mock_session = Mock()
        mock_session.prompt = Mock(
            side_effect=[
                "P(A)",  # Query - returns Factor
                "entropy(A)",  # Command - returns scalar
                "P(A=True) * 2",  # Expression - returns scalar
                "printCPT(B)",  # Command - returns string
                "isindependent(A, B)",  # Command - returns boolean
                "exit",
            ]
        )

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Should have executed all commands
        self.assertIn("0.6", output)  # P(A=True)
        self.assertIn("0.9", output)  # entropy result
        self.assertIn("1.2", output)  # P(A=True) * 2 = 1.2
        # printCPT output contains the table with variable B
        self.assertIn("B", output)
        self.assertIn("FALSE", output.upper() or "False")  # isindependent result

    def test_repl_run_expression_not_evaluable_as_command(self):
        """Test that non-expression input is handled as command."""
        mock_session = Mock()
        # "ls" is not evaluable as expression, should be handled as command
        mock_session.prompt = Mock(side_effect=["ls", "exit"])

        self.repl.session = mock_session

        # Capture output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # Should list variables
        self.assertIn("A", output)
        self.assertIn("B", output)

    def test_repl_run_continues_after_error(self):
        """Test that REPL continues running after encountering an error."""
        mock_session = Mock()
        mock_session.prompt = Mock(
            side_effect=[
                "invalid_command_xyz",  # Error
                "entropy(A)",  # Valid command after error
                "exit",
            ]
        )

        self.repl.session = mock_session

        # Capture both stdout and stderr
        with patch("sys.stderr", new=StringIO()) as fake_err:
            with patch("sys.stdout", new=StringIO()) as fake_out:
                import bayescalc.repl

                original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
                try:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                    self.repl.run()
                finally:
                    bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
                output = fake_out.getvalue()
                error_output = fake_err.getvalue()

        # Should have error for first command
        self.assertIn("Error", error_output)
        # But should have successfully executed second command
        self.assertIn("0.9", output)  # entropy result

    def test_repl_run_whitespace_variations(self):
        """Test REPL with various whitespace patterns in input."""
        mock_session = Mock()
        mock_session.prompt = Mock(
            side_effect=[
                "  entropy(A)  ",  # Leading/trailing spaces
                "\tentropy(B)\t",  # Tabs
                "  P(A)  ",  # Spaces around query
                "exit",
            ]
        )

        self.repl.session = mock_session

        # Should handle all inputs correctly after stripping
        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # All commands should execute
        self.assertIn("0.9", output)  # entropy results

    def test_repl_run_evaluates_expression_before_command(self):
        """Test that expression evaluation is tried before command execution."""
        mock_session = Mock()
        # log10(0.1) is an expression, should be evaluated not treated as command
        mock_session.prompt = Mock(side_effect=["log10(0.1)", "exit"])

        self.repl.session = mock_session

        with patch("sys.stdout", new=StringIO()) as fake_out:
            import bayescalc.repl

            original_available = bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE
            try:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = True
                self.repl.run()
            finally:
                bayescalc.repl.PROMPT_TOOLKIT_AVAILABLE = original_available
            output = fake_out.getvalue()

        # log10(0.1) = -1.0
        self.assertIn("-1.0", output)
        self.assertIn("=", output)  # Expression result format


if __name__ == "__main__":
    unittest.main()
