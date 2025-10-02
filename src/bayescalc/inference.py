"""
Inference algorithms for Bayesian Networks.

This module provides implementation of exact inference algorithms for Bayesian networks,
specifically the variable elimination algorithm. It allows for computing marginal and
conditional probabilities in Bayesian networks by manipulating factors (conditional
probability tables) through operations like joining (multiplication) and
marginalization (summing out).

The main class is Inference, which takes a BayesianNetwork object and provides
methods for performing probabilistic inference on that network.

Key Components:
--------------
- Inference: Main class for performing probabilistic inference
- Factor operations: Joining factors and summing out variables
- Variable elimination: Algorithm for computing conditional probabilities

Example Usage:
-------------
>>> from bayescalc.lexer import Lexer
>>> from bayescalc.parser import Parser
>>> from bayescalc.inference import Inference
>>>
>>> # Define and parse a simple Bayesian network
>>> network_text = '''
... variable Rain {True, False}
... variable Sprinkler {True, False}
... variable GrassWet {True, False}
...
... Rain { P(True) = 0.2 }
...
... Sprinkler | Rain {
...     P(True | True) = 0.01
...     P(True | False) = 0.4
... }
...
... GrassWet | Rain, Sprinkler {
...     P(True | True, True) = 0.99
...     P(True | True, False) = 0.8
...     P(True | False, True) = 0.9
...     P(True | False, False) = 0.0
... }
... '''
>>> network = Parser(Lexer(network_text).tokenize()).parse()
>>>
>>> # Create inference engine and perform a query
>>> inference = Inference(network)
>>> result = inference.variable_elimination({"Rain": None}, {"GrassWet": "True"})
>>>
>>> # Print the result: P(Rain | GrassWet=True)
>>> for assignment, prob in result.probabilities.items():
...     print(f"P(Rain={assignment[0]} | GrassWet=True) = {prob:.4f}")
"""

from typing import Dict
from itertools import product

from .network_model import BayesianNetwork, Factor, Variable


