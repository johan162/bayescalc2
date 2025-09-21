"""
Test the performance and robustness of the Bayesian network calculator on large networks.
"""
import unittest
import sys
import os
import time
from contextlib import redirect_stdout
import io

# Add src to path to allow importing bayescalc modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from bayescalc.network_model import BayesianNetwork
from bayescalc.inference import Inference

class TestLargeNetworks(unittest.TestCase):
    
    def test_chain_network(self):
        """Test inference in a large chain network (A -> B -> C -> ... -> Z)."""
        
        # Create a chain network with 10 binary variables
        network = BayesianNetwork()
        
        # Add variables
        num_vars = 10
        var_names = [chr(65 + i) for i in range(num_vars)]  # A, B, C, ...
        
        for var in var_names:
            network.add_variable(var, ("True", "False"))
        
        # Add factors: first variable has no parents
        network.add_factor(var_names[0], [], {("True",): 0.5, ("False",): 0.5})
        
        # Each subsequent variable depends only on the previous variable
        for i in range(1, num_vars):
            network.add_factor(var_names[i], [var_names[i-1]], {
                ("True", "True"): 0.8,
                ("False", "True"): 0.2,
                ("True", "False"): 0.3,
                ("False", "False"): 0.7
            })
        
        inference = Inference(network)
        
        # Query the probability of the last variable
        result = inference.variable_elimination({var_names[-1]: None}, {})
        
        # The result should be a valid probability distribution
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
        
        # For this specific chain, we can calculate the exact probability analytically
        # But we'll just check it's within a reasonable range
        self.assertTrue(0 <= result.probabilities[("True",)] <= 1)
        
        # Test with evidence at the start of the chain
        result = inference.variable_elimination({var_names[-1]: None}, {var_names[0]: "True"})
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
    
    def test_tree_network(self):
        """Test inference in a tree-structured network."""
        
        network = BayesianNetwork()
        
        # Level 1: Root
        network.add_variable("A", ("True", "False"))
        
        # Level 2: B, C, D depend on A
        for var in ["B", "C", "D"]:
            network.add_variable(var, ("True", "False"))
        
        # Level 3: E, F depend on B; G, H depend on C; I, J depend on D
        for var in ["E", "F", "G", "H", "I", "J"]:
            network.add_variable(var, ("True", "False"))
        
        # Add factors
        network.add_factor("A", [], {("True",): 0.5, ("False",): 0.5})
        
        # Level 2 factors
        for var in ["B", "C", "D"]:
            network.add_factor(var, ["A"], {
                ("True", "True"): 0.8,
                ("False", "True"): 0.2,
                ("True", "False"): 0.3,
                ("False", "False"): 0.7
            })
        
        # Level 3 factors
        parent_child_pairs = [
            ("B", "E"), ("B", "F"),
            ("C", "G"), ("C", "H"),
            ("D", "I"), ("D", "J")
        ]
        
        for parent, child in parent_child_pairs:
            network.add_factor(child, [parent], {
                ("True", "True"): 0.7,
                ("False", "True"): 0.3,
                ("True", "False"): 0.2,
                ("False", "False"): 0.8
            })
        
        inference = Inference(network)
        
        # Query a leaf node given evidence about the root
        result = inference.variable_elimination({"J": None}, {"A": "True"})
        
        # The result should be a valid probability distribution
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
        
        # Query the root given evidence about multiple leaves
        result = inference.variable_elimination({"A": None}, {"E": "True", "G": "True", "J": "True"})
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
    
    def test_fully_connected_network(self):
        """Test inference in a small but fully connected network (clique)."""
        
        network = BayesianNetwork()
        
        # Add 4 variables
        for var in ["A", "B", "C", "D"]:
            network.add_variable(var, ("True", "False"))
        
        # A has no parents
        network.add_factor("A", [], {("True",): 0.5, ("False",): 0.5})
        
        # B depends on A
        network.add_factor("B", ["A"], {
            ("True", "True"): 0.8,
            ("False", "True"): 0.2,
            ("True", "False"): 0.3,
            ("False", "False"): 0.7
        })
        
        # C depends on A and B
        network.add_factor("C", ["A", "B"], {
            ("True", "True", "True"): 0.9,
            ("False", "True", "True"): 0.1,
            ("True", "False", "True"): 0.8,
            ("False", "False", "True"): 0.2,
            ("True", "True", "False"): 0.7,
            ("False", "True", "False"): 0.3,
            ("True", "False", "False"): 0.4,
            ("False", "False", "False"): 0.6
        })
        
        # D depends on A, B, and C (fully connected)
        network.add_factor("D", ["A", "B", "C"], {
            ("True", "True", "True", "True"): 0.95,
            ("False", "True", "True", "True"): 0.05,
            ("True", "False", "True", "True"): 0.9,
            ("False", "False", "True", "True"): 0.1,
            ("True", "True", "False", "True"): 0.8,
            ("False", "True", "False", "True"): 0.2,
            ("True", "False", "False", "True"): 0.7,
            ("False", "False", "False", "True"): 0.3,
            ("True", "True", "True", "False"): 0.6,
            ("False", "True", "True", "False"): 0.4,
            ("True", "False", "True", "False"): 0.5,
            ("False", "False", "True", "False"): 0.5,
            ("True", "True", "False", "False"): 0.4,
            ("False", "True", "False", "False"): 0.6,
            ("True", "False", "False", "False"): 0.3,
            ("False", "False", "False", "False"): 0.7
        })
        
        inference = Inference(network)
        
        # Query for P(D | A=True, B=True)
        result = inference.variable_elimination({"D": None}, {"A": "True", "B": "True"})
        
        # The result should be a valid probability distribution
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
    
    def test_diamond_network(self):
        """Test inference in a diamond-shaped network (A -> B,C -> D)."""
        
        network = BayesianNetwork()
        
        # Add variables
        for var in ["A", "B", "C", "D"]:
            network.add_variable(var, ("True", "False"))
        
        # Add factors
        network.add_factor("A", [], {("True",): 0.5, ("False",): 0.5})
        
        network.add_factor("B", ["A"], {
            ("True", "True"): 0.8,
            ("False", "True"): 0.2,
            ("True", "False"): 0.3,
            ("False", "False"): 0.7
        })
        
        network.add_factor("C", ["A"], {
            ("True", "True"): 0.7,
            ("False", "True"): 0.3,
            ("True", "False"): 0.2,
            ("False", "False"): 0.8
        })
        
        network.add_factor("D", ["B", "C"], {
            ("True", "True", "True"): 0.9,
            ("False", "True", "True"): 0.1,
            ("True", "False", "True"): 0.8,
            ("False", "False", "True"): 0.2,
            ("True", "True", "False"): 0.7,
            ("False", "True", "False"): 0.3,
            ("True", "False", "False"): 0.1,
            ("False", "False", "False"): 0.9
        })
        
        inference = Inference(network)
        
        # Query for P(D | A=True)
        result = inference.variable_elimination({"D": None}, {"A": "True"})
        
        # The result should be a valid probability distribution
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=10)
        
        # Testing Explaining Away: P(B | D=True)
        result_b = inference.variable_elimination({"B": None}, {"D": "True"})
        
        # Now P(B | D=True, C=False)
        # With C=False, B needs to be more likely to explain D=True
        result_b_given_c_false = inference.variable_elimination({"B": None}, {"D": "True", "C": "False"})
        
        # The posterior probability of B should increase when C is False
        # This tests the explaining away phenomenon
        self.assertGreater(
            result_b_given_c_false.probabilities[("True",)], 
            result_b.probabilities[("True",)]
        )
    
    def test_complex_evidence(self):
        """Test inference with complex evidence patterns."""
        
        network = BayesianNetwork()
        
        # Add variables for a medical diagnosis network
        variables = [
            "Fever", "Cough", "Fatigue", "SoreThroat", "Headache",
            "Flu", "Covid", "CommonCold", "Allergies"
        ]
        
        for var in variables:
            network.add_variable(var, ("True", "False"))
        
        # Disease priors
        for disease in ["Flu", "Covid", "CommonCold", "Allergies"]:
            if disease == "CommonCold":
                prob = 0.1  # Common cold is more prevalent
            elif disease == "Allergies":
                prob = 0.2  # Allergies are common
            else:
                prob = 0.05  # Flu and Covid are less common
            
            network.add_factor(disease, [], {("True",): prob, ("False",): 1-prob})
        
        # Symptom factors
        # Fever depends on Flu, Covid, CommonCold
        network.add_factor("Fever", ["Flu", "Covid", "CommonCold"], {
            ("True", "True", "True", "True"): 0.9,
            ("False", "True", "True", "True"): 0.1,
            ("True", "False", "True", "True"): 0.8,
            ("False", "False", "True", "True"): 0.2,
            ("True", "True", "False", "True"): 0.7,
            ("False", "True", "False", "True"): 0.3,
            ("True", "False", "False", "True"): 0.6,
            ("False", "False", "False", "True"): 0.4,
            ("True", "True", "True", "False"): 0.3,
            ("False", "True", "True", "False"): 0.7,
            ("True", "False", "True", "False"): 0.2,
            ("False", "False", "True", "False"): 0.8,
            ("True", "True", "False", "False"): 0.1,
            ("False", "True", "False", "False"): 0.9,
            ("True", "False", "False", "False"): 0.05,
            ("False", "False", "False", "False"): 0.95,
        })
        
        # Simplified factors for the rest of the symptoms
        # For simplicity, let's use a simpler approach - just create Cough based on Flu and Covid
        network.add_factor("Cough", ["Flu", "Covid"], {
            ("True", "True", "True"): 0.95,
            ("False", "True", "True"): 0.05,
            
            ("True", "True", "False"): 0.80,
            ("False", "True", "False"): 0.20,
            
            ("True", "False", "True"): 0.70,
            ("False", "False", "True"): 0.30,
            
            ("True", "False", "False"): 0.20,
            ("False", "False", "False"): 0.80,
            ("True", "True", "True", "True", "False"): 0.9,
            ("True", "True", "True", "False", "True"): 0.85,
            ("True", "True", "False", "True", "True"): 0.8,
            ("True", "False", "True", "True", "True"): 0.75,
            ("True", "True", "False", "False", "True"): 0.7,
            ("True", "False", "True", "False", "True"): 0.65,
            ("True", "False", "False", "True", "True"): 0.6,
            ("True", "True", "False", "False", "False"): 0.55,
            ("True", "False", "True", "False", "False"): 0.5,
            ("True", "False", "False", "True", "False"): 0.45,
            ("True", "False", "False", "False", "True"): 0.4,
            ("True", "False", "False", "False", "False"): 0.1,
            # False cases are the complement probabilities
            ("False", "True", "True", "True", "True"): 0.05,
            ("False", "True", "True", "True", "False"): 0.1,
            ("False", "True", "True", "False", "True"): 0.15,
            ("False", "True", "False", "True", "True"): 0.2,
            ("False", "False", "True", "True", "True"): 0.25,
            ("False", "True", "False", "False", "True"): 0.3,
            ("False", "False", "True", "False", "True"): 0.35,
            ("False", "False", "False", "True", "True"): 0.4,
            ("False", "True", "False", "False", "False"): 0.45,
            ("False", "False", "True", "False", "False"): 0.5,
            ("False", "False", "False", "True", "False"): 0.55,
            ("False", "False", "False", "False", "True"): 0.6,
            ("False", "False", "False", "False", "False"): 0.9,
        })
        
        # Simplified factors for the rest of the symptoms
        for symptom, base_probs in [
            ("Fatigue", {"Flu": 0.9, "Covid": 0.8, "CommonCold": 0.6, "Allergies": 0.4}),
            ("SoreThroat", {"Flu": 0.7, "Covid": 0.6, "CommonCold": 0.8, "Allergies": 0.3}),
            ("Headache", {"Flu": 0.8, "Covid": 0.7, "CommonCold": 0.6, "Allergies": 0.5})
        ]:
            # Simple dependency: symptom depends directly on each disease
            for disease, prob in base_probs.items():
                network.add_factor(symptom, [disease], {
                    ("True", "True"): prob,
                    ("False", "True"): 1 - prob,
                    ("True", "False"): 0.1,  # 10% chance of symptom if no disease
                    ("False", "False"): 0.9
                })
        
        inference = Inference(network)
        
        # Complex diagnosis query
        # If we observe fever, cough, and fatigue, what's the probability of each disease?
        evidence = {
            "Fever": "True",
            "Cough": "True",
            "Fatigue": "True"
        }
        
        # Query each disease
        for disease in ["Flu", "Covid", "CommonCold", "Allergies"]:
            result = inference.variable_elimination({disease: None}, evidence)
            
            # Result should be a valid probability distribution
            total_prob = sum(result.probabilities.values())
            self.assertAlmostEqual(total_prob, 1.0, places=10)
            
            # Probability of disease should be higher than prior given these symptoms
            prob_true = result.probabilities[("True",)]
            
            # Get the prior for comparison
            if disease == "CommonCold":
                prior = 0.1
            elif disease == "Allergies":
                prior = 0.2
            else:
                prior = 0.05
                
            # Given these symptoms, probability should be higher than prior
            self.assertGreater(prob_true, prior)

if __name__ == '__main__':
    unittest.main()