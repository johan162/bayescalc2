"""
Test cases for the ExpressionParser class.

This module tests the expression evaluation functionality including:
- Pure mathematical expressions (static)
- Probability queries
- Mixed expressions (math + probability)
- Error handling for invalid expressions
"""

import unittest
import math
from bayescalc.expression_parser import ExpressionParser
from bayescalc.queries import QueryParser
from bayescalc.network_model import BayesianNetwork


class TestExpressionParser(unittest.TestCase):
    """Test cases for expression evaluation."""

    @classmethod
    def setUpClass(cls):
        """Set up a test network used across all test methods."""
        cls.network = BayesianNetwork()

        # Create a simple network with boolean variables
        cls.network.add_variable("Sick", ("True", "False"))
        cls.network.add_factor("Sick", [], {("True",): 0.1, ("False",): 0.9})

        # Add a second variable for more complex tests
        cls.network.add_variable("Test", ("Positive", "Negative"))
        cls.network.add_factor(
            "Test",
            ["Sick"],
            {
                ("Positive", "True"): 0.9,
                ("Positive", "False"): 0.1,
                ("Negative", "True"): 0.1,
                ("Negative", "False"): 0.9,
            },
        )

        cls.query_parser = QueryParser(cls.network)
        cls.expr_parser = ExpressionParser(cls.query_parser)

    # ========================================================================
    # Positive Test Cases: Pure Mathematical Expressions (Static)
    # ========================================================================

    def test_pure_math_log10(self):
        """Test base-10 logarithm of a number."""
        result = self.expr_parser.evaluate("log10(0.5)")
        expected = math.log10(0.5)
        self.assertAlmostEqual(result, expected, places=6)

    def test_pure_math_log(self):
        """Test natural logarithm of a number."""
        result = self.expr_parser.evaluate("log(2)")
        expected = math.log(2)
        self.assertAlmostEqual(result, expected, places=6)

    def test_pure_math_sqrt(self):
        """Test square root."""
        result = self.expr_parser.evaluate("sqrt(2)")
        expected = math.sqrt(2)
        self.assertAlmostEqual(result, expected, places=6)

    def test_pure_math_exp(self):
        """Test exponential function."""
        result = self.expr_parser.evaluate("exp(1)")
        expected = math.exp(1)
        self.assertAlmostEqual(result, expected, places=6)

    def test_pure_math_sin(self):
        """Test sine function."""
        result = self.expr_parser.evaluate("sin(0)")
        expected = math.sin(0)
        self.assertAlmostEqual(result, expected, places=6)

    def test_pure_math_cos(self):
        """Test cosine function."""
        result = self.expr_parser.evaluate("cos(0)")
        expected = math.cos(0)
        self.assertAlmostEqual(result, expected, places=6)

    def test_pure_math_tan(self):
        """Test tangent function."""
        result = self.expr_parser.evaluate("tan(0)")
        expected = math.tan(0)
        self.assertAlmostEqual(result, expected, places=6)

    def test_pure_math_abs(self):
        """Test absolute value."""
        result = self.expr_parser.evaluate("abs(-5)")
        self.assertAlmostEqual(result, 5, places=6)

    def test_pure_math_pow(self):
        """Test power function."""
        result = self.expr_parser.evaluate("pow(2, 3)")
        self.assertAlmostEqual(result, 8, places=6)

    def test_arithmetic_addition(self):
        """Test simple addition."""
        result = self.expr_parser.evaluate("1 + 2")
        self.assertAlmostEqual(result, 3, places=6)

    def test_arithmetic_subtraction(self):
        """Test simple subtraction."""
        result = self.expr_parser.evaluate("5 - 3")
        self.assertAlmostEqual(result, 2, places=6)

    def test_arithmetic_multiplication(self):
        """Test simple multiplication."""
        result = self.expr_parser.evaluate("2 * 3")
        self.assertAlmostEqual(result, 6, places=6)

    def test_arithmetic_division(self):
        """Test simple division."""
        result = self.expr_parser.evaluate("6 / 2")
        self.assertAlmostEqual(result, 3, places=6)

    def test_arithmetic_precedence(self):
        """Test arithmetic with operator precedence."""
        result = self.expr_parser.evaluate("1 + 2 * 3")
        self.assertAlmostEqual(result, 7, places=6)

    def test_arithmetic_parentheses(self):
        """Test arithmetic with parentheses."""
        result = self.expr_parser.evaluate("(1 + 2) * 3")
        self.assertAlmostEqual(result, 9, places=6)

    def test_complex_arithmetic(self):
        """Test complex arithmetic expression."""
        result = self.expr_parser.evaluate("(1 + 2) * 3 - 4 / 2")
        expected = (1 + 2) * 3 - 4 / 2
        self.assertAlmostEqual(result, expected, places=6)

    def test_nested_functions(self):
        """Test nested mathematical functions."""
        result = self.expr_parser.evaluate("sqrt(abs(-4))")
        expected = math.sqrt(abs(-4))
        self.assertAlmostEqual(result, expected, places=6)

    def test_combined_math_functions(self):
        """Test combination of different math functions."""
        result = self.expr_parser.evaluate("log10(100) + sqrt(16)")
        expected = math.log10(100) + math.sqrt(16)
        self.assertAlmostEqual(result, expected, places=6)

    # ========================================================================
    # Positive Test Cases: Probability Queries
    # ========================================================================

    def test_simple_probability_query(self):
        """Test simple probability query returns a Factor."""
        result = self.expr_parser.evaluate("P(Sick)")
        self.assertTrue(hasattr(result, "probabilities"))
        self.assertEqual(len(result.probabilities), 1)

    def test_probability_query_with_value(self):
        """Test probability query with specific value."""
        result = self.expr_parser.evaluate("P(Sick=True)")
        self.assertTrue(hasattr(result, "probabilities"))
        prob = list(result.probabilities.values())[0]
        self.assertAlmostEqual(prob, 0.1, places=6)

    def test_conditional_probability_query(self):
        """Test conditional probability query."""
        result = self.expr_parser.evaluate("P(Test=Positive | Sick=True)")
        self.assertTrue(hasattr(result, "probabilities"))
        prob = list(result.probabilities.values())[0]
        self.assertAlmostEqual(prob, 0.9, places=6)

    # ========================================================================
    # Positive Test Cases: Mixed Expressions (Math + Probability)
    # ========================================================================

    def test_log10_of_probability(self):
        """Test logarithm of probability."""
        result = self.expr_parser.evaluate("log10(P(Sick))")
        expected = math.log10(0.1)
        self.assertAlmostEqual(result, expected, places=6)

    def test_sqrt_of_probability(self):
        """Test square root of probability."""
        result = self.expr_parser.evaluate("sqrt(P(Sick=True))")
        expected = math.sqrt(0.1)
        self.assertAlmostEqual(result, expected, places=6)

    def test_probability_addition(self):
        """Test addition of probabilities."""
        result = self.expr_parser.evaluate("P(Sick=True) + P(Sick=False)")
        self.assertAlmostEqual(result, 1.0, places=6)

    def test_probability_multiplication(self):
        """Test multiplication of probabilities."""
        result = self.expr_parser.evaluate("P(Sick=True) * 2")
        self.assertAlmostEqual(result, 0.2, places=6)

    def test_probability_division(self):
        """Test division of probabilities."""
        result = self.expr_parser.evaluate("P(Sick=False) / P(Sick=True)")
        self.assertAlmostEqual(result, 9.0, places=6)

    def test_complex_mixed_expression(self):
        """Test complex expression with multiple probabilities and math."""
        result = self.expr_parser.evaluate("log10(P(Sick=True)) + sqrt(P(Sick=False))")
        expected = math.log10(0.1) + math.sqrt(0.9)
        self.assertAlmostEqual(result, expected, places=6)

    def test_nested_math_with_probability(self):
        """Test nested mathematical functions with probability."""
        result = self.expr_parser.evaluate("sqrt(abs(log10(P(Sick=True))))")
        expected = math.sqrt(abs(math.log10(0.1)))
        self.assertAlmostEqual(result, expected, places=6)

    def test_multiple_probabilities_in_expression(self):
        """Test expression with multiple probability queries."""
        result = self.expr_parser.evaluate("(P(Sick=True) + P(Sick=False)) / 2")
        self.assertAlmostEqual(result, 0.5, places=6)

    # ========================================================================
    # Test Cases: can_evaluate() Method
    # ========================================================================

    def test_can_evaluate_pure_math(self):
        """Test can_evaluate identifies pure math expressions."""
        self.assertTrue(self.expr_parser.can_evaluate("log10(0.5)"))
        self.assertTrue(self.expr_parser.can_evaluate("sqrt(2)"))
        self.assertTrue(self.expr_parser.can_evaluate("1 + 2"))

    def test_can_evaluate_probability(self):
        """Test can_evaluate identifies probability queries."""
        self.assertTrue(self.expr_parser.can_evaluate("P(Sick)"))
        self.assertTrue(self.expr_parser.can_evaluate("P(Sick=True)"))

    def test_can_evaluate_mixed(self):
        """Test can_evaluate identifies mixed expressions."""
        self.assertTrue(self.expr_parser.can_evaluate("log10(P(Sick))"))
        self.assertTrue(self.expr_parser.can_evaluate("sqrt(P(Sick=True))"))

    def test_can_evaluate_commands_false(self):
        """Test can_evaluate returns False for commands."""
        self.assertFalse(self.expr_parser.can_evaluate("ls()"))
        self.assertFalse(self.expr_parser.can_evaluate("help"))
        self.assertFalse(self.expr_parser.can_evaluate("printCPT(Sick)"))
        self.assertFalse(self.expr_parser.can_evaluate("showGraph()"))

    def test_can_evaluate_pure_numbers(self):
        """Test can_evaluate identifies pure numeric expressions."""
        self.assertTrue(self.expr_parser.can_evaluate("3.14"))
        self.assertTrue(self.expr_parser.can_evaluate("42"))

    # ========================================================================
    # Negative Test Cases: Invalid Expressions
    # ========================================================================

    def test_invalid_math_function(self):
        """Test invalid mathematical function raises error."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("invalid_func(0.5)")

    def test_invalid_probability_variable(self):
        """Test probability query with non-existent variable."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("P(NonExistent)")

    def test_invalid_probability_value(self):
        """Test probability query with invalid value."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("P(Sick=InvalidValue)")

    def test_division_by_zero(self):
        """Test division by zero raises error."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("1 / 0")

    def test_syntax_error_unmatched_parentheses(self):
        """Test unmatched parentheses raises error."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("log10(0.5")

    def test_syntax_error_extra_parentheses(self):
        """Test extra parentheses raises error."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("log10(0.5))")

    def test_invalid_operator(self):
        """Test invalid operator raises error."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("1 % 2")  # Modulo not in allowed operators

    def test_log_of_zero(self):
        """Test logarithm of zero raises error."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("log10(0)")

    def test_log_of_negative(self):
        """Test logarithm of negative number raises error."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("log10(-1)")

    def test_sqrt_of_negative(self):
        """Test square root of negative number raises error."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate("sqrt(-1)")

    def test_empty_expression(self):
        """Test empty expression is not evaluable."""
        self.assertFalse(self.expr_parser.can_evaluate(""))

    def test_invalid_characters(self):
        """Test expression with invalid characters raises error."""
        with self.assertRaises(ValueError):
            self.expr_parser.evaluate('1 + 2; print("hello")')

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_very_small_probability(self):
        """Test handling of very small probability values."""
        # Create a network with very small probability
        network = BayesianNetwork()
        network.add_variable("Rare", ("True", "False"))
        network.add_factor("Rare", [], {("True",): 0.0001, ("False",): 0.9999})

        query_parser = QueryParser(network)
        expr_parser = ExpressionParser(query_parser)

        result = expr_parser.evaluate("log10(P(Rare=True))")
        expected = math.log10(0.0001)
        self.assertAlmostEqual(result, expected, places=6)

    def test_floating_point_arithmetic(self):
        """Test floating point arithmetic precision."""
        result = self.expr_parser.evaluate("0.1 + 0.2")
        # Note: This tests floating point arithmetic behavior
        self.assertAlmostEqual(result, 0.3, places=6)

    def test_whitespace_handling(self):
        """Test expressions with various whitespace."""
        result1 = self.expr_parser.evaluate("1+2")
        result2 = self.expr_parser.evaluate("1 + 2")
        result3 = self.expr_parser.evaluate("  1  +  2  ")

        self.assertAlmostEqual(result1, 3, places=6)
        self.assertAlmostEqual(result2, 3, places=6)
        self.assertAlmostEqual(result3, 3, places=6)

    def test_probability_with_conditional_and_math(self):
        """Test complex expression with conditional probability and math."""
        result = self.expr_parser.evaluate("log10(P(Test=Positive | Sick=True))")
        expected = math.log10(0.9)
        self.assertAlmostEqual(result, expected, places=6)

    def test_chained_operations(self):
        """Test chained mathematical operations."""
        result = self.expr_parser.evaluate("sqrt(exp(log(4)))")
        expected = math.sqrt(math.exp(math.log(4)))
        self.assertAlmostEqual(result, expected, places=6)


if __name__ == "__main__":
    unittest.main()
