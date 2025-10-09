"""
Integration test for load command in REPL context.
"""

import unittest
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.commands import CommandHandler
from bayescalc.queries import QueryParser
from bayescalc.expression_parser import ExpressionParser


class TestLoadCommandIntegration(unittest.TestCase):
    """Test load command works correctly in REPL-like context."""

    def test_load_prioritized_over_expression(self):
        """Test that load command is executed as a command, not an expression."""
        # Load initial network
        network_str = """
        boolean A
        A { P(True) = 0.3 }
        """

        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        # Create handlers
        query_parser = QueryParser(network)
        expression_parser = ExpressionParser(query_parser)

        # Track reload
        reload_called = [False]

        def reload_callback(new_network):
            reload_called[0] = True

        cmd_handler = CommandHandler(network, reload_callback=reload_callback)

        # Test command pattern
        load_cmd = "load(examples/rain_sprinkler_grass.net)"

        # Verify it's recognized as a command (not an expression)
        self.assertTrue(cmd_handler.is_command(load_cmd))

        # Verify expression parser would accept it (the bug we're fixing)
        # This shows why we need to check commands first
        self.assertTrue(expression_parser.can_evaluate(load_cmd))

        # Execute as command (should work)
        result = cmd_handler.execute(load_cmd)

        # Verify success
        self.assertIn("Successfully loaded", result)
        self.assertTrue(reload_called[0])

        # Verify new network is loaded
        self.assertIn("Rain", cmd_handler.network.variables)
        self.assertIn("Sprinkler", cmd_handler.network.variables)
        self.assertIn("GrassWet", cmd_handler.network.variables)
        self.assertNotIn("A", cmd_handler.network.variables)

    def test_probability_queries_still_work(self):
        """Ensure probability queries still work after fixing command priority."""
        network_str = """
        boolean A
        A { P(True) = 0.3 }
        """

        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        query_parser = QueryParser(network)
        expression_parser = ExpressionParser(query_parser)
        cmd_handler = CommandHandler(network)

        # Test P() queries are NOT recognized as commands
        self.assertFalse(cmd_handler.is_command("P(A)"))
        self.assertFalse(cmd_handler.is_command("P(A=True)"))

        # But ARE recognized as expressions
        self.assertTrue(expression_parser.can_evaluate("P(A)"))
        self.assertTrue(expression_parser.can_evaluate("P(A=True)"))

        # And they work
        result = expression_parser.evaluate("P(A)")
        self.assertIsNotNone(result)

    def test_other_commands_still_work(self):
        """Ensure other commands aren't broken by the fix."""
        network_str = """
        boolean A
        variable B {Yes, No}

        A { P(True) = 0.3 }
        B | A {
            P(Yes | True) = 0.8
            P(Yes | False) = 0.2
        }
        """

        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        network = parser.parse()

        cmd_handler = CommandHandler(network)

        # All these should be recognized as commands
        test_commands = [
            "printCPT(A)",
            "parents(B)",
            "children(A)",
            "entropy(A)",
            "showGraph()",
            "printJPT()",
            "ls",
            "vars",
            "help",
        ]

        for cmd in test_commands:
            with self.subTest(command=cmd):
                self.assertTrue(
                    cmd_handler.is_command(cmd),
                    f"{cmd} should be recognized as a command",
                )


if __name__ == "__main__":
    unittest.main()
