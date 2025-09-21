"""
Test numerical edge cases and robustness of the variable elimination algorithm.
"""
import unittest
import sys
import os
import io
import math
from contextlib import redirect_stdout

# Add src to path to allow importing bayescalc modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from bayescalc.network_model import BayesianNetwork, Factor, Variable
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.inference import Inference
from bayescalc.queries import QueryParser

class TestAdvancedNumericalCases(unittest.TestCase):
    
    def test_extreme_probability_values(self):
        """Test inference with extreme probability values."""
        
        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))
        network.add_variable("B", ("True", "False"))
        
        # A has extremely small probability of True
        network.add_factor("A", [], {("True",): 1e-10, ("False",): 1.0 - 1e-10})
        
        # B has extremely large difference between True and False given A
        network.add_factor("B", ["A"], {
            ("True", "True"): 0.99999999,
            ("False", "True"): 0.00000001,
            ("True", "False"): 1e-9,
            ("False", "False"): 1.0 - 1e-9
        })
        
        inference = Inference(network)
        
        # Query for P(B | A=True)
        result = inference.variable_elimination({"B": None}, {"A": "True"})
        
        # Should still get sensible result despite extreme values
        self.assertAlmostEqual(result.probabilities[("True",)], 0.99999999, places=7)
        
        # Query for P(A | B=True)
        # This tests Bayes rule with extreme values
        result = inference.variable_elimination({"A": None}, {"B": "True"})
        self.assertTrue(0 <= result.probabilities[("True",)] <= 1)
    
    def test_zero_probability_handling(self):
        """Test handling of true zero probabilities."""
        
        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))
        network.add_variable("B", ("True", "False"))
        network.add_variable("C", ("True", "False"))
        
        # A is 50/50
        network.add_factor("A", [], {("True",): 0.5, ("False",): 0.5})
        
        # B is deterministically related to A
        network.add_factor("B", ["A"], {
            ("True", "True"): 1.0,  # If A=True, B=True with probability 1
            ("False", "True"): 0.0,  # If A=True, B=False with probability 0
            ("True", "False"): 0.0,  # If A=False, B=True with probability 0
            ("False", "False"): 1.0   # If A=False, B=False with probability 1
        })
        
        # C depends on both A and B
        network.add_factor("C", ["A", "B"], {
            ("True", "True", "True"): 0.8,
            ("False", "True", "True"): 0.2,
            ("True", "False", "True"): 0.0,  # C can never be True if B is False
            ("False", "False", "True"): 1.0,  # Must sum to 1.0
            ("True", "True", "False"): 0.4,
            ("False", "True", "False"): 0.6,
            ("True", "False", "False"): 0.3,
            ("False", "False", "False"): 0.7,  # Ensure each condition sums to 1.0
            ("False", "False", "False"): 0.7
        })
        
        inference = Inference(network)
        
        # Query with impossible evidence combination: A=True, B=False
        # This combination has zero probability in the model
        result = inference.variable_elimination({"C": None}, {"A": "True", "B": "False"})
        
        # Should still return a result with valid probabilities that sum to 1
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=5)
    
    def test_floating_point_precision(self):
        """Test handling of floating point precision issues."""
        
        network = BayesianNetwork()
        network.add_variable("A", ("True", "False"))
        network.add_variable("B", ("True", "False"))
        
        # Use values that don't add up to exactly 1 due to floating point
        network.add_factor("A", [], {("True",): 0.3333333333333333, ("False",): 0.6666666666666667})
        
        # These values add up to slightly more than 1 due to floating point
        network.add_factor("B", ["A"], {
            ("True", "True"): 0.5000000000000001,  # Note the extra precision
            ("False", "True"): 0.5,
            ("True", "False"): 0.4999999999999999,  # Note the lost precision
            ("False", "False"): 0.5
        })
        
        inference = Inference(network)
        
        # Run inference
        result = inference.variable_elimination({"B": None}, {})
        
        # Should still get valid probabilities that sum to 1
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
    
    def test_large_network_elimination_order(self):
        """Test variable elimination with different elimination orders."""
        
        network = BayesianNetwork()
        
        # Create a moderately large network with 5 variables
        network.add_variable("A", ("True", "False"))
        network.add_variable("B", ("True", "False"))
        network.add_variable("C", ("True", "False"))
        network.add_variable("D", ("True", "False"))
        network.add_variable("E", ("True", "False"))
        
        # Add factors to create a structure: A -> B -> C -> D -> E
        network.add_factor("A", [], {("True",): 0.4, ("False",): 0.6})
        
        network.add_factor("B", ["A"], {
            ("True", "True"): 0.8,
            ("False", "True"): 0.2,
            ("True", "False"): 0.3,
            ("False", "False"): 0.7
        })
        
        network.add_factor("C", ["B"], {
            ("True", "True"): 0.9,
            ("False", "True"): 0.1,
            ("True", "False"): 0.2,
            ("False", "False"): 0.8
        })
        
        network.add_factor("D", ["C"], {
            ("True", "True"): 0.7,
            ("False", "True"): 0.3,
            ("True", "False"): 0.1,
            ("False", "False"): 0.9
        })
        
        network.add_factor("E", ["D"], {
            ("True", "True"): 0.6,
            ("False", "True"): 0.4,
            ("True", "False"): 0.2,
            ("False", "False"): 0.8
        })
        
        inference = Inference(network)
        
        # Query for P(E | A=True)
        # This requires eliminating B, C, D in some order
        result = inference.variable_elimination({"E": None}, {"A": "True"})
        
        # The result should be a valid probability distribution
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
        
        # This tests both the variable elimination algorithm and the internal
        # heuristic for choosing elimination order
    
    def test_independence_in_inference(self):
        """Test inference with independent variables."""
        
        network = BayesianNetwork()
        
        # Create two independent variables
        network.add_variable("A", ("True", "False"))
        network.add_variable("B", ("True", "False"))
        
        network.add_factor("A", [], {("True",): 0.3, ("False",): 0.7})
        network.add_factor("B", [], {("True",): 0.6, ("False",): 0.4})
        
        inference = Inference(network)
        
        # Query P(B | A=True)
        # Since they're independent, P(B|A) = P(B)
        result = inference.variable_elimination({"B": None}, {"A": "True"})
        
        # Should get P(B=True) = 0.6
        self.assertAlmostEqual(result.probabilities[("True",)], 0.6, places=10)
        
        # Query P(A,B)
        result = inference.variable_elimination({"A": None, "B": None}, {})
        
        # Should get P(A=True,B=True) = 0.3 * 0.6 = 0.18
        self.assertAlmostEqual(result.probabilities[("True", "True")], 0.18, places=10)
    
    def test_multi_valued_variables(self):
        """Test inference with multi-valued (non-boolean) variables."""
        
        network = BayesianNetwork()
        
        # Create variables with more than 2 values
        network.add_variable("Weather", ("Sunny", "Cloudy", "Rainy"))
        network.add_variable("Mood", ("Happy", "Neutral", "Sad"))
        
        # Weather probabilities
        network.add_factor("Weather", [], {
            ("Sunny",): 0.6,
            ("Cloudy",): 0.3,
            ("Rainy",): 0.1
        })
        
        # Mood depends on Weather
        network.add_factor("Mood", ["Weather"], {
            ("Happy", "Sunny"): 0.8,
            ("Neutral", "Sunny"): 0.15,
            ("Sad", "Sunny"): 0.05,
            ("Happy", "Cloudy"): 0.4,
            ("Neutral", "Cloudy"): 0.5,
            ("Sad", "Cloudy"): 0.1,
            ("Happy", "Rainy"): 0.1,
            ("Neutral", "Rainy"): 0.3,
            ("Sad", "Rainy"): 0.6
        })
        
        inference = Inference(network)
        
        # Query for P(Mood | Weather=Rainy)
        result = inference.variable_elimination({"Mood": None}, {"Weather": "Rainy"})
        
        # Check the result is a valid probability distribution
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
        
        # Check specific values
        self.assertAlmostEqual(result.probabilities[("Happy",)], 0.1, places=10)
        self.assertAlmostEqual(result.probabilities[("Sad",)], 0.6, places=10)

    def test_variable_elimination_complex_queries(self):
        """Test complex queries using variable elimination."""
        
        network = BayesianNetwork()
        
        # Create a moderately complex network
        network.add_variable("Burglary", ("True", "False"))
        network.add_variable("Earthquake", ("True", "False"))
        network.add_variable("Alarm", ("True", "False"))
        network.add_variable("JohnCalls", ("True", "False"))
        network.add_variable("MaryCalls", ("True", "False"))
        
        # Prior probabilities
        network.add_factor("Burglary", [], {("True",): 0.001, ("False",): 0.999})
        network.add_factor("Earthquake", [], {("True",): 0.002, ("False",): 0.998})
        
        # Alarm depends on Burglary and Earthquake
        network.add_factor("Alarm", ["Burglary", "Earthquake"], {
            ("True", "True", "True"): 0.95,
            ("False", "True", "True"): 0.05,
            ("True", "True", "False"): 0.94,
            ("False", "True", "False"): 0.06,
            ("True", "False", "True"): 0.29,
            ("False", "False", "True"): 0.71,
            ("True", "False", "False"): 0.001,
            ("False", "False", "False"): 0.999
        })
        
        # JohnCalls depends on Alarm
        network.add_factor("JohnCalls", ["Alarm"], {
            ("True", "True"): 0.9,
            ("False", "True"): 0.1,
            ("True", "False"): 0.05,
            ("False", "False"): 0.95
        })
        
        # MaryCalls depends on Alarm
        network.add_factor("MaryCalls", ["Alarm"], {
            ("True", "True"): 0.7,
            ("False", "True"): 0.3,
            ("True", "False"): 0.01,
            ("False", "False"): 0.99
        })
        
        inference = Inference(network)
        
        # Query for P(Burglary | JohnCalls=True, MaryCalls=True)
        result = inference.variable_elimination({"Burglary": None}, {"JohnCalls": "True", "MaryCalls": "True"})
        
        # The result should be a valid probability distribution
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
        
        # P(Burglary=True | JohnCalls=True, MaryCalls=True) should be around 0.284
        # This is an approximate value for the classic Burglar Alarm example
        self.assertGreater(result.probabilities[("True",)], 0.2)
        self.assertLess(result.probabilities[("True",)], 0.4)

if __name__ == '__main__':
    unittest.main()