"""
Tests for the example networks in the examples directory.
Tests loading and inference for a selected set of examples known to work properly.

This test suite validates that example networks can be properly loaded
and inference can be performed on them. It focuses on a set of the
available examples that demonstrate key Bayesian network concepts.

This test suite also serves as a reference for how to:
1. Load Bayesian networks from files
2. Perform inference using variable elimination
3. Calculate and verify conditional probabilities
"""

import unittest
import os
import sys
from pathlib import Path

# Add src to path to allow importing bayescalc modules
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.inference import Inference


class TestExampleNetworks(unittest.TestCase):

    def test_alarm_network(self):
        """Test inference with the alarm_network.net example."""
        network = self._load_network_from_file("alarm_network.net")
        inference = Inference(network)

        # Test: P(Burglary | Alarm=True)
        result = inference.variable_elimination({"Burglary": None}, {"Alarm": "True"})
        # Prior is 0.001, posterior should be higher
        self.assertGreater(result.probabilities[("True",)], 0.001)

        # Test: P(Alarm | Earthquake=True, Burglary=False)
        result = inference.variable_elimination(
            {"Alarm": None}, {"Earthquake": "True", "Burglary": "False"}
        )
        # Should match the direct CPT value
        self.assertAlmostEqual(result.probabilities[("True",)], 0.29, places=4)

        # Test: P(JohnCalls | Alarm=True)
        result = inference.variable_elimination({"JohnCalls": None}, {"Alarm": "True"})
        # Should match the direct CPT value
        self.assertAlmostEqual(result.probabilities[("True",)], 0.9, places=4)

    def test_rain_sprinkler_grass(self):
        """Test inference with the rain_sprinkler_grass.net example."""
        network = self._load_network_from_file("rain_sprinkler_grass.net")
        inference = Inference(network)

        # Test 1: P(Rain)
        result = inference.variable_elimination({"Rain": None}, {})
        self.assertAlmostEqual(result.probabilities[("True",)], 0.2, places=4)

        # Test 2: P(GrassWet | Rain=True, Sprinkler=True)
        result = inference.variable_elimination(
            {"GrassWet": None}, {"Rain": "True", "Sprinkler": "True"}
        )
        # From the CPT directly
        self.assertAlmostEqual(result.probabilities[("True",)], 0.99, places=4)

    def test_medical_test(self):
        """Test inference with the medical_test.net example."""
        network = self._load_network_from_file("medical_test.net")
        inference = Inference(network)

        # Test: P(Sick)
        result = inference.variable_elimination({"Sick": None}, {})
        # Prior probability from the CPT
        self.assertAlmostEqual(result.probabilities[("True",)], 0.01, places=4)

    def test_rain_sprinkler_boolean(self):
        """Test inference with the rain_sprinkler_boolean.net example."""
        network = self._load_network_from_file("rain_sprinkler_boolean.net")
        inference = Inference(network)

        # Test: P(Rain)
        result = inference.variable_elimination({"Rain": None}, {})
        self.assertAlmostEqual(result.probabilities[("True",)], 0.2, places=4)

    def test_student_network(self):
        """Test inference with the student_network.net example."""
        network = self._load_network_from_file("student_network.net")
        inference = Inference(network)

        # Test: P(Grade | Intelligence=High, Difficulty=Easy)
        result = inference.variable_elimination(
            {"Grade": None}, {"Intelligence": "High", "Difficulty": "Easy"}
        )
        # Verify probabilities sum to 1
        total_prob = sum(result.probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=4)

        # Verify that probabilities make sense (higher probability for better grades)
        self.assertGreater(result.probabilities[("A",)], result.probabilities[("C",)])

    def test_medical_test_short(self):
        """Test inference with the medical_test_short.net example."""
        network = self._load_network_from_file("medical_test_short.net")
        inference = Inference(network)

        # Test: P(Sick)
        result = inference.variable_elimination({"Sick": None}, {})
        self.assertAlmostEqual(result.probabilities[("True",)], 0.01, places=4)

        # Test: P(Sick | Test=T)
        result = inference.variable_elimination({"Sick": None}, {"Test": "T"})
        # Calculate expected result using Bayes rule
        # P(D|T) = P(T|D)P(D)/P(T)
        # P(T) = P(T|D)P(D) + P(T|~D)P(~D) = 0.95*0.01 + 0.06*0.99 = 0.0095 + 0.0594 = 0.0689
        # P(D|T) = 0.95*0.01/0.0689 = 0.0095/0.0689 = 0.1379
        self.assertAlmostEqual(result.probabilities[("True",)], 0.1379, places=3)

    def test_load_basic_examples(self):
        """Test loading a specific subset of example networks."""
        # Examples that are known to work with the parser
        example_files = [
            "alarm_network.net",
            "medical_test.net",
            "rain_sprinkler_boolean.net",
            "rain_sprinkler_grass.net",
            "student_network.net",
            "alarm_with_sensors.net",
            "medical_test_short.net",
        ]

        for filename in example_files:
            with self.subTest(filename=filename):
                network = self._load_network_from_file(filename)
                self.assertIsNotNone(network)
                self.assertGreater(len(network.variables), 0)
                self.assertGreater(len(network.factors), 0)

    def _load_network_from_file(self, filename):
        """Load a Bayesian network from a file in the examples directory."""
        examples_dir = Path(__file__).parent.parent / "examples"
        file_path = examples_dir / filename

        with open(file_path, "r") as file:
            content = file.read()

        lexer = Lexer(content)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_alarm_with_sensors(self):
        """Test inference with the alarm_with_sensors.net example."""
        network = self._load_network_from_file("alarm_with_sensors.net")
        inference = Inference(network)

        # Test: P(Alarm | Burglary=True)
        result = inference.variable_elimination({"Alarm": None}, {"Burglary": "True"})
        # Burglary should increase probability of alarm being triggered
        self.assertGreater(result.probabilities[("True",)], 0.5)

        # Test: P(Sensor1 | Alarm=True)
        result = inference.variable_elimination({"Sensor1": None}, {"Alarm": "True"})
        # Sensor1 should have high probability when alarm is triggered
        self.assertGreater(result.probabilities[("True",)], 0.7)


if __name__ == "__main__":
    unittest.main()
