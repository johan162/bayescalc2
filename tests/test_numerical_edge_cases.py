"""
Test numerical edge cases in probability calculations.
"""

import unittest
import sys
import os
from decimal import Decimal, getcontext

# Add src to path to allow importing bayescalc modules
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from bayescalc.network_model import BayesianNetwork
from bayescalc.inference import Inference


class TestNumericalEdgeCases(unittest.TestCase):

    def test_extreme_small_probabilities(self):
        """Test calculations involving extremely small probability values."""
        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))
        network.add_variable("B", ("True", "False"))

        # A has an extremely small probability of being True
        network.add_factor("A", [], {("True",): 1e-15, ("False",): 1 - 1e-15})

        # B has different probabilities conditioned on A
        network.add_factor(
            "B",
            ["A"],
            {
                ("True", "True"): 0.9,
                ("False", "True"): 0.1,
                ("True", "False"): 0.1,
                ("False", "False"): 0.9,
            },
        )

        inference = Inference(network)

        # P(A=True) should be 1e-15
        result = inference.variable_elimination({"A": None}, {})
        self.assertAlmostEqual(result.probabilities[("True",)], 1e-15, places=16)

        # P(A=True|B=True) should be calculable and not underflow to zero
        # Using Bayes' theorem:
        # P(A=T|B=T) = P(B=T|A=T)*P(A=T) / P(B=T)
        # P(B=T) = P(B=T|A=T)*P(A=T) + P(B=T|A=F)*P(A=F)
        # P(B=T) = 0.9*1e-15 + 0.1*(1-1e-15) ≈ 0.1
        # P(A=T|B=T) = 0.9*1e-15 / 0.1 = 9e-15
        result = inference.variable_elimination({"A": None}, {"B": "True"})
        self.assertAlmostEqual(result.probabilities[("True",)], 9e-15, places=16)

    def test_zero_probabilities(self):
        """Test calculations involving zero probability values."""
        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))
        network.add_variable("B", ("True", "False"))

        # A has 0 probability of being True
        network.add_factor("A", [], {("True",): 0.0, ("False",): 1.0})

        # B has different probabilities conditioned on A
        network.add_factor(
            "B",
            ["A"],
            {
                ("True", "True"): 0.8,  # Note: This will never actually happen
                ("False", "True"): 0.2,  # Note: This will never actually happen
                ("True", "False"): 0.3,
                ("False", "False"): 0.7,
            },
        )

        inference = Inference(network)

        # P(A=True) should be 0
        result = inference.variable_elimination({"A": None}, {})
        self.assertEqual(result.probabilities[("True",)], 0.0)

        # P(A=True|B=True) should be 0 because P(A=True) = 0
        result = inference.variable_elimination({"A": None}, {"B": "True"})
        self.assertEqual(result.probabilities[("True",)], 0.0)

        # P(A=True|B=False) should be 0 because P(A=True) = 0
        result = inference.variable_elimination({"A": None}, {"B": "False"})
        self.assertEqual(result.probabilities[("True",)], 0.0)

    def test_certainty_propagation(self):
        """Test that certainty propagates correctly in deterministic relationships."""
        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))
        network.add_variable("B", ("True", "False"))

        # A is equally likely to be True or False
        network.add_factor("A", [], {("True",): 0.5, ("False",): 0.5})

        # B is deterministically True if A is True, and False if A is False
        network.add_factor(
            "B",
            ["A"],
            {
                ("True", "True"): 1.0,
                ("False", "True"): 0.0,
                ("True", "False"): 0.0,
                ("False", "False"): 1.0,
            },
        )

        inference = Inference(network)

        # P(A=True|B=True) should be 1
        result = inference.variable_elimination({"A": None}, {"B": "True"})
        self.assertEqual(result.probabilities[("True",)], 1.0)

        # P(A=False|B=False) should be 1
        result = inference.variable_elimination({"A": None}, {"B": "False"})
        self.assertEqual(result.probabilities[("False",)], 1.0)

    def test_precision_high_probabilities(self):
        """Test calculations involving high precision probability calculations."""
        getcontext().prec = 28  # Set decimal precision to 28 digits

        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))

        # A has a very precise probability of being True
        # Using Decimal for high precision
        probability = float(Decimal("0.999999999999999999999999999"))
        network.add_factor(
            "A", [], {("True",): probability, ("False",): 1 - probability}
        )

        inference = Inference(network)

        # P(A=True) should maintain precision
        result = inference.variable_elimination({"A": None}, {})
        self.assertAlmostEqual(result.probabilities[("True",)], probability, places=25)

    def test_extreme_probabilities_simple(self):
        """Test extremely low/high probabilities in a small network."""
        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))

        # A has an extremely small probability of being False
        network.add_factor("A", [], {("True",): 1 - 1e-15, ("False",): 1e-15})

        inference = Inference(network)

        # P(A=True) should be extremely close to 1
        result = inference.variable_elimination({"A": None}, {})
        self.assertAlmostEqual(result.probabilities[("True",)], 1.0, places=14)

    def test_complex_network_with_extreme_probabilities(self):
        """Test a more complex network with extreme probability values."""
        network = BayesianNetwork()

        # Define variables
        network.add_variable("A", ("True", "False"))  # Root node
        network.add_variable("B", ("True", "False"))  # Depends on A
        network.add_variable("C", ("True", "False"))  # Depends on A
        network.add_variable("D", ("True", "False"))  # Depends on B and C

        # A has a very low probability of being True
        network.add_factor("A", [], {("True",): 1e-10, ("False",): 1.0 - 1e-10})

        # B is strongly influenced by A
        network.add_factor(
            "B",
            ["A"],
            {
                ("True", "True"): 0.99,
                ("False", "True"): 0.01,
                ("True", "False"): 0.001,
                ("False", "False"): 0.999,
            },
        )

        # C is moderately influenced by A
        network.add_factor(
            "C",
            ["A"],
            {
                ("True", "True"): 0.8,
                ("False", "True"): 0.2,
                ("True", "False"): 0.3,
                ("False", "False"): 0.7,
            },
        )

        # D depends on both B and C
        network.add_factor(
            "D",
            ["B", "C"],
            {
                ("True", "True", "True"): 0.95,
                ("False", "True", "True"): 0.05,
                ("True", "False", "True"): 0.75,
                ("False", "False", "True"): 0.25,
                ("True", "True", "False"): 0.65,
                ("False", "True", "False"): 0.35,
                ("True", "False", "False"): 0.02,
                ("False", "False", "False"): 0.98,
            },
        )

        inference = Inference(network)

        # P(A=True,C=True) should compute correctly without underflow
        result = inference.variable_elimination({"A": None, "C": None}, {})
        self.assertNotEqual(
            result.probabilities[("True", "True")], 0.0
        )  # Should not be exactly 0

        # P(A=True|C=True) should compute correctly
        result = inference.variable_elimination({"A": None}, {"C": "True"})
        self.assertNotEqual(
            result.probabilities[("True",)], 0.0
        )  # Should not be exactly 0

        # Testing a more complex query with multiple evidence variables
        result = inference.variable_elimination(
            {"B": None, "D": None}, {"A": "True", "C": "False"}
        )
        # Just verify it computes (no underflow/overflow errors)
        self.assertTrue(0 <= result.probabilities[("True", "True")] <= 1)
