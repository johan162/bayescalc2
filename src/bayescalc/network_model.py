"""
This module defines the core data structures for the Bayesian Network.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set


@dataclass(frozen=True)
class Variable:
    """Represents a random variable."""

    name: str
    domain: Tuple[str, ...]

    def __repr__(self):
        return f"Variable({self.name}, {self.domain})"

    @property
    def is_boolean(self) -> bool:
        """Returns True if this is a boolean variable (domain includes True/False or T/F)."""
        if len(self.domain) != 2:
            return False

        # Check for various boolean representations
        true_values = {"True", "T"}
        false_values = {"False", "F"}

        has_true = any(val in true_values for val in self.domain)
        has_false = any(val in false_values for val in self.domain)

        return has_true and has_false

    @property
    def var_type(self) -> str:
        """Returns the type of the variable as a string: 'Boolean' or 'Multival'."""
        return "Boolean" if self.is_boolean else "Multival"


@dataclass
class Factor:
    """Represents a factor (e.g., a CPT) in the network."""

    variables: Tuple[Variable, ...]
    probabilities: Dict[Tuple[str, ...], float] = field(default_factory=dict)
    name: str | None = None

    def __repr__(self):
        if self.name:
            # For single probability results, we want a clean output
            if not self.variables and len(self.probabilities) == 1:
                prob = list(self.probabilities.values())[0]
                return f"{self.name} = {prob:.4f}"
            return self.name
        return f"Factor({[v.name for v in self.variables]})"


class BayesianNetwork:
    """Represents a Bayesian Network."""

    def __init__(self):
        self.variables: Dict[str, Variable] = {}
        self.variable_order: List[str] = []
        self.factors: Dict[str, Factor] = {}
        self.adj: Dict[str, Set[str]] = {}
        self.rev_adj: Dict[str, Set[str]] = {}

    def add_variable(self, name: str, domain: Tuple[str, ...]):
        """Adds a variable to the network."""
        if name in self.variables:
            raise ValueError(f"Variable '{name}' already exists.")
        self.variables[name] = Variable(name, domain)
        self.variable_order.append(name)
        self.adj[name] = set()
        self.rev_adj[name] = set()

    def add_factor(
        self,
        variable_name: str,
        parent_names: List[str],
        cpt_entries: Dict[Tuple[str, ...], float],
    ):
        """Adds a factor (CPT) to the network."""
        if variable_name not in self.variables:
            raise ValueError(f"Variable '{variable_name}' not found.")

        variable = self.variables[variable_name]
        parents = [self.variables[p] for p in parent_names]

        factor_variables = (variable,) + tuple(parents)
        factor = Factor(factor_variables)

        # Validate and auto-complete CPT
        self._validate_and_complete_cpt(factor, cpt_entries, variable, parents)

        self.factors[variable_name] = factor

        for p in parent_names:
            self.adj[p].add(variable_name)
            self.rev_adj[variable_name].add(p)

    def _validate_and_complete_cpt(
        self,
        factor: Factor,
        cpt_entries: Dict[Tuple[str, ...], float],
        variable: Variable,
        parents: List[Variable],
    ):
        """Validates and auto-completes the CPT entries."""
        if not parents:
            # Prior probability
            total_prob = 0.0
            for val in variable.domain:
                if (val,) in cpt_entries:
                    total_prob += cpt_entries[(val,)]
                    factor.probabilities[(val,)] = cpt_entries[(val,)]

            if len(cpt_entries) < len(variable.domain):
                # Auto-complete
                if len(variable.domain) - len(cpt_entries) == 1:
                    missing_val = [
                        v for v in variable.domain if (v,) not in cpt_entries
                    ][0]
                    factor.probabilities[(missing_val,)] = 1.0 - total_prob
                else:
                    raise ValueError(
                        f"Ambiguous auto-completion for '{variable.name}'. Please specify more entries."
                    )

            if abs(sum(factor.probabilities.values()) - 1.0) > 1e-6:
                raise ValueError(
                    f"Probabilities for '{variable.name}' do not sum to 1."
                )
        else:
            # Conditional probability
            parent_domains = [p.domain for p in parents]
            from itertools import product

            parent_combinations = list(product(*parent_domains))

            for p_comb in parent_combinations:
                total_prob = 0.0

                for val in variable.domain:
                    key = (val,) + p_comb
                    if key in cpt_entries:
                        total_prob += cpt_entries[key]
                        factor.probabilities[key] = cpt_entries[key]

                if len([k for k in cpt_entries if k[1:] == p_comb]) < len(
                    variable.domain
                ):
                    # Auto-complete
                    if (
                        len(variable.domain)
                        - len([k for k in cpt_entries if k[1:] == p_comb])
                        == 1
                    ):
                        missing_val = [
                            v
                            for v in variable.domain
                            if (v,) + p_comb not in cpt_entries
                        ][0]
                        factor.probabilities[(missing_val,) + p_comb] = 1.0 - total_prob
                    else:
                        raise ValueError(
                            f"Ambiguous auto-completion for '{variable.name}' given {p_comb}. Please specify more entries."
                        )

                if (
                    abs(
                        sum(
                            factor.probabilities[(v,) + p_comb] for v in variable.domain
                        )
                        - 1.0
                    )
                    > 1e-6
                ):
                    raise ValueError(
                        f"Probabilities for '{variable.name}' given {p_comb} do not sum to 1."
                    )

    def get_parents(self, variable_name: str) -> Set[str]:
        """Returns the parents of a variable."""
        return self.rev_adj.get(variable_name, set())

    def get_children(self, variable_name: str) -> Set[str]:
        """Returns the children of a variable."""
        return self.adj.get(variable_name, set())

    def __repr__(self):
        return f"BayesianNetwork(variables={list(self.variables.keys())})"