class Inference:
    """
    The central class for performing probabilistic inference on Bayesian networks.

    This class implements algorithms for exact inference in Bayesian networks,
    particularly the variable elimination algorithm. It provides methods to compute
    marginal and conditional probabilities by manipulating factors (conditional
    probability tables) through operations like joining (multiplication) and
    marginalization (summing out variables).

    The main workflow with this class is:
    1. Create an Inference object with a BayesianNetwork
    2. Use variable_elimination() to perform queries on the network

    Attributes:
    -----------
    network : BayesianNetwork
        The Bayesian network on which inference will be performed.

    Methods:
    --------
    variable_elimination(query_vars, evidence):
        Performs inference to compute P(query_vars | evidence)
    _join_factors(factor1, factor2):
        Helper method to multiply two factors
    _sum_out(factor, var_to_sum_out):
        Helper method to marginalize (sum out) a variable from a factor

    Examples:
    ---------
    >>> from bayescalc.lexer import Lexer
    >>> from bayescalc.parser import Parser
    >>> from bayescalc.inference import Inference
    >>>
    >>> # Parse a Bayesian network
    >>> network = Parser(Lexer(network_text).tokenize()).parse()
    >>>
    >>> # Create inference engine
    >>> inference = Inference(network)
    >>>
    >>> # Compute P(Rain | GrassWet=True)
    >>> result = inference.variable_elimination({"Rain": None}, {"GrassWet": "True"})
    >>> print(result.probabilities)
    """

    def __init__(self, network: BayesianNetwork):
        """
        Initialize an inference engine with a Bayesian network.

        Parameters:
        -----------
        network : BayesianNetwork
            The Bayesian network model on which inference will be performed.
        """
        self.network = network

    def _join_factors(self, factor1: Factor, factor2: Factor) -> Factor:
        """
        Joins (multiplies) two factors to create a new combined factor.

        This is a key operation in variable elimination, where factors containing
        the variable to be eliminated are multiplied together. The result is a factor
        defined over the union of the variables in the input factors, with probabilities
        calculated as the product of the corresponding probabilities from the input factors.

        Mathematical definition:
        For factors f(X) and g(Y), the joined factor h(X,Y) is defined as:
        h(x,y) = f(x) × g(y) for all assignments x to X and y to Y

        Parameters:
        -----------
        factor1 : Factor
            The first factor to join
        factor2 : Factor
            The second factor to join

        Returns:
        --------
        Factor
            A new factor representing the product of the input factors

        Example:
        --------
        For factor1 representing P(A) and factor2 representing P(B|A):
        - factor1 might have variables [A] and probabilities {('True',): 0.2, ('False',): 0.8}
        - factor2 might have variables [B, A] and probabilities
          {('True', 'True'): 0.7, ('True', 'False'): 0.1, ('False', 'True'): 0.3, ('False', 'False'): 0.9}

        Joining these would create a factor with variables [A, B] and probabilities:
        {
            ('True', 'True'): 0.2 * 0.7 = 0.14,
            ('True', 'False'): 0.2 * 0.3 = 0.06,
            ('False', 'True'): 0.8 * 0.1 = 0.08,
            ('False', 'False'): 0.8 * 0.9 = 0.72
        }

        Note that the resulting factor contains the joint probability distribution P(A,B).
        """
        # New variables are the union of the variables in the two factors
        vars1 = set(factor1.variables)
        vars2 = set(factor2.variables)
        new_vars_tuple = tuple(vars1.union(vars2))

        new_factor = Factor(new_vars_tuple)

        # Create a mapping from the new variable order to the old orders
        map1 = [new_vars_tuple.index(v) for v in factor1.variables]
        map2 = [new_vars_tuple.index(v) for v in factor2.variables]

        # Get the domains for the new set of variables
        new_domains = [v.domain for v in new_vars_tuple]

        for assignment in product(*new_domains):
            # Extract the parts of the assignment corresponding to each original factor
            ass1 = tuple(assignment[i] for i in map1)
            ass2 = tuple(assignment[i] for i in map2)

            # Multiply the probabilities
            prob1 = factor1.probabilities.get(ass1, 1.0)
            prob2 = factor2.probabilities.get(ass2, 1.0)
            new_factor.probabilities[assignment] = prob1 * prob2

        return new_factor

    def _sum_out(self, factor: Factor, var_to_sum_out: Variable) -> Factor:
        """
        Sums out (marginalizes) a variable from a factor.

        This operation removes a variable from a factor by summing over all its possible values.
        It is a fundamental operation in variable elimination, where variables are successively
        eliminated from the network by summing them out from factors.

        Mathematical definition:
        For a factor f(X,Y) where X is the variable to sum out, the resulting factor g(Y) is:
        g(y) = ∑ₓ f(x,y) for all assignments y to Y

        Parameters:
        -----------
        factor : Factor
            The factor from which to sum out the variable
        var_to_sum_out : Variable
            The variable to be summed out (marginalized)

        Returns:
        --------
        Factor
            A new factor with var_to_sum_out removed, representing the marginal over remaining variables

        Example:
        --------
        For a factor representing P(A,B) with variables [A, B] and probabilities:
        {
            ('True', 'True'): 0.14,
            ('True', 'False'): 0.06,
            ('False', 'True'): 0.08,
            ('False', 'False'): 0.72
        }

        Summing out variable A would create a factor with variables [B] and probabilities:
        {
            ('True',): 0.14 + 0.08 = 0.22,
            ('False',): 0.06 + 0.72 = 0.78
        }

        This represents the marginal probability P(B).

        Note:
        -----
        If the variable to sum out is not in the factor, the original factor is returned unchanged.
        """
        if var_to_sum_out not in factor.variables:
            return factor

        # New variables are the old variables minus the one to sum out
        new_vars_list = list(factor.variables)
        var_index = new_vars_list.index(var_to_sum_out)
        new_vars_list.remove(var_to_sum_out)
        new_vars_tuple = tuple(new_vars_list)

        new_factor = Factor(new_vars_tuple)

        # Sum over the values of the variable to be eliminated
        for old_assignment, prob in factor.probabilities.items():
            new_assignment = tuple(
                old_assignment[i] for i in range(len(old_assignment)) if i != var_index
            )
            new_factor.probabilities[new_assignment] = (
                new_factor.probabilities.get(new_assignment, 0.0) + prob
            )

        return new_factor

    def variable_elimination(
        self, query_vars: Dict[str, str | None], evidence: Dict[str, str]
    ) -> Factor:
        """
        Performs Variable Elimination to compute P(query_vars | evidence).

        Variable elimination is an exact inference algorithm for Bayesian networks that
        efficiently computes marginal and conditional probabilities. It works by successively
        eliminating variables from the network through a process of factor operations.

        The algorithm follows these steps:
        1. Start with all factors (CPTs) in the network
        2. Reduce factors by incorporating observed evidence
        3. Determine elimination order using a heuristic
        4. For each non-query, non-evidence variable:
           a. Collect all factors containing the variable
           b. Join (multiply) these factors together
           c. Sum out the variable from the joined factor
           d. Replace the original factors with the new factor
        5. Join all remaining factors
        6. Normalize the result to get conditional probabilities

        Parameters:
        -----------
        query_vars : Dict[str, str]
            Variables to query. Keys are variable names and values are either specific
            values to query (if not None) or None to query all values for that variable.

        evidence : Dict[str, str]
            Observed evidence. Keys are variable names and values are their observed states.

        Returns:
        --------
        Factor
            A Factor object containing the probability distribution P(query_vars | evidence).

        Examples:
        ---------
        >>> # Query: P(Rain | GrassWet=True)
        >>> inference.variable_elimination({"Rain": None}, {"GrassWet": "True"})

        >>> # Query: P(Sprinkler=True | Rain=False, GrassWet=True)
        >>> inference.variable_elimination({"Sprinkler": "True"}, {"Rain": "False", "GrassWet": "True"})

        Elimination Process Example:
        ---------------------------
        For a simple Rain-Sprinkler-GrassWet network to compute P(Rain | GrassWet=True):

        1. Start with factors: P(Rain), P(Sprinkler|Rain), P(GrassWet|Rain,Sprinkler)
        2. Reduce P(GrassWet|Rain,Sprinkler) by evidence GrassWet=True to get P'(Rain,Sprinkler)
        3. Choose to eliminate Sprinkler next (non-query, non-evidence)
        4. Multiply P(Sprinkler|Rain) × P'(Rain,Sprinkler) to get joint factor P''(Rain,Sprinkler)
        5. Sum out Sprinkler: ∑ₛ P''(Rain,s) to get P'''(Rain)
        6. Multiply with P(Rain) to get unnormalized P(Rain|GrassWet=True)
        7. Normalize to get final P(Rain|GrassWet=True)

        Notes:
        ------
        - The algorithm handles both standard notation ("True"/"False") and shorthand ("T"/"F")
        - Performance depends heavily on the elimination order, which is determined by a heuristic
        - Time complexity is exponential in the worst case, but practical for most networks
        """
        # 1. Start with all factors
        factors = list(self.network.factors.values())

        # 2. Reduce factors by evidence
        reduced_factors = []
        for f in factors:
            if any(v.name in evidence for v in f.variables):
                # Initialize variables outside the loop to avoid UnboundLocalError
                new_vars_temp: list[Variable] = []
                new_probs = {}

                var_map = {v.name: i for i, v in enumerate(f.variables)}

                # Filter assignments that are consistent with evidence
                for assignment, prob in f.probabilities.items():
                    consistent = True
                    for var_name, value in evidence.items():
                        if var_name in var_map:
                            # Handle both "T"/"F" and "True"/"False" by normalizing both sides
                            assignment_value = assignment[var_map[var_name]]
                            # Normalize assignment and evidence values
                            if assignment_value == "T" or assignment_value == "True":
                                normalized_assignment = "True"
                            elif assignment_value == "F" or assignment_value == "False":
                                normalized_assignment = "False"
                            else:
                                normalized_assignment = assignment_value

                            if value == "T" or value == "True":
                                normalized_evidence = "True"
                            elif value == "F" or value == "False":
                                normalized_evidence = "False"
                            else:
                                normalized_evidence = value

                            if normalized_assignment != normalized_evidence:
                                consistent = False
                                break
                    if consistent:
                        new_assignment = []
                        new_vars_temp = (
                            []
                        )  # Reinitialize for each consistent assignment
                        for i, v in enumerate(f.variables):
                            if v.name not in evidence:
                                new_assignment.append(assignment[i])
                                if v not in new_vars_temp:
                                    new_vars_temp.append(v)
                        new_probs[tuple(new_assignment)] = prob

                if new_vars_temp:  # Only create a factor if we have variables left
                    reduced_factors.append(Factor(tuple(new_vars_temp), new_probs))
            else:
                reduced_factors.append(f)

        factors = reduced_factors

        # 3. Determine elimination order (simple heuristic: least complex first)
        all_vars = set(v.name for v in self.network.variables.values())
        vars_to_eliminate = all_vars - set(query_vars) - set(evidence.keys())

        # A simple heuristic for ordering: eliminate variables that appear in fewest factors
        elimination_order = sorted(
            vars_to_eliminate,
            key=lambda var: sum(
                1 for f in factors if self.network.variables[var] in f.variables
            ),
        )

        # 4. Eliminate variables
        for var_name in elimination_order:
            var_to_eliminate = self.network.variables[var_name]

            # Find all factors containing the variable
            factors_with_var = [f for f in factors if var_to_eliminate in f.variables]
            factors_without_var = [
                f for f in factors if var_to_eliminate not in f.variables
            ]

            if not factors_with_var:
                continue

            # Join all factors with the variable
            joined_factor = factors_with_var[0]
            for i in range(1, len(factors_with_var)):
                joined_factor = self._join_factors(joined_factor, factors_with_var[i])

            # Sum out the variable
            new_factor = self._sum_out(joined_factor, var_to_eliminate)

            # Update the list of factors
            factors = factors_without_var + [new_factor]

        # 5. Join remaining factors
        result_factor = factors[0]
        for i in range(1, len(factors)):
            result_factor = self._join_factors(result_factor, factors[i])

        # 6. Normalize the result
        total_prob = sum(result_factor.probabilities.values())
        if total_prob > 1e-9:  # Avoid division by zero
            for assignment, prob in result_factor.probabilities.items():
                result_factor.probabilities[assignment] = prob / total_prob

        return result_factor


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

    inference = Inference(network)

    # Test query: P(Rain | GrassWet=Yes)
    query_vars : Dict[str, str | None] = {"Rain": None}
    evidence = {"GrassWet": "Yes"}
    result = inference.variable_elimination(query_vars, evidence)

    print(f"Query: P({', '.join(query_vars)} | {evidence})")
    for assignment, prob in result.probabilities.items():
        print(f"  P({', '.join(assignment)}) = {prob:.4f}")

    # Test query: P(GrassWet)
    query_vars = {"GrassWet": None}
    evidence = {}
    result = inference.variable_elimination(query_vars, evidence)

    print(f"Query: P({', '.join(query_vars)})")
    for assignment, prob in result.probabilities.items():
        print(f"  P({', '.join(assignment)}) = {prob:.4f}")
