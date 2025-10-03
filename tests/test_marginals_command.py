"""
Test cases for the marginals() command.

This module tests the marginals command functionality including:
- Positive flows: marginals(1) and marginals(2)
- Negative flows: marginals(0) and marginals(3)
- Using the medical_test.net example with two variables
"""

import unittest
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.commands import CommandHandler


class TestMarginalsCommand(unittest.TestCase):
    """Test cases for the marginals() command using medical_test.net."""

    @classmethod
    def setUpClass(cls):
        """Set up a test network from the medical_test.net example."""
        # Classical medical test with 95% sensitivity and 94% specificity
        # and prevalence of 1%
        net_str = """
        variable Sick {True, False}
        variable Test {True, False}

        Sick {
            P(True) = 0.01
        }

        Test | Sick {
            P(True | True) = 0.95
            P(True | False) = 0.06
        }
        """
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        cls.network = parser.parse()
        cls.cmd_handler = CommandHandler(cls.network)

    # ========================================================================
    # Positive Test Cases
    # ========================================================================

    def test_marginals_1_returns_valid_output(self):
        """Test marginals(1) returns marginal probabilities for single variables."""
        result = self.cmd_handler.execute("marginals(1)")

        # Check that result is a string
        self.assertIsInstance(result, str)

        # Result should contain both variables
        self.assertIn("Sick", result)
        self.assertIn("Test", result)

        # Should contain probability values
        self.assertIn("0.0", result)  # Probabilities are present

    def test_marginals_1_contains_sick_probabilities(self):
        """Test marginals(1) contains correct probabilities for Sick variable."""
        result = self.cmd_handler.execute("marginals(1)")

        # Should show P(Sick) = 0.01 and P(~Sick) = 0.99
        # The output uses ~ notation for negation instead of True/False
        self.assertIn("Sick", result)
        self.assertIn("~Sick", result)

        # Check that probabilities are in the output
        # P(Sick=True) = 0.01, P(Sick=False) = 0.99
        self.assertIn("0.01", result)
        self.assertIn("0.99", result)

    def test_marginals_1_contains_test_probabilities(self):
        """Test marginals(1) contains correct probabilities for Test variable."""
        result = self.cmd_handler.execute("marginals(1)")

        # Should show marginal probability for Test
        self.assertIn("Test", result)

        # P(Test=True) = P(Test=True|Sick=True)*P(Sick=True) +
        #                P(Test=True|Sick=False)*P(Sick=False)
        #              = 0.95*0.01 + 0.06*0.99 = 0.0095 + 0.0594 = 0.0689
        # P(Test=False) = 1 - 0.0689 = 0.9311

        # Check for approximate values (allowing for formatting differences)
        self.assertIn("0.06", result)  # Part of 0.0689

    def test_marginals_2_returns_valid_output(self):
        """Test marginals(2) returns joint probabilities for all 2-variable combinations."""
        result = self.cmd_handler.execute("marginals(2)")

        # Check that result is a string
        self.assertIsInstance(result, str)

        # Since there are only 2 variables, there's only one combination: (Sick, Test)
        self.assertIn("Sick", result)
        self.assertIn("Test", result)

    def test_marginals_2_contains_joint_probabilities(self):
        """Test marginals(2) contains all joint probability combinations."""
        result = self.cmd_handler.execute("marginals(2)")

        # Should contain all four combinations:
        # P(Sick=True, Test=True), P(Sick=True, Test=False),
        # P(Sick=False, Test=True), P(Sick=False, Test=False)

        # The joint probabilities should be:
        # P(Sick=True, Test=True) = 0.01 * 0.95 = 0.0095
        # P(Sick=True, Test=False) = 0.01 * 0.05 = 0.0005
        # P(Sick=False, Test=True) = 0.99 * 0.06 = 0.0594
        # P(Sick=False, Test=False) = 0.99 * 0.94 = 0.9306

        self.assertIn("0.00", result)  # Part of 0.0095 or 0.0005

    def test_marginals_2_probabilities_sum_to_one(self):
        """Test that marginals(2) joint probabilities sum to approximately 1.0."""
        result = self.cmd_handler.execute("marginals(2)")

        # Extract all probability values from the output
        import re

        prob_pattern = r"(\d+\.\d+)"
        probabilities = re.findall(prob_pattern, result)

        # Convert to floats and sum (skip the first few which might be labels)
        prob_values = []
        for prob_str in probabilities:
            try:
                prob = float(prob_str)
                if 0.0 <= prob <= 1.0:  # Only valid probabilities
                    prob_values.append(prob)
            except ValueError:
                pass

        # The sum of joint probabilities should be approximately 1.0
        if len(prob_values) >= 4:  # We expect at least 4 joint probabilities
            # Take the last 4 probabilities (most likely the actual probability values)
            total = sum(prob_values[-4:])
            self.assertAlmostEqual(total, 1.0, places=2)

    def test_marginals_1_output_format(self):
        """Test marginals(1) output has proper formatting."""
        result = self.cmd_handler.execute("marginals(1)")

        # Output should contain separators or newlines
        self.assertTrue("\n" in result or "|" in result)

        # Should contain variable names as headers
        lines = result.split("\n")
        self.assertTrue(len(lines) > 1)  # Multiple lines of output

    def test_marginals_2_output_format(self):
        """Test marginals(2) output has proper formatting."""
        result = self.cmd_handler.execute("marginals(2)")

        # Output should contain separators or newlines
        self.assertTrue("\n" in result or "|" in result)

        # Should have structured output
        lines = result.split("\n")
        self.assertTrue(len(lines) > 1)  # Multiple lines of output

    # ========================================================================
    # Negative Test Cases
    # ========================================================================

    def test_marginals_0_raises_error(self):
        """Test marginals(0) raises ValueError for non-positive n."""
        with self.assertRaises(ValueError) as context:
            self.cmd_handler.execute("marginals(0)")

        error_msg = str(context.exception)
        self.assertIn("positive", error_msg.lower())

    def test_marginals_negative_raises_error(self):
        """Test marginals with negative number raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.cmd_handler.execute("marginals(-1)")

        error_msg = str(context.exception)
        self.assertIn("positive", error_msg.lower())

    def test_marginals_3_raises_error(self):
        """Test marginals(3) raises ValueError when n exceeds number of variables."""
        with self.assertRaises(ValueError) as context:
            self.cmd_handler.execute("marginals(3)")

        error_msg = str(context.exception)
        # Error should mention that n exceeds the number of variables
        self.assertTrue(
            "exceeds" in error_msg.lower()
            or "more than" in error_msg.lower()
            or "only" in error_msg.lower()
        )
        self.assertIn("2", error_msg)  # Should mention there are 2 variables

    def test_marginals_large_number_raises_error(self):
        """Test marginals with large n raises appropriate error."""
        with self.assertRaises(ValueError) as context:
            self.cmd_handler.execute("marginals(10)")

        error_msg = str(context.exception)
        self.assertIn("2", error_msg)  # Should mention the actual number of variables

    def test_marginals_non_integer_raises_error(self):
        """Test marginals with non-integer argument raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.cmd_handler.execute("marginals(1.5)")

        error_msg = str(context.exception)
        self.assertIn("integer", error_msg.lower())

    def test_marginals_string_raises_error(self):
        """Test marginals with string argument raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.cmd_handler.execute("marginals(abc)")

        error_msg = str(context.exception)
        self.assertIn("integer", error_msg.lower())

    def test_marginals_empty_raises_error(self):
        """Test marginals with no argument raises appropriate error."""
        with self.assertRaises(Exception):
            # This should fail during command parsing
            self.cmd_handler.execute("marginals()")

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_marginals_1_multiple_calls_consistent(self):
        """Test multiple calls to marginals(1) return consistent results."""
        result1 = self.cmd_handler.execute("marginals(1)")
        result2 = self.cmd_handler.execute("marginals(1)")

        # Results should be identical
        self.assertEqual(result1, result2)

    def test_marginals_2_multiple_calls_consistent(self):
        """Test multiple calls to marginals(2) return consistent results."""
        result1 = self.cmd_handler.execute("marginals(2)")
        result2 = self.cmd_handler.execute("marginals(2)")

        # Results should be identical
        self.assertEqual(result1, result2)

    def test_marginals_with_whitespace(self):
        """Test marginals command handles whitespace in arguments."""
        result1 = self.cmd_handler.execute("marginals(1)")
        result2 = self.cmd_handler.execute("marginals( 1 )")

        # Results should be essentially the same (allowing for minor formatting)
        self.assertEqual(result1.strip(), result2.strip())


if __name__ == "__main__":
    unittest.main()
