"""
Tests that all example .net files can be loaded without errors or warnings.
"""

import unittest
import sys
import os
import warnings
import glob


class TestExampleFilesLoad(unittest.TestCase):
    """
    Test that all example network files can be loaded successfully
    without errors or warnings.
    """

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        sys.path.insert(
            0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        )

        # Get the examples directory path
        cls.examples_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "examples")
        )

        # Get all .net files
        cls.net_files = glob.glob(os.path.join(cls.examples_dir, "*.net"))
        cls.net_files.sort()  # Sort for consistent test ordering

    def test_examples_directory_exists(self):
        """Test that the examples directory exists."""
        self.assertTrue(
            os.path.exists(self.examples_dir),
            f"Examples directory not found at {self.examples_dir}",
        )

    def test_net_files_found(self):
        """Test that at least some .net files were found."""
        self.assertGreater(
            len(self.net_files), 0, f"No .net files found in {self.examples_dir}"
        )
        print(f"\nFound {len(self.net_files)} .net files to test")

    def test_all_example_files_load_without_errors(self):
        """Test that all example files can be loaded without errors."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        failed_files = []

        for net_file in self.net_files:
            filename = os.path.basename(net_file)

            with self.subTest(file=filename):
                try:
                    with open(net_file, "r") as f:
                        net_str = f.read()

                    lexer = Lexer(net_str)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    network = parser.parse()

                    # Basic validation
                    self.assertIsNotNone(network, f"Network is None for {filename}")
                    self.assertGreater(
                        len(network.variables), 0, f"No variables found in {filename}"
                    )

                except Exception as e:
                    failed_files.append((filename, str(e)))
                    self.fail(f"Failed to load {filename}: {e}")

        # If any files failed, print summary
        if failed_files:
            print("\n\nFailed files:")
            for filename, error in failed_files:
                print(f"  - {filename}: {error}")

    def test_all_example_files_load_without_warnings(self):
        """Test that all example files can be loaded without deprecation warnings."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        files_with_warnings = []

        for net_file in self.net_files:
            filename = os.path.basename(net_file)

            with self.subTest(file=filename):
                try:
                    with open(net_file, "r") as f:
                        net_str = f.read()

                    # Capture warnings
                    with warnings.catch_warnings(record=True) as w:
                        warnings.simplefilter("always")

                        lexer = Lexer(net_str)
                        tokens = lexer.tokenize()
                        parser = Parser(tokens)
                        _ = parser.parse()

                        # Check for deprecation warnings
                        deprecation_warnings = [
                            warning
                            for warning in w
                            if issubclass(warning.category, DeprecationWarning)
                        ]

                        if deprecation_warnings:
                            warning_messages = [
                                str(warning.message) for warning in deprecation_warnings
                            ]
                            files_with_warnings.append((filename, warning_messages))
                            self.fail(
                                f"{filename} has {len(deprecation_warnings)} "
                                f"deprecation warning(s): {warning_messages[0]}"
                            )

                except Exception as e:
                    self.fail(f"Failed to load {filename}: {e}")

        # If any files had warnings, print summary
        if files_with_warnings:
            print("\n\nFiles with deprecation warnings:")
            for filename, messages in files_with_warnings:
                print(f"  - {filename}:")
                for msg in messages:
                    print(f"      {msg}")

    def test_each_example_file_individually(self):
        """
        Test each example file individually with detailed output.
        This makes it easier to identify which specific file has issues.
        """
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        results = []

        for net_file in self.net_files:
            filename = os.path.basename(net_file)

            try:
                with open(net_file, "r") as f:
                    net_str = f.read()

                # Capture warnings
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")

                    lexer = Lexer(net_str)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    network = parser.parse()

                    num_vars = len(network.variables)
                    num_factors = len(network.factors)

                    deprecation_warnings = [
                        warning
                        for warning in w
                        if issubclass(warning.category, DeprecationWarning)
                    ]

                    results.append(
                        {
                            "file": filename,
                            "success": True,
                            "variables": num_vars,
                            "factors": num_factors,
                            "warnings": len(deprecation_warnings),
                        }
                    )

            except Exception as e:
                results.append(
                    {
                        "file": filename,
                        "success": False,
                        "error": str(e),
                        "variables": 0,
                        "factors": 0,
                        "warnings": 0,
                    }
                )

        # Print summary
        print("\n\nExample Files Loading Summary:")
        print("=" * 80)
        print(f"{'File':<40} {'Status':<10} {'Vars':<6} {'Factors':<8} {'Warnings':<8}")
        print("-" * 80)

        for result in results:
            if result["success"]:
                status = "✓ PASS"
                details = f"{result['variables']:<6} {result['factors']:<8} {result['warnings']:<8}"
            else:
                status = "✗ FAIL"
                details = result.get("error", "Unknown error")[:40]

            print(f"{result['file']:<40} {status:<10} {details}")

        print("=" * 80)

        # Count successes
        successes = sum(1 for r in results if r["success"])
        total = len(results)
        print(f"Total: {successes}/{total} files loaded successfully")

        # All files should load successfully
        self.assertEqual(
            successes,
            total,
            f"Not all example files loaded successfully: {successes}/{total}",
        )

    def test_example_files_have_valid_structure(self):
        """Test that loaded networks have valid structure."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser

        for net_file in self.net_files:
            filename = os.path.basename(net_file)

            with self.subTest(file=filename):
                with open(net_file, "r") as f:
                    net_str = f.read()

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")

                    lexer = Lexer(net_str)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    network = parser.parse()

                    # Validate network structure
                    self.assertIsNotNone(network.variables)
                    self.assertIsNotNone(network.factors)

                    # Each variable should have a factor
                    for var_name in network.variables.keys():
                        self.assertIn(
                            var_name,
                            network.factors,
                            f"{filename}: Variable {var_name} has no factor",
                        )

                    # Each factor should reference existing variables
                    for factor_var, factor in network.factors.items():
                        self.assertIn(
                            factor_var,
                            network.variables,
                            f"{filename}: Factor for {factor_var} references non-existent variable",
                        )

                        # Check that parent variables exist
                        for parent in factor.variables:
                            # parent is a Variable object, so get its name
                            parent_name = (
                                parent.name if hasattr(parent, "name") else str(parent)
                            )
                            if parent_name != factor_var:
                                self.assertIn(
                                    parent_name,
                                    network.variables,
                                    f"{filename}: Factor for {factor_var} references non-existent parent {parent_name}",
                                )

    def test_example_files_can_perform_basic_queries(self):
        """Test that basic queries can be performed on each network."""
        from bayescalc.lexer import Lexer
        from bayescalc.parser import Parser
        from bayescalc.queries import QueryParser

        for net_file in self.net_files:
            filename = os.path.basename(net_file)

            with self.subTest(file=filename):
                with open(net_file, "r") as f:
                    net_str = f.read()

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")

                    lexer = Lexer(net_str)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    network = parser.parse()

                    # Try to query the first variable
                    if len(network.variables) > 0:
                        first_var = list(network.variables.keys())[0]
                        first_domain = network.variables[first_var].domain
                        first_value = first_domain[0]

                        # Create a simple query
                        query = f"P({first_var}={first_value})"

                        try:
                            qp = QueryParser(network)
                            result = qp.parse_and_execute(query)

                            self.assertIsNotNone(
                                result, f"{filename}: Query {query} returned None"
                            )
                            self.assertGreater(
                                len(result.probabilities),
                                0,
                                f"{filename}: Query {query} returned no probabilities",
                            )

                            # Check that probability is valid
                            prob = list(result.probabilities.values())[0]
                            self.assertGreaterEqual(
                                prob, 0.0, f"{filename}: Probability is negative"
                            )
                            self.assertLessEqual(
                                prob, 1.0, f"{filename}: Probability is greater than 1"
                            )

                        except Exception as e:
                            self.fail(
                                f"{filename}: Failed to execute query {query}: {e}"
                            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
