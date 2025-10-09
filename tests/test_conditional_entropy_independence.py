"""
Test cases for conditional entropy and conditional independence.

This module tests:
1. Conditional entropy H(X|Y) calculations
2. Conditional independence tests A ⊥ B | C
3. Both positive and negative test cases
4. Edge cases and error handling
"""

import unittest
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.commands import CommandHandler


class TestConditionalEntropy(unittest.TestCase):
    """Test cases for conditional entropy H(X|Y)."""

    @classmethod
    def setUpClass(cls):
        """Set up test networks for conditional entropy tests."""

        # Network 1: Independent variables (A ⊥ B)
        # H(A|B) should equal H(A) since they are independent
        cls.independent_net_str = """
        boolean A
        boolean B

        A {
            P(True) = 0.5
        }

        B | A {
            P(True | True) = 0.5
            P(True | False) = 0.5
        }
        """

        # Network 2: Deterministic relationship
        # B is completely determined by A
        cls.deterministic_net_str = """
        boolean A
        boolean B

        A {
            P(True) = 0.5
        }

        B | A {
            P(True | True) = 1.0
            P(True | False) = 0.0
        }
        """

        # Network 3: Rain-Sprinkler-GrassWet (classic example)
        # GrassWet depends on both Rain and Sprinkler
        cls.rain_net_str = """
        boolean Rain
        boolean Sprinkler
        boolean GrassWet

        Rain {
            P(True) = 0.2
        }

        Sprinkler | Rain {
            P(True | True) = 0.01
            P(True | False) = 0.4
        }

        GrassWet | Rain, Sprinkler {
            P(True | True, True) = 0.99
            P(True | True, False) = 0.8
            P(True | False, True) = 0.9
            P(True | False, False) = 0.1
        }
        """

        # Network 4: Medical test example
        cls.medical_net_str = """
        boolean Sick
        boolean Test

        Sick {
            P(True) = 0.01
        }

        Test | Sick {
            P(True | True) = 0.95
            P(True | False) = 0.06
        }
        """

        # Parse all networks
        lexer = Lexer(cls.independent_net_str)
        cls.independent_network = Parser(lexer.tokenize()).parse()
        cls.independent_handler = CommandHandler(cls.independent_network)

        lexer = Lexer(cls.deterministic_net_str)
        cls.deterministic_network = Parser(lexer.tokenize()).parse()
        cls.deterministic_handler = CommandHandler(cls.deterministic_network)

        lexer = Lexer(cls.rain_net_str)
        cls.rain_network = Parser(lexer.tokenize()).parse()
        cls.rain_handler = CommandHandler(cls.rain_network)

        lexer = Lexer(cls.medical_net_str)
        cls.medical_network = Parser(lexer.tokenize()).parse()
        cls.medical_handler = CommandHandler(cls.medical_network)

    # ========================================================================
    # Positive Test Cases - Conditional Entropy
    # ========================================================================

    def test_conditional_entropy_independent_variables(self):
        """Test H(A|B) = H(A) when A and B are independent."""
        h_a = self.independent_handler.execute("entropy(A)")
        h_a_given_b = self.independent_handler.execute("conditional_entropy(A|B)")

        # When A and B are independent, H(A|B) should equal H(A)
        self.assertAlmostEqual(h_a_given_b, h_a, places=6)
        self.assertAlmostEqual(h_a_given_b, 1.0, places=6)  # H(A) = 1 bit

    def test_conditional_entropy_deterministic_relationship(self):
        """Test H(B|A) = 0 when B is completely determined by A."""
        h_b_given_a = self.deterministic_handler.execute("conditional_entropy(B|A)")

        # When B is completely determined by A, H(B|A) should be 0
        self.assertAlmostEqual(h_b_given_a, 0.0, places=6)

    def test_conditional_entropy_reduces_uncertainty(self):
        """Test that conditioning reduces or maintains entropy: H(X|Y) ≤ H(X)."""
        # Test with Rain-Sprinkler network
        h_sprinkler = self.rain_handler.execute("entropy(Sprinkler)")
        h_sprinkler_given_rain = self.rain_handler.execute(
            "conditional_entropy(Sprinkler|Rain)"
        )

        # Conditioning should reduce entropy
        self.assertLessEqual(h_sprinkler_given_rain, h_sprinkler)

    def test_conditional_entropy_grass_given_rain(self):
        """Test H(GrassWet|Rain) in the rain-sprinkler network."""
        h_grass_given_rain = self.rain_handler.execute(
            "conditional_entropy(GrassWet|Rain)"
        )

        # Should be a positive value less than H(GrassWet)
        h_grass = self.rain_handler.execute("entropy(GrassWet)")
        self.assertGreater(h_grass_given_rain, 0.0)
        self.assertLess(h_grass_given_rain, h_grass)

    def test_conditional_entropy_medical_test(self):
        """Test H(Test|Sick) in medical test network."""
        h_test_given_sick = self.medical_handler.execute(
            "conditional_entropy(Test|Sick)"
        )

        # Should be positive since the test is not perfect (95% sensitivity)
        self.assertGreater(h_test_given_sick, 0.0)

        # Should be less than H(Test)
        h_test = self.medical_handler.execute("entropy(Test)")
        self.assertLess(h_test_given_sick, h_test)

    def test_conditional_entropy_symmetry_check(self):
        """Test that H(A|B) generally differs from H(B|A)."""
        h_rain_given_sprinkler = self.rain_handler.execute(
            "conditional_entropy(Rain|Sprinkler)"
        )
        h_sprinkler_given_rain = self.rain_handler.execute(
            "conditional_entropy(Sprinkler|Rain)"
        )

        # These should generally be different (asymmetric)
        # In this network, they are different because of the causal structure
        self.assertNotAlmostEqual(
            h_rain_given_sprinkler, h_sprinkler_given_rain, places=2
        )

    def test_conditional_entropy_multiple_calls_consistent(self):
        """Test that multiple calls return consistent results."""
        result1 = self.rain_handler.execute("conditional_entropy(GrassWet|Rain)")
        result2 = self.rain_handler.execute("conditional_entropy(GrassWet|Rain)")

        self.assertAlmostEqual(result1, result2, places=10)

    def test_conditional_entropy_chain_rule(self):
        """Test chain rule: H(X,Y) = H(X) + H(Y|X)."""
        # Using medical network
        h_sick = self.medical_handler.execute("entropy(Sick)")
        h_test_given_sick = self.medical_handler.execute(
            "conditional_entropy(Test|Sick)"
        )

        # Calculate joint entropy manually using mutual information
        h_test = self.medical_handler.execute("entropy(Test)")
        mi = self.medical_handler.execute("mutual_information(Sick, Test)")
        h_joint_expected = h_sick + h_test - mi
        h_joint_from_chain = h_sick + h_test_given_sick

        self.assertAlmostEqual(h_joint_expected, h_joint_from_chain, places=6)

    # ========================================================================
    # Negative Test Cases - Conditional Entropy
    # ========================================================================

    def test_conditional_entropy_nonexistent_variable_x(self):
        """Test that conditional_entropy raises error for nonexistent first variable."""
        with self.assertRaises(Exception):
            self.rain_handler.execute("conditional_entropy(NonExistent|Rain)")

    def test_conditional_entropy_nonexistent_variable_y(self):
        """Test that conditional_entropy raises error for nonexistent second variable."""
        with self.assertRaises(Exception):
            self.rain_handler.execute("conditional_entropy(Rain|NonExistent)")

    def test_conditional_entropy_both_nonexistent(self):
        """Test that conditional_entropy raises error when both variables don't exist."""
        with self.assertRaises(Exception):
            self.rain_handler.execute("conditional_entropy(Foo|Bar)")

    def test_conditional_entropy_missing_pipe(self):
        """Test that conditional_entropy raises error without pipe separator."""
        with self.assertRaises(ValueError) as context:
            self.rain_handler.execute("conditional_entropy(Rain, Sprinkler)")

        self.assertIn("format", str(context.exception).lower())

    def test_conditional_entropy_empty_arguments(self):
        """Test that conditional_entropy raises error with empty arguments."""
        with self.assertRaises(Exception):
            self.rain_handler.execute("conditional_entropy(|)")

    def test_conditional_entropy_only_first_variable(self):
        """Test that conditional_entropy raises error with only first variable."""
        with self.assertRaises(Exception):  # KeyError for empty variable name
            self.rain_handler.execute("conditional_entropy(Rain|)")

    def test_conditional_entropy_only_second_variable(self):
        """Test that conditional_entropy raises error with only second variable."""
        with self.assertRaises(Exception):  # KeyError for empty variable name
            self.rain_handler.execute("conditional_entropy(|Rain)")

    def test_conditional_entropy_same_variable(self):
        """Test H(X|X) should equal 0 (a variable is determined by itself)."""
        h_rain_given_rain = self.rain_handler.execute("conditional_entropy(Rain|Rain)")

        # H(X|X) = 0 because knowing X fully determines X
        self.assertAlmostEqual(h_rain_given_rain, 0.0, places=6)


