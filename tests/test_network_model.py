"""
Tests for the network_model module.
"""

import unittest
from bayescalc.network_model import Variable, BayesianNetwork


class TestNetworkModel(unittest.TestCase):

    def test_variable_creation(self):
        var = Variable("TestVar", ("A", "B", "C"))
        self.assertEqual(var.name, "TestVar")
        self.assertEqual(var.domain, ("A", "B", "C"))

    def test_add_variable(self):
        net = BayesianNetwork()
        net.add_variable("Rain", ("True", "False"))
        self.assertIn("Rain", net.variables)
        self.assertEqual(net.variables["Rain"].domain, ("True", "False"))

    def test_add_duplicate_variable_raises_error(self):
        net = BayesianNetwork()
        net.add_variable("Rain", ("True", "False"))
        with self.assertRaises(ValueError):
            net.add_variable("Rain", ("Yes", "No"))

    def test_add_factor_prior(self):
        net = BayesianNetwork()
        net.add_variable("Rain", ("True", "False"))
        net.add_factor("Rain", [], {("True",): 0.2})
        self.assertIn("Rain", net.factors)
        factor = net.factors["Rain"]
        self.assertEqual(factor.probabilities[("True",)], 0.2)
        self.assertAlmostEqual(factor.probabilities[("False",)], 0.8)

    def test_add_factor_conditional(self):
        net = BayesianNetwork()
        net.add_variable("Rain", ("True", "False"))
        net.add_variable("Sprinkler", ("On", "Off"))
        net.add_factor(
            "Sprinkler", ["Rain"], {("On", "True"): 0.01, ("On", "False"): 0.4}
        )
        self.assertIn("Sprinkler", net.factors)
        factor = net.factors["Sprinkler"]
        self.assertEqual(factor.probabilities[("On", "True")], 0.01)
        self.assertAlmostEqual(factor.probabilities[("Off", "True")], 0.99)
        self.assertEqual(factor.probabilities[("On", "False")], 0.4)
        self.assertAlmostEqual(factor.probabilities[("Off", "False")], 0.6)

    def test_cpt_validation_incomplete(self):
        net = BayesianNetwork()
        net.add_variable("Test", ("A", "B", "C"))
        with self.assertRaises(ValueError):
            net.add_factor("Test", [], {("A",): 0.5})

    def test_cpt_validation_sum_error(self):
        net = BayesianNetwork()
        net.add_variable("Test", ("A", "B"))
        with self.assertRaises(ValueError):
            net.add_factor("Test", [], {("A",): 0.5, ("B",): 0.6})

    def test_get_parents_children(self):
        net = BayesianNetwork()
        net.add_variable("A", ("1",))
        net.add_variable("B", ("1",))
        net.add_variable("C", ("1",))
        net.add_factor("B", ["A"], {("1", "1"): 1.0})
        net.add_factor("C", ["A"], {("1", "1"): 1.0})

        self.assertEqual(net.get_parents("A"), set())
        self.assertEqual(net.get_children("A"), {"B", "C"})
        self.assertEqual(net.get_parents("B"), {"A"})
        self.assertEqual(net.get_children("B"), set())


if __name__ == "__main__":
    unittest.main()
