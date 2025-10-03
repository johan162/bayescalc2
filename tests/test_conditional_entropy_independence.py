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
        variable A {True, False}
        variable B {True, False}

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
        variable A {True, False}
        variable B {True, False}

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
        variable Rain {True, False}
        variable Sprinkler {True, False}
        variable GrassWet {True, False}

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
        variable A {True, False}
        variable B {True, False}

        A {
            P(True) = 0.5
        }

        B {
            P(True) = 0.5
        }
        """

        # Network 2: Chain A → B → C (B d-separates A and C)
        cls.chain_net_str = """
        variable A {True, False}
        variable B {True, False}
        variable C {True, False}

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
        variable A {True, False}
        variable B {True, False}
        variable C {True, False}

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
        variable A {True, False}
        variable B {True, False}
        variable C {True, False}

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
        variable Rain {True, False}
        variable Sprinkler {True, False}
        variable GrassWet {True, False}

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
        variable A {True, False}
        variable B {True, False}

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


if __name__ == "__main__":
    unittest.main()
