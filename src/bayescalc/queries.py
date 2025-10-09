"""
This module handles parsing and executing probability queries.
"""

import re
from typing import List, Dict, Tuple

from .network_model import BayesianNetwork
from .inference import Inference


class QueryParser:
    def __init__(self, network: BayesianNetwork):
        self.network = network
        self.inference = Inference(network)

    def _parse_query_string(self, query_str: str) -> Tuple[str, str]:
        """
        Parses the query string using regex to extract query and evidence parts.

        Parameters:
        -----------
        query_str : str
            The probability query string in format P(A, B=b | C=c, D=d)

        Returns:
        --------
        Tuple[str, str]
            A tuple containing (query_part, evidence_part)

        Raises:
        -------
        ValueError
            If the query string format is invalid
        """
        # Simple regex for P(A, B=b | C=c, D=d)
        match = re.match(r"P\(([^|]+)\|?([^)]*)\)", query_str.replace(" ", ""))
        if not match:
            raise ValueError(f"Invalid query format: {query_str}")

        query_part = match.group(1)
        evidence_part = match.group(2)

        return query_part, evidence_part

    def _validate_and_normalize_values(
        self,
        query_vars_names: List[str],
        evidence: Dict[str, str],
        query_evidence: Dict[str, str],
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Validates all variables and values in the query and evidence.
        Normalizes boolean shorthand (T/F) to full form (True/False).

        Parameters:
        -----------
        query_vars_names : List[str]
            List of variable names in the query part
        evidence : Dict[str, str]
            Dictionary of evidence variable assignments
        query_evidence : Dict[str, str]
            Dictionary of query variable assignments

        Returns:
        --------
        Tuple[Dict[str, str], Dict[str, str]]
            Tuple containing normalized (evidence, query_evidence)

        Raises:
        -------
        ValueError
            If a variable is not in the network or a value is not in the domain of its variable
        """
        # Validate that all variables exist in the network
        all_vars_in_query = query_vars_names + list(evidence.keys())
        for var in all_vars_in_query:
            if var not in self.network.variables:
                raise ValueError(f"Variable '{var}' not in network")

        # Normalize and validate values
        for var, val in {**evidence, **query_evidence}.items():
            # If value is a boolean shorthand (T/F), convert it to full form (True/False)
            if self.network.variables[var].is_boolean:
                if val == "T":
                    val = "True"
                elif val == "F":
                    val = "False"
                # Update the evidence with the full form
                if var in evidence and evidence[var] in ["T", "F"]:
                    evidence[var] = val
                if var in query_evidence and query_evidence[var] in ["T", "F"]:
                    query_evidence[var] = val

            # Validate that values are in the domain of their variables
            if val not in self.network.variables[var].domain:
                # Special handling for boolean values to accept T/F as True/False
                if self.network.variables[var].is_boolean:
                    if (
                        val == "T" and "True" in self.network.variables[var].domain
                    ) or (val == "F" and "False" in self.network.variables[var].domain):
                        continue
                raise ValueError(f"Value '{val}' not in domain of variable '{var}'")

        return evidence, query_evidence

    def _parse_evidence_variables(self, evidence_part: str) -> Dict[str, str]:
        """
        Parses the evidence part of a probability query to extract variable assignments.

        Parameters:
        -----------
        evidence_part : str
            The evidence part of a probability query (e.g., "C=c, D=d" from P(... | C=c, D=d))

        Returns:
        --------
        Dict[str, str]
            Dictionary mapping evidence variable names to their values

        Raises:
        -------
        ValueError
            If a variable doesn't exist in the network, negation is used with non-boolean variables,
            or a non-boolean variable is missing a value
        """
        evidence: Dict[str, str] = {}

        if not evidence_part:
            return evidence

        for item in evidence_part.split(","):
            item = item.strip()

            # Handle negation in evidence
            if item.startswith("~"):
                var_name = item[1:].strip()
                if var_name not in self.network.variables:
                    raise ValueError(f"Variable '{var_name}' not in network")

                if not self.network.variables[var_name].is_boolean:
                    raise ValueError(
                        f"Negation (~) can only be used with boolean variables, but '{var_name}' is not boolean"
                    )

                evidence[var_name] = "False"
                continue

            # Standard evidence format
            if "=" in item:
                var, val = item.split("=")
                var, val = var.strip(), val.strip()
                evidence[var] = val
            else:
                # For boolean variables without value, assume True
                var_name = item.strip()
                if (
                    var_name in self.network.variables
                    and self.network.variables[var_name].is_boolean
                ):
                    evidence[var_name] = "True"
                else:
                    raise ValueError(
                        f"Non-boolean variable '{var_name}' must specify a value in evidence"
                    )

        return evidence

    def _parse_query_variables(
        self, query_part: str
    ) -> Tuple[List[str], Dict[str, str]]:
        """
        Parses the query part of a probability query to extract variable names and values.

        Parameters:
        -----------
        query_part : str
            The query part of a probability query (e.g., "A, B=b" from P(A, B=b | ...))

        Returns:
        --------
        Tuple[List[str], Dict[str, str]]
            A tuple containing:
            - List of query variable names
            - Dictionary mapping variable names to their values (if specified)

        Raises:
        -------
        ValueError
            If a variable doesn't exist in the network or negation is used with non-boolean variables
        """
        query_vars_names: List[str] = []
        query_evidence: Dict[str, str] = {}

        if not query_part:
            return query_vars_names, query_evidence

        for item in query_part.split(","):
            item = item.strip()

            # Handle negation for boolean variables (~Var means Var=False)
            if item.startswith("~"):
                var_name = item[1:].strip()  # Remove the ~ prefix
                if var_name not in self.network.variables:
                    raise ValueError(f"Variable '{var_name}' not in network")

                if not self.network.variables[var_name].is_boolean:
                    raise ValueError(
                        f"Negation (~) can only be used with boolean variables, but '{var_name}' is not boolean"
                    )

                query_vars_names.append(var_name)
                query_evidence[var_name] = "False"
                continue

            # Handle standard variable=value format
            if "=" in item:
                var, val = item.split("=")
                var, val = var.strip(), val.strip()
                query_vars_names.append(var)
                query_evidence[var] = val
            else:
                # For boolean variables without value, assume True
                var_name = item.strip()
                query_vars_names.append(var_name)

                # If it's a boolean variable with no value specified, assume True
                if (
                    var_name in self.network.variables
                    and self.network.variables[var_name].is_boolean
                ):
                    query_evidence[var_name] = "True"

        return query_vars_names, query_evidence

    def _execute_inference(
        self,
        query_vars_names: List[str],
        evidence: Dict[str, str],
        query_evidence: Dict[str, str],
    ):
        """
        Executes inference using variable elimination and processes the results.

        Parameters:
        -----------
        query_vars_names : List[str]
            List of variable names to query
        evidence : Dict[str, str]
            Dictionary of evidence variable assignments
        query_evidence : Dict[str, str]
            Dictionary of query variable assignments

        Returns:
        --------
        Factor
            A Factor object representing the query result

        Raises:
        -------
        ValueError
            If the specified assignment cannot be found in the result
        """

        query_vars_dict: Dict[str, str | None] = {}
        for var_name in query_vars_names:
            if var_name in query_evidence:
                # If we have a specific value for this variable, use it
                query_vars_dict[var_name] = query_evidence[var_name]
            else:
                # If no specific value, query all values (marginal query)
                query_vars_dict[var_name] = None

        result_factor = self.inference.variable_elimination(query_vars_dict, evidence)

        # Perform inference using variable elimination
        # result_factor = self.inference.variable_elimination(query_vars_names, evidence)

        # If the original query had specific values (e.g., P(Rain=True|...)),
        # we need to filter the final result to get that single probability.
        if query_evidence:
            # The result_factor contains the distribution, e.g., P(Rain|GrassWet=Yes).
            # We need to find the assignment that matches our query_evidence.

            # The factor's variables define the order in the assignment tuples.
            # e.g., if factor.variables is (Var1, Var2), an assignment is (val1, val2)
            try:
                assignment_tuple = tuple(
                    query_evidence[var.name] for var in result_factor.variables
                )
                prob = result_factor.probabilities[assignment_tuple]

                from .network_model import Factor

                final_assignment_str = ", ".join(
                    [f"{k}={v}" for k, v in query_evidence.items()]
                )
                if evidence:
                    final_assignment_str += " | " + ", ".join(
                        [f"{k}={v}" for k, v in evidence.items()]
                    )

                return Factor(
                    variables=tuple(),
                    probabilities={tuple(): prob},
                    name=f"P({final_assignment_str})",
                )

            except (KeyError, StopIteration):
                raise ValueError(
                    "Could not find the specified assignment in the result."
                )

        return result_factor

    def parse_and_execute(self, query_str: str):
        """
        Parses a probability query string and executes inference on the Bayesian network.

        This method coordinates the parsing, validation, and inference process by calling
        the specialized helper methods that handle specific parts of the query.

        Parameters:
        -----------
        query_str : str
            The probability query string in format P(A, B=b | C=c, D=d)

        Returns:
        --------
        Factor
            A Factor object representing the query result

        Raises:
        -------
        ValueError
            If the query string format is invalid, variables don't exist in the network,
            values are not in the domain of their variables, or other validation errors occur
        """
        # Parse the query string to get query part and evidence part
        query_part, evidence_part = self._parse_query_string(query_str)

        # Parse the query variables
        query_vars_names, query_evidence = self._parse_query_variables(query_part)

        # Parse the evidence variables
        evidence = self._parse_evidence_variables(evidence_part)

        # Validate variables and values, normalizing T/F to True/False if needed
        evidence, query_evidence = self._validate_and_normalize_values(
            query_vars_names, evidence, query_evidence
        )

        # Execute the inference and process the results
        return self._execute_inference(query_vars_names, evidence, query_evidence)


if __name__ == "__main__":
    # Example usage for testing
    from .lexer import Lexer
    from .parser import Parser

    example_net = """
    variable Rain {True, False}
    variable Sprinkler {On, Off}
    variable GrassWet {Yes, No}

    Rain { P(True) = 0.2 }
    Sprinkler | Rain {
        P(On | True) = 0.01
        P(On | False) = 0.4
    }
    GrassWet | Rain, Sprinkler {
        P(Yes | True, On) = 0.99
        P(Yes | True, Off) = 0.8
        P(Yes | False, On) = 0.9
        P(Yes | False, Off) = 0.1
    }
    """
    lexer = Lexer(example_net)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    network = parser.parse()

    query_parser = QueryParser(network)

    # Test query: P(Rain | GrassWet=Yes)
    query_str = "P(Rain | GrassWet=Yes)"
    try:
        result = query_parser.parse_and_execute(query_str)
        print(f"Query: {query_str}")
        for assignment, prob in result.probabilities.items():
            print(f"  P({', '.join(assignment)}) = {prob:.4f}")
    except ValueError as e:
        print(f"Error: {e}")

    # Test query: P(GrassWet)
    query_str = "P(GrassWet)"
    try:
        result = query_parser.parse_and_execute(query_str)
        print(f"Query: {query_str}")
        for assignment, prob in result.probabilities.items():
            print(f"  P({', '.join(assignment)}) = {prob:.4f}")
    except ValueError as e:
        print(f"Error: {e}")

    # Test query: P(Rain, Sprinkler | GrassWet=No)
    query_str = "P(Rain, Sprinkler=Off | GrassWet=No)"
    try:
        result = query_parser.parse_and_execute(query_str)
        print(f"Query: {query_str}")
        for assignment, prob in result.probabilities.items():
            print(f"  P({', '.join(assignment)}) = {prob:.4f}")
    except ValueError as e:
        print(f"Error: {e}")