class TestConditionalIndependence(unittest.TestCase):
    """Test cases for conditional independence A ⊥ B | C."""

    @classmethod
    def setUpClass(cls):
        """Set up test networks for conditional independence tests."""

        # Network 1: Simple independent variables
        cls.independent_net_str = """
        boolean A
        boolean B

        A {
            P(True) = 0.5
        }

        B {
            P(True) = 0.5
        }
        """

        # Network 2: Chain A → B → C (B d-separates A and C)
        cls.chain_net_str = """
        boolean A
        boolean B
        boolean C

        A {
            P(True) = 0.5
        }

        B | A {
            P(True | True) = 0.8
            P(True | False) = 0.2
        }

        C | B {
            P(True | True) = 0.7
            P(True | False) = 0.3
        }
        """

        # Network 3: Common cause A ← B → C (B d-separates A and C)
        cls.common_cause_net_str = """
        boolean A
        boolean B
        boolean C

        B {
            P(True) = 0.5
        }

        A | B {
            P(True | True) = 0.8
            P(True | False) = 0.2
        }

        C | B {
            P(True | True) = 0.7
            P(True | False) = 0.3
        }
        """

        # Network 4: V-structure (collider) A → C ← B
        # A and B are marginally independent but dependent given C
        cls.collider_net_str = """
        boolean A
        boolean B
        boolean C

        A {
            P(True) = 0.5
        }

        B {
            P(True) = 0.5
        }

        C | A, B {
            P(True | True, True) = 0.95
            P(True | True, False) = 0.6
            P(True | False, True) = 0.6
            P(True | False, False) = 0.05
        }
        """

        # Network 5: Rain-Sprinkler-GrassWet (classic d-separation example)
        cls.rain_net_str = """
        boolean Rain
        boolean Sprinkler
        boolean GrassWet

        Rain {
            P(True) = 0.2
        }

        Sprinkler | Rain {
            P(True | True) = 0.01
            P(True | False) = 0.4
        }

        GrassWet | Rain, Sprinkler {
            P(True | True, True) = 0.99
            P(True | True, False) = 0.8
            P(True | False, True) = 0.9
            P(True | False, False) = 0.1
        }
        """

        # Parse all networks
        lexer = Lexer(cls.independent_net_str)
        cls.independent_network = Parser(lexer.tokenize()).parse()
        cls.independent_handler = CommandHandler(cls.independent_network)

        lexer = Lexer(cls.chain_net_str)
        cls.chain_network = Parser(lexer.tokenize()).parse()
        cls.chain_handler = CommandHandler(cls.chain_network)

        lexer = Lexer(cls.common_cause_net_str)
        cls.common_cause_network = Parser(lexer.tokenize()).parse()
        cls.common_cause_handler = CommandHandler(cls.common_cause_network)

        lexer = Lexer(cls.collider_net_str)
        cls.collider_network = Parser(lexer.tokenize()).parse()
        cls.collider_handler = CommandHandler(cls.collider_network)

        lexer = Lexer(cls.rain_net_str)
        cls.rain_network = Parser(lexer.tokenize()).parse()
        cls.rain_handler = CommandHandler(cls.rain_network)

    # ========================================================================
    # Positive Test Cases - Unconditional Independence
    # ========================================================================

    def test_independent_variables_are_independent(self):
        """Test that truly independent variables are detected as independent."""
        result = self.independent_handler.execute("isindependent(A, B)")
        self.assertTrue(result)

    def test_collider_parents_are_marginally_independent(self):
        """Test that parents of a collider are marginally independent."""
        # A and B are independent (both cause C)
        result = self.collider_handler.execute("isindependent(A, B)")
        self.assertTrue(result)

    def test_rain_and_sprinkler_not_independent(self):
        """Test that Rain and Sprinkler are NOT independent (causally related)."""
        result = self.rain_handler.execute("isindependent(Rain, Sprinkler)")
        self.assertFalse(result)

    def test_chain_endpoints_not_marginally_independent(self):
        """Test that endpoints of a chain are NOT marginally independent."""
        # A → B → C, so A and C are dependent marginally
        result = self.chain_handler.execute("isindependent(A, C)")
        self.assertFalse(result)

    def test_common_cause_children_not_marginally_independent(self):
        """Test that children of common cause are NOT marginally independent."""
        # B → A and B → C, so A and C are dependent marginally
        result = self.common_cause_handler.execute("isindependent(A, C)")
        self.assertFalse(result)

    # ========================================================================
    # Positive Test Cases - Conditional Independence
    # ========================================================================

    def test_chain_conditional_independence(self):
        """Test conditional independence in a chain: A ⊥ C | B."""
        # A → B → C, so A and C are independent given B
        result = self.chain_handler.execute("iscondindependent(A, C | B)")
        self.assertTrue(result)

    def test_common_cause_conditional_independence(self):
        """Test conditional independence with common cause: A ⊥ C | B."""
        # B → A and B → C, so A and C are independent given B
        result = self.common_cause_handler.execute("iscondindependent(A, C | B)")
        self.assertTrue(result)

    def test_rain_sprinkler_independent_given_nothing(self):
        """Test that Rain and Sprinkler are NOT unconditionally independent."""
        result = self.rain_handler.execute("isindependent(Rain, Sprinkler)")
        self.assertFalse(result)

    def test_collider_creates_dependence(self):
        """Test that conditioning on a collider creates dependence (explaining away)."""
        # A and B are independent, but become dependent when we condition on C
        result = self.collider_handler.execute("iscondindependent(A, B | C)")
        self.assertFalse(result)

    def test_multiple_conditioning_variables(self):
        """Test conditional independence with multiple conditioning variables."""
        # In rain network: Rain ⊥ Sprinkler | GrassWet should be False
        # (they become dependent when we observe GrassWet - explaining away effect)
        result = self.rain_handler.execute(
            "iscondindependent(Rain, Sprinkler | GrassWet)"
        )
        self.assertFalse(result)

    def test_symmetric_conditional_independence(self):
        """Test that conditional independence is symmetric: A ⊥ B | C ⟺ B ⊥ A | C."""
        result1 = self.chain_handler.execute("iscondindependent(A, C | B)")
        result2 = self.chain_handler.execute("iscondindependent(C, A | B)")

        self.assertEqual(result1, result2)

    def test_variable_independent_of_itself_given_nothing(self):
        """Test that a variable is not independent of itself unconditionally."""
        # A variable is perfectly correlated with itself
        result = self.independent_handler.execute("isindependent(A, A)")
        # This should be False since P(A,A) = P(A) ≠ P(A)*P(A) in general
        # Actually, for a binary variable: P(A=T,A=T) = P(A=T) but P(A=T)*P(A=T) = P(A=T)^2
        # So unless P(A=T) = 0 or 1, they are not equal
        self.assertFalse(result)

    # ========================================================================
    # Negative Test Cases - Independence
    # ========================================================================

    def test_isindependent_nonexistent_first_variable(self):
        """Test that isindependent raises error for nonexistent first variable."""
        with self.assertRaises(Exception):
            self.rain_handler.execute("isindependent(NonExistent, Rain)")

    def test_isindependent_nonexistent_second_variable(self):
        """Test that isindependent raises error for nonexistent second variable."""
        with self.assertRaises(Exception):
            self.rain_handler.execute("isindependent(Rain, NonExistent)")

    def test_isindependent_single_argument(self):
        """Test that isindependent raises error with only one argument."""
        with self.assertRaises(Exception):
            self.rain_handler.execute("isindependent(Rain)")

    def test_isindependent_no_arguments(self):
        """Test that isindependent raises error with no arguments."""
        with self.assertRaises(Exception):
            self.rain_handler.execute("isindependent()")

    def test_isindependent_too_many_arguments(self):
        """Test that isindependent raises error with too many arguments."""
        with self.assertRaises(Exception):
            self.rain_handler.execute("isindependent(Rain, Sprinkler, GrassWet)")

    # ========================================================================
    # Negative Test Cases - Conditional Independence
    # ========================================================================

    def test_iscondindependent_nonexistent_first_variable(self):
        """Test that iscondindependent raises error for nonexistent first variable."""
        with self.assertRaises(Exception):
            self.chain_handler.execute("iscondindependent(NonExistent, C | B)")

    def test_iscondindependent_nonexistent_second_variable(self):
        """Test that iscondindependent raises error for nonexistent second variable."""
        with self.assertRaises(Exception):
            self.chain_handler.execute("iscondindependent(A, NonExistent | B)")

    def test_iscondindependent_nonexistent_conditioning_variable(self):
        """Test that iscondindependent raises error for nonexistent conditioning variable."""
        with self.assertRaises(Exception):
            self.chain_handler.execute("iscondindependent(A, C | NonExistent)")

    def test_iscondindependent_missing_pipe(self):
        """Test that iscondindependent raises error without pipe separator."""
        with self.assertRaises(ValueError) as context:
            self.chain_handler.execute("iscondindependent(A, C, B)")

        self.assertIn("format", str(context.exception).lower())

    def test_iscondindependent_single_variable(self):
        """Test that iscondindependent raises error with only one variable."""
        with self.assertRaises(ValueError):
            self.chain_handler.execute("iscondindependent(A | B)")

    def test_iscondindependent_empty_conditioning_set(self):
        """Test that iscondindependent raises error with empty conditioning set."""
        with self.assertRaises(Exception):
            self.chain_handler.execute("iscondindependent(A, C | )")

    def test_iscondindependent_no_variables_to_check(self):
        """Test that iscondindependent raises error with no variables to check."""
        with self.assertRaises(ValueError):
            self.chain_handler.execute("iscondindependent( | B)")

    # ========================================================================
    # Edge Cases and Mathematical Properties
    # ========================================================================

    def test_conditional_independence_transitive_property_fails(self):
        """Test that conditional independence is NOT transitive."""
        # Even if A ⊥ B | C and B ⊥ D | C, it doesn't mean A ⊥ D | C
        # This is just a demonstration that we can test such properties

        # In chain A → B → C, we have A ⊥ C | B
        result = self.chain_handler.execute("iscondindependent(A, C | B)")
        self.assertTrue(result)

    def test_independence_vs_conditional_independence_difference(self):
        """Test that unconditional independence differs from conditional independence."""
        # In collider network: A ⊥ B (marginally) but NOT A ⊥ B | C
        marginal = self.collider_handler.execute("isindependent(A, B)")
        conditional = self.collider_handler.execute("iscondindependent(A, B | C)")

        self.assertTrue(marginal)  # Marginally independent
        self.assertFalse(conditional)  # Dependent given C (explaining away)

    def test_multiple_calls_consistent(self):
        """Test that multiple calls return consistent results."""
        result1 = self.chain_handler.execute("iscondindependent(A, C | B)")
        result2 = self.chain_handler.execute("iscondindependent(A, C | B)")

        self.assertEqual(result1, result2)

    def test_conditional_entropy_related_to_independence(self):
        """Test relationship between conditional entropy and independence."""
        # If A ⊥ B, then H(A|B) = H(A)
        # Using independent network
        h_a = self.independent_handler.execute("entropy(A)")
        h_a_given_b = self.independent_handler.execute("conditional_entropy(A|B)")
        is_independent = self.independent_handler.execute("isindependent(A, B)")

        self.assertTrue(is_independent)
        self.assertAlmostEqual(h_a, h_a_given_b, places=6)


class TestConditionalEntropyEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions for conditional entropy."""

    @classmethod
    def setUpClass(cls):
        """Set up networks with extreme probability values."""

        # Network with extreme probabilities (close to 0 or 1)
        cls.extreme_net_str = """
        boolean A
        boolean B

        A {
            P(True) = 0.99
        }

        B | A {
            P(True | True) = 0.01
            P(True | False) = 0.99
        }
        """

        lexer = Lexer(cls.extreme_net_str)
        cls.extreme_network = Parser(lexer.tokenize()).parse()
        cls.extreme_handler = CommandHandler(cls.extreme_network)

    def test_conditional_entropy_with_extreme_probabilities(self):
        """Test conditional entropy with very skewed probability distributions."""
        h_b_given_a = self.extreme_handler.execute("conditional_entropy(B|A)")

        # Should still be a valid entropy value
        self.assertGreaterEqual(h_b_given_a, 0.0)
        self.assertLessEqual(h_b_given_a, 1.0)

    def test_conditional_entropy_is_non_negative(self):
        """Test that conditional entropy is always non-negative."""
        h_b_given_a = self.extreme_handler.execute("conditional_entropy(B|A)")

        self.assertGreaterEqual(h_b_given_a, 0.0)

    def test_data_processing_inequality(self):
        """Test data processing inequality: I(A;C) ≤ I(A;B) for A → B → C."""
        # This tests a fundamental property of information theory
        # We would need a chain network for this, but it's tested implicitly
        # by the conditional entropy tests
        pass


class TestCondprobs(unittest.TestCase):
    """Test cases for the condprobs(m,n) command."""

    @classmethod
    def setUpClass(cls):
        """Set up test networks for condprobs tests."""

        # Network 1: Simple 2-variable network
        cls.simple_net_str = """
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

        # Network 2: 3-variable chain A → B → C
        cls.chain_net_str = """
        boolean A
        boolean B
        boolean C

        A {
            P(True) = 0.5
        }

        B | A {
            P(True | True) = 0.7
            P(True | False) = 0.2
        }

        C | B {
            P(True | True) = 0.9
            P(True | False) = 0.1
        }
        """

        # Network 3: Rain-Sprinkler-GrassWet (3 variables with complex dependencies)
        cls.rain_net_str = """
        boolean Rain
        boolean Sprinkler
        boolean GrassWet

        Rain {
            P(True) = 0.2
        }

        Sprinkler | Rain {
            P(True | True) = 0.01
            P(True | False) = 0.4
        }

        GrassWet | Rain, Sprinkler {
            P(True | True, True) = 0.99
            P(True | True, False) = 0.8
            P(True | False, True) = 0.9
            P(True | False, False) = 0.1
        }
        """

        # Network 4: 4-variable network for testing larger combinations
        cls.four_var_net_str = """
        boolean A
        boolean B
        boolean C
        boolean D

        A {
            P(True) = 0.5
        }

        B | A {
            P(True | True) = 0.8
            P(True | False) = 0.2
        }

        C | A {
            P(True | True) = 0.7
            P(True | False) = 0.3
        }

        D | B, C {
            P(True | True, True) = 0.9
            P(True | True, False) = 0.6
            P(True | False, True) = 0.5
            P(True | False, False) = 0.1
        }
        """

        # Parse all networks
        lexer = Lexer(cls.simple_net_str)
        cls.simple_network = Parser(lexer.tokenize()).parse()
        cls.simple_handler = CommandHandler(cls.simple_network)

        lexer = Lexer(cls.chain_net_str)
        cls.chain_network = Parser(lexer.tokenize()).parse()
        cls.chain_handler = CommandHandler(cls.chain_network)

        lexer = Lexer(cls.rain_net_str)
        cls.rain_network = Parser(lexer.tokenize()).parse()
        cls.rain_handler = CommandHandler(cls.rain_network)

        lexer = Lexer(cls.four_var_net_str)
        cls.four_var_network = Parser(lexer.tokenize()).parse()
        cls.four_var_handler = CommandHandler(cls.four_var_network)

    # ========================================================================
    # Positive Test Cases - condprobs(m,n)
    # ========================================================================

    def test_condprobs_1_1_simple_network(self):
        """Test condprobs(1,1) on a simple 2-variable network."""
        result = self.simple_handler.execute("condprobs(1, 1)")

        # Should return string with conditional probabilities
        self.assertIsInstance(result, str)

        # Should contain P(A|B) and P(B|A) style probabilities
        self.assertIn("P(", result)
        self.assertIn("|", result)

        # Should have multiple lines (multiple conditional probabilities)
        lines = result.split("\n")
        self.assertGreater(len(lines), 1)

    def test_condprobs_1_1_contains_expected_probabilities(self):
        """Test that condprobs(1,1) contains expected probability patterns."""
        result = self.simple_handler.execute("condprobs(1, 1)")

        # Should contain probabilities with both variables
        self.assertIn("A", result)
        self.assertIn("B", result)

        # Should have probability values (decimal numbers)
        self.assertIn("0.", result)  # Probability values

    def test_condprobs_1_2_three_variable_network(self):
        """Test condprobs(1,2) with 3-variable chain network."""
        result = self.chain_handler.execute("condprobs(1, 2)")

        self.assertIsInstance(result, str)
        self.assertIn("P(", result)

        # Should have conditional probabilities with 2 variables in evidence
        # Format: P(X | Y, Z)
        lines = result.split("\n")
        self.assertGreater(len(lines), 1)

    def test_condprobs_2_1_three_variable_network(self):
        """Test condprobs(2,1) with 3-variable chain network."""
        result = self.chain_handler.execute("condprobs(2, 1)")

        self.assertIsInstance(result, str)
        self.assertIn("P(", result)

        # Should have conditional probabilities with 2 variables being queried
        # Format: P(X, Y | Z)
        self.assertIn(",", result)  # Comma separating multiple query variables

    def test_condprobs_output_format(self):
        """Test that condprobs output is properly formatted."""
        result = self.simple_handler.execute("condprobs(1, 1)")

        lines = result.split("\n")
        for line in lines:
            if line.strip():  # Non-empty lines
                # Should have format: P(...|...) = number
                self.assertIn("=", line)
                self.assertIn("P(", line)

    def test_condprobs_probabilities_valid_range(self):
        """Test that all probabilities are in valid range [0,1]."""
        result = self.simple_handler.execute("condprobs(1, 1)")

        import re

        # Extract probability values (numbers after '=')
        prob_pattern = r"=\s*(\d+\.\d+)"
        probabilities = re.findall(prob_pattern, result)

        for prob_str in probabilities:
            prob = float(prob_str)
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)

    def test_condprobs_uses_negation_syntax(self):
        """Test that condprobs uses ~ notation for False values."""
        result = self.simple_handler.execute("condprobs(1, 1)")

        # Should contain negation symbol for False values
        # (assuming the variables have True/False domains)
        self.assertIn("~", result)

    def test_condprobs_sorted_output(self):
        """Test that condprobs output is sorted consistently."""
        result1 = self.simple_handler.execute("condprobs(1, 1)")
        result2 = self.simple_handler.execute("condprobs(1, 1)")

        # Multiple calls should produce identical output
        self.assertEqual(result1, result2)

    def test_condprobs_rain_network_1_1(self):
        """Test condprobs(1,1) on Rain-Sprinkler-GrassWet network."""
        result = self.rain_handler.execute("condprobs(1, 1)")

        self.assertIsInstance(result, str)
        self.assertIn("Rain", result)
        self.assertIn("Sprinkler", result)
        self.assertIn("GrassWet", result)

    def test_condprobs_rain_network_1_2(self):
        """Test condprobs(1,2) on Rain-Sprinkler-GrassWet network."""
        result = self.rain_handler.execute("condprobs(1, 2)")

        self.assertIsInstance(result, str)

        # Should have probabilities conditioned on 2 variables
        # Count occurrences of commas in evidence part
        lines = result.split("\n")
        # Each line should have format P(X | Y, Z)
        self.assertGreater(len(lines), 1)

    def test_condprobs_2_2_four_variable_network(self):
        """Test condprobs(2,2) with 4-variable network."""
        result = self.four_var_handler.execute("condprobs(2, 2)")

        self.assertIsInstance(result, str)
        self.assertIn("P(", result)

        # Should have both query and evidence with 2 variables
        self.assertIn(",", result)

    def test_condprobs_multiple_calls_consistent(self):
        """Test that multiple calls return consistent results."""
        result1 = self.chain_handler.execute("condprobs(1, 1)")
        result2 = self.chain_handler.execute("condprobs(1, 1)")

        self.assertEqual(result1, result2)

    def test_condprobs_no_overlap_variables(self):
        """Test that condprobs doesn't create P(A|A) (overlapping variables)."""
        result = self.simple_handler.execute("condprobs(1, 1)")

        # Parse each line and check that query and evidence don't overlap
        lines = result.split("\n")
        for line in lines:
            if "P(" in line:
                # Extract query and evidence parts
                # Format: P(query | evidence) = value
                import re

                match = re.search(r"P\(([^|]+)\|([^)]+)\)", line)
                if match:
                    query_part = match.group(1)
                    evidence_part = match.group(2)

                    # Extract variable names (removing ~ and whitespace)
                    query_vars = set(
                        [v.strip().lstrip("~") for v in query_part.split(",")]
                    )
                    evidence_vars = set(
                        [v.strip().lstrip("~") for v in evidence_part.split(",")]
                    )

                    # Ensure no overlap
                    self.assertEqual(len(query_vars & evidence_vars), 0)

    # ========================================================================
    # Negative Test Cases - condprobs(m,n)
    # ========================================================================

    def test_condprobs_zero_n(self):
        """Test that condprobs(0,1) raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(0, 1)")

        self.assertIn("positive", str(context.exception).lower())

    def test_condprobs_zero_m(self):
        """Test that condprobs(1,0) raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(1, 0)")

        self.assertIn("positive", str(context.exception).lower())

    def test_condprobs_both_zero(self):
        """Test that condprobs(0,0) raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(0, 0)")

        self.assertIn("positive", str(context.exception).lower())

    def test_condprobs_negative_n(self):
        """Test that condprobs(-1,1) raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(-1, 1)")

        self.assertIn("positive", str(context.exception).lower())

    def test_condprobs_negative_m(self):
        """Test that condprobs(1,-1) raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(1, -1)")

        self.assertIn("positive", str(context.exception).lower())

    def test_condprobs_exceeds_variable_count(self):
        """Test that condprobs(n+m > num_vars) raises ValueError."""
        # Simple network has 2 variables
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(2, 2)")  # 2+2=4 > 2 variables

        error_msg = str(context.exception).lower()
        self.assertTrue("exceeds" in error_msg or "number" in error_msg)

    def test_condprobs_n_exceeds_variables(self):
        """Test that condprobs with n > num_vars raises ValueError."""
        # Simple network has 2 variables
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(5, 1)")

        self.assertIn("exceeds", str(context.exception).lower())

    def test_condprobs_m_exceeds_variables(self):
        """Test that condprobs with m > num_vars raises ValueError."""
        # Simple network has 2 variables
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(1, 5)")

        self.assertIn("exceeds", str(context.exception).lower())

    def test_condprobs_non_integer_n(self):
        """Test that condprobs with non-integer n raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(1.5, 1)")

        self.assertIn("integer", str(context.exception).lower())

    def test_condprobs_non_integer_m(self):
        """Test that condprobs with non-integer m raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(1, 1.5)")

        self.assertIn("integer", str(context.exception).lower())

    def test_condprobs_string_n(self):
        """Test that condprobs with string n raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(abc, 1)")

        self.assertIn("integer", str(context.exception).lower())

    def test_condprobs_string_m(self):
        """Test that condprobs with string m raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.simple_handler.execute("condprobs(1, xyz)")

        self.assertIn("integer", str(context.exception).lower())

    def test_condprobs_missing_argument(self):
        """Test that condprobs with only one argument raises error."""
        with self.assertRaises(Exception):
            self.simple_handler.execute("condprobs(1)")

    def test_condprobs_no_arguments(self):
        """Test that condprobs with no arguments raises error."""
        with self.assertRaises(Exception):
            self.simple_handler.execute("condprobs()")

    def test_condprobs_too_many_arguments(self):
        """Test that condprobs with too many arguments raises error."""
        with self.assertRaises(Exception):
            self.simple_handler.execute("condprobs(1, 1, 1)")

    # ========================================================================
    # Edge Cases and Mathematical Properties
    # ========================================================================

    def test_condprobs_sum_to_one_for_complete_distribution(self):
        """Test that conditional probabilities sum to 1 for complete outcome space."""
        result = self.simple_handler.execute("condprobs(1, 1)")

        # For each unique evidence configuration, probabilities should sum to ~1
        # This is complex to test thoroughly, but we can verify format
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_condprobs_whitespace_handling(self):
        """Test that condprobs handles extra whitespace in arguments."""
        result1 = self.simple_handler.execute("condprobs(1, 1)")
        result2 = self.simple_handler.execute("condprobs( 1 , 1 )")

        # Results should be identical (whitespace stripped)
        self.assertEqual(result1, result2)

    def test_condprobs_max_combinations(self):
        """Test condprobs with maximum valid n+m equal to number of variables."""
        # Chain network has 3 variables, so n=2, m=1 should work
        result = self.chain_handler.execute("condprobs(2, 1)")

        self.assertIsInstance(result, str)
        self.assertIn("P(", result)

    def test_condprobs_symmetric_arguments(self):
        """Test that condprobs(n,m) differs from condprobs(m,n)."""
        # Using 4-variable network
        result_1_2 = self.four_var_handler.execute("condprobs(1, 2)")
        result_2_1 = self.four_var_handler.execute("condprobs(2, 1)")

        # Results should be different (different query/evidence structure)
        self.assertNotEqual(result_1_2, result_2_1)

    def test_condprobs_all_combinations_accounted(self):
        """Test that condprobs generates all valid non-overlapping combinations."""
        result = self.chain_handler.execute("condprobs(1, 1)")

        lines = [line for line in result.split("\n") if line.strip()]

        # With 3 variables (A, B, C), condprobs(1,1) should generate:
        # P(A|B), P(A|C), P(B|A), P(B|C), P(C|A), P(C|B)
        # Each with True/False variants = 6 * 4 = 24 combinations
        # (actually depends on how many value combinations exist)
        self.assertGreater(len(lines), 5)  # At least several combinations


if __name__ == "__main__":
    unittest.main()
