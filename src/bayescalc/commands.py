"""
This module implements the utility commands for the Bayesian Network calculator.
"""

import math
import numpy as np
import re
import os
from typing import Dict, List, Set, Callable, Optional

from .network_model import BayesianNetwork
from .inference import Inference
from .lexer import Lexer
from .parser import Parser


class CommandHandler:
    def __init__(
        self,
        network: BayesianNetwork,
        reload_callback: Optional[Callable[[BayesianNetwork], None]] = None,
    ):
        self.network = network
        self.inference = Inference(network)
        self.reload_callback = reload_callback
        self._initialize_command_registry()

    def _initialize_command_registry(self):
        """Initialize the command registry with all available commands."""
        self.commands = {
            # Command name -> {aliases, handler, help, requires_args, special_parsing, arg_count, validate_args}
            "printCPT": {
                "aliases": [],
                "handler": self.print_cpt,
                "help": "printCPT(variable_name) - Print the Conditional Probability Table for a variable",
                "requires_args": True,
                "special_parsing": False,
                "arg_count": 1,
                "validate_args": True,
            },
            "parents": {
                "aliases": [],
                "handler": self.get_parents,
                "help": "parents(variable_name) - Get the parent variables of a given variable",
                "requires_args": True,
                "special_parsing": False,
                "arg_count": 1,
                "validate_args": True,
            },
            "children": {
                "aliases": [],
                "handler": self.get_children,
                "help": "children(variable_name) - Get the child variables of a given variable",
                "requires_args": True,
                "special_parsing": False,
                "arg_count": 1,
                "validate_args": True,
            },
            "isindependent": {
                "aliases": [],
                "handler": self.is_independent,
                "help": "isindependent(var1, var2) - Check if two variables are independent",
                "requires_args": True,
                "special_parsing": False,
                "arg_count": 2,
                "validate_args": True,
            },
            "iscondindependent": {
                "aliases": [],
                "handler": self._handle_cond_independent,
                "help": "iscondindependent(var1, var2 | cond_vars...) - Check conditional independence",
                "requires_args": True,
                "special_parsing": True,
                "arg_count": None,  # Variable arguments due to special parsing
                "validate_args": False,  # Validation handled in special parser
            },
            "entropy": {
                "aliases": [],
                "handler": self.entropy,
                "help": "entropy(variable_name) - Calculate the entropy of a variable",
                "requires_args": True,
                "special_parsing": False,
                "arg_count": 1,
                "validate_args": True,
            },
            "conditional_entropy": {
                "aliases": [],
                "handler": self._handle_conditional_entropy,
                "help": "conditional_entropy(X | Y) - Calculate conditional entropy H(X|Y)",
                "requires_args": True,
                "special_parsing": True,
                "arg_count": None,  # Variable arguments due to special parsing
                "validate_args": False,  # Validation handled in special parser
            },
            "mutual_information": {
                "aliases": [],
                "handler": self.mutual_information,
                "help": "mutual_information(var1, var2) - Calculate mutual information between two variables",
                "requires_args": True,
                "special_parsing": False,
                "arg_count": 2,
                "validate_args": True,
            },
            "ls": {
                "aliases": ["vars"],
                "handler": self.list_variables,
                "help": "ls() or vars() - List all variables and their domains",
                "requires_args": False,
                "special_parsing": False,
                "arg_count": 0,
                "validate_args": False,  # No args to validate
            },
            "showGraph": {
                "aliases": [],
                "handler": self.show_graph,
                "help": "showGraph() - Display an ASCII representation of the network graph",
                "requires_args": False,
                "special_parsing": False,
                "arg_count": 0,
                "validate_args": False,  # No args to validate
            },
            "printJPT": {
                "aliases": [],
                "handler": self.print_jpt,
                "help": "printJPT() - Print the complete Joint Probability Table",
                "requires_args": False,
                "special_parsing": False,
                "arg_count": 0,
                "validate_args": False,  # No args to validate
            },
            "help": {
                "aliases": ["?"],
                "handler": self._handle_help,
                "help": "help() or help(command) - Show help for all commands or a specific command",
                "requires_args": False,
                "special_parsing": True,
                "arg_count": None,  # Optional argument
                "validate_args": False,  # Validation handled in special parser
            },
            "marginals": {
                "aliases": [],
                "handler": self.marginals,
                "help": "marginals(n) - List marginal probabilities for all n-variable combinations",
                "requires_args": True,
                "special_parsing": False,
                "arg_count": 1,
                "validate_args": True,
            },
            "condprobs": {
                "aliases": [],
                "handler": self.condprobs,
                "help": "condprobs(n, m) - List all conditional probabilities P(A|B) for n-by-m variable combinations",
                "requires_args": True,
                "special_parsing": False,
                "arg_count": 2,
                "validate_args": True,
            },
            "load": {
                "aliases": [],
                "handler": self.load_network,
                "help": "load(filename) - Load a new Bayesian network from a file",
                "requires_args": True,
                "special_parsing": False,
                "arg_count": 1,
                "validate_args": True,
            },
            "visualize": {
                "aliases": ["viz"],
                "handler": self._handle_visualize,
                "help": (
                    "visualize(output_file, format=pdf, show_cpt=True, layout=dot, rankdir=TB) - Generate network visualization\n"
                    "    output_file: Path to output file (without extension)\n"
                    "    format: Output format (pdf, png, svg, jpg) [default: pdf]\n"
                    "    show_cpt: Include CPT tables in visualization (True/False) [default: True]\n"
                    "    layout: Graph layout engine (dot, neato, fdp, circo, twopi) [default: dot]\n"
                    "    rankdir: Graph direction (TB, LR, BT, RL) [default: TB]\n"
                    "    Examples: visualize(network.pdf), visualize(graph, format=png, show_cpt=False)"
                ),
                "requires_args": True,
                "special_parsing": True,
                "arg_count": None,
                "validate_args": False,
            },
        }

        # Create alias lookup table
        self.alias_to_command = {}
        for cmd_name, cmd_info in self.commands.items():
            self.alias_to_command[cmd_name] = cmd_name
            for alias in cmd_info["aliases"]:
                self.alias_to_command[alias] = cmd_name

    def is_command(self, command_str: str) -> bool:
        """
        Check if the given string looks like a command from the command registry.

        Args:
            command_str: The string to check

        Returns:
            bool: True if it matches a known command pattern
        """
        command_str = command_str.strip()

        # Check if it's a command without arguments
        if command_str in self.alias_to_command:
            return True

        # Check if it matches command(args) pattern
        match = re.match(r"(\w+)\(", command_str)
        if match:
            command = match.group(1)
            return command in self.alias_to_command

        return False

    def execute(self, command_str: str):
        """Parses and executes a command using the command registry."""
        command_str = command_str.strip()

        # Handle commands without arguments/parentheses (shortcuts)
        if command_str in self.alias_to_command:
            cmd_name = self.alias_to_command[command_str]
            cmd_info = self.commands[cmd_name]
            if not cmd_info["requires_args"]:
                return cmd_info["handler"]()
            else:
                raise ValueError(
                    f"Command '{command_str}' requires arguments. Use: {cmd_info['help']}"
                )

        # Parse command with parentheses
        match = re.match(r"(\w+)\((.*)\)", command_str)
        if not match:
            raise ValueError(
                f"Invalid command format: {command_str}. Use 'help()' to see available commands."
            )

        command = match.group(1)
        args_str = match.group(2)

        # Look up command in registry
        if command not in self.alias_to_command:
            raise ValueError(
                f"Unknown command: {command}. Use 'help()' to see available commands."
            )

        cmd_name = self.alias_to_command[command]
        cmd_info = self.commands[cmd_name]

        # Handle commands that require special parsing
        if cmd_info["special_parsing"]:
            return cmd_info["handler"](args_str)

        # Handle commands that don't require arguments
        if not cmd_info["requires_args"]:
            if args_str.strip():
                raise ValueError(
                    f"Command '{command}' does not take arguments. Use: {cmd_info['help']}"
                )
            return cmd_info["handler"]()

        # Handle regular commands with comma-separated arguments
        args = [arg.strip() for arg in args_str.split(",")] if args_str else []

        # Validate argument count using registry information
        if cmd_info["validate_args"]:
            expected_count = cmd_info["arg_count"]
            if len(args) != expected_count:
                if expected_count == 1:
                    raise ValueError(
                        f"{cmd_name} requires one argument. Use: {cmd_info['help']}"
                    )
                elif expected_count == 2:
                    raise ValueError(
                        f"{cmd_name} requires two arguments. Use: {cmd_info['help']}"
                    )
                else:
                    raise ValueError(
                        f"{cmd_name} requires {expected_count} arguments. Use: {cmd_info['help']}"
                    )

        return cmd_info["handler"](*args)

    def _handle_help(self, args_str: str = "") -> str:
        """Handle help command - show help for all commands or a specific command."""
        command_name = args_str.strip() if args_str else None

        if not command_name:
            # Show help for all commands
            lines = ["Available commands:"]
            lines.append("=" * 50)
            for cmd_name in sorted(self.commands.keys()):
                cmd_info = self.commands[cmd_name]
                lines.append(f"  {cmd_info['help']}")
                if cmd_info["aliases"]:
                    lines.append(f"    Aliases: {', '.join(cmd_info['aliases'])}")
            return "\n".join(lines)
        else:
            # Show help for specific command
            if command_name not in self.alias_to_command:
                return f"Unknown command: {command_name}"

            cmd_name = self.alias_to_command[command_name]
            cmd_info = self.commands[cmd_name]
            help_text = cmd_info["help"]
            if cmd_info["aliases"]:
                help_text += f"\nAliases: {', '.join(cmd_info['aliases'])}"
            return help_text

    def _handle_cond_independent(self, args_str: str) -> bool:
        """Handle conditional independence command with special parsing."""
        parts = args_str.split("|")
        if len(parts) != 2:
            raise ValueError("iscondindependent format: A, B | C, D")
        vars_part = [v.strip() for v in parts[0].split(",")]
        cond_part = [v.strip() for v in parts[1].split(",")]
        if len(vars_part) != 2:
            raise ValueError("iscondindependent requires two variables to check")
        return self.is_cond_independent(vars_part[0], vars_part[1], cond_part)

    def _handle_conditional_entropy(self, args_str: str) -> float:
        """Handle conditional entropy command with special parsing."""
        parts = args_str.split("|")
        if (
            len(parts) != 2
            or len(parts[0].split(",")) != 1
            or len(parts[1].split(",")) != 1
        ):
            raise ValueError("conditional_entropy format: X | Y")
        return self.conditional_entropy(parts[0].strip(), parts[1].strip())

    def marginals(self, n_str: str) -> str:
        """Compute and display marginal probabilities for all n-variable combinations."""
        try:
            n = int(n_str)
        except ValueError:
            raise ValueError(f"Invalid argument '{n_str}': n must be an integer")

        if n <= 0:
            raise ValueError(f"n must be positive, got {n}")

        all_vars = list(self.network.variables.keys())
        num_vars = len(all_vars)

        if n > num_vars:
            raise ValueError(
                f"n={n} exceeds number of variables ({num_vars}) in the network"
            )

        from itertools import combinations

        # Get all combinations of n variables
        var_combinations = list(combinations(all_vars, n))

        if not var_combinations:
            return "No variable combinations available."

        # Compute marginals for each combination
        results = []
        max_prob_width = 0

        for var_combo in var_combinations:
            # Convert list of variable names to the expected Dict[str, str | None] format
            query_vars_dict: Dict[str, str | None] = {
                var_name: None for var_name in var_combo
            }

            # Compute marginal distribution for this combination
            marginal = self.inference.variable_elimination(query_vars_dict, {})

            # Get all possible value assignments for these variables
            var_objects = [self.network.variables[var_name] for var_name in var_combo]

            from itertools import product

            value_assignments = list(product(*(var.domain for var in var_objects)))

            for assignment in value_assignments:
                # Create probability string representation
                prob_key = assignment
                probability = marginal.probabilities.get(prob_key, 0.0)

                # Create variable assignment string with negations for False/No/Off values
                var_strs = []
                for i, (var_name, value) in enumerate(zip(var_combo, assignment)):
                    if value.lower() in ["false", "no", "off"]:
                        var_strs.append(f"~{var_name}")
                    else:
                        var_strs.append(var_name)

                prob_str = f"P({', '.join(var_strs)})"
                prob_value = f"{probability:.6f}"

                results.append((prob_str, prob_value))
                max_prob_width = max(max_prob_width, len(prob_str))

        # Format output with aligned columns
        lines = []
        for prob_str, prob_value in results:
            lines.append(f"{prob_str:<{max_prob_width}} = {prob_value}")

        return "\n".join(lines)

    def condprobs(self, n_str: str, m_str: str) -> str:
        """Compute and display conditional probabilities P(A|B) for all n-by-m variable combinations."""
        try:
            n = int(n_str)
            m = int(m_str)
        except ValueError:
            raise ValueError(
                f"Invalid arguments: n={n_str} and m={m_str} must be integers"
            )

        if n <= 0 or m <= 0:
            raise ValueError(f"n and m must be positive, got n={n}, m={m}")

        all_vars = list(self.network.variables.keys())
        num_vars = len(all_vars)

        if n + m > num_vars:
            raise ValueError(
                f"n+m={n+m} exceeds number of variables ({num_vars}) in the network"
            )

        from itertools import combinations, product

        # Get all combinations of n variables (for the condition part A)
        condition_var_combinations = list(combinations(all_vars, n))

        # Get all combinations of m variables (for the evidence part B)
        evidence_var_combinations = list(combinations(all_vars, m))

        if not condition_var_combinations or not evidence_var_combinations:
            return "No variable combinations available."

        results = []
        max_prob_width = 0

        # For each combination of condition variables and evidence variables
        for cond_vars in condition_var_combinations:
            for evid_vars in evidence_var_combinations:

                # Skip if there's overlap between condition and evidence variables
                if set(cond_vars) & set(evid_vars):
                    continue

                # Get variable objects
                cond_var_objects = [
                    self.network.variables[var_name] for var_name in cond_vars
                ]
                evid_var_objects = [
                    self.network.variables[var_name] for var_name in evid_vars
                ]

                # Get all possible value assignments for condition variables
                cond_value_assignments = list(
                    product(*(var.domain for var in cond_var_objects))
                )

                # Get all possible value assignments for evidence variables
                evid_value_assignments = list(
                    product(*(var.domain for var in evid_var_objects))
                )

                # Compute P(A|B) for each combination of values
                for cond_assignment in cond_value_assignments:
                    for evid_assignment in evid_value_assignments:

                        # Create evidence dictionary for the inference
                        evidence = dict(zip(evid_vars, evid_assignment))

                        # Compute P(A|B) using variable elimination
                        try:
                            query_vars_dict: Dict[str, str | None] = {
                                var_name: None for var_name in cond_vars
                            }
                            conditional_dist = self.inference.variable_elimination(
                                query_vars_dict, evidence
                            )

                            # Get probability for this specific assignment of condition variables
                            probability = conditional_dist.probabilities.get(
                                cond_assignment, 0.0
                            )

                            # Create string representations with negations
                            cond_strs = []
                            for var_name, value in zip(cond_vars, cond_assignment):
                                if value.lower() in ["false", "no", "off"]:
                                    cond_strs.append(f"~{var_name}")
                                else:
                                    cond_strs.append(var_name)

                            evid_strs = []
                            for var_name, value in zip(evid_vars, evid_assignment):
                                if value.lower() in ["false", "no", "off"]:
                                    evid_strs.append(f"~{var_name}")
                                else:
                                    evid_strs.append(var_name)

                            prob_str = (
                                f"P({', '.join(cond_strs)} | {', '.join(evid_strs)})"
                            )
                            prob_value = f"{probability:.6f}"

                            results.append((prob_str, prob_value))
                            max_prob_width = max(max_prob_width, len(prob_str))

                        except Exception:
                            # Handle cases where conditional probability cannot be computed
                            # (e.g., when evidence has zero probability)
                            continue

        if not results:
            return "No valid conditional probabilities found (may be due to disjoint variable sets or zero evidence probabilities)."

        # Sort results for consistent output
        results.sort(key=lambda x: x[0])

        # Format output with aligned columns
        lines = []
        for prob_str, prob_value in results:
            lines.append(f"{prob_str:<{max_prob_width}} = {prob_value}")

        return "\n".join(lines)

    def print_cpt(self, variable_name: str) -> str:
        """Prints the CPT for a given variable with proper column alignment."""
        if variable_name not in self.network.factors:
            return f"No CPT found for variable '{variable_name}'."

        factor = self.network.factors[variable_name]
        variable = self.network.variables[variable_name]
        parents = [v for v in factor.variables if v != variable]

        # New format: Child | Parents (comma-separated) | Probability
        if not parents:
            # No parents case - just show variable and probability
            col_names = [variable.name, "P"]
            col_widths = [len(variable.name), 1]

            data_rows = []
            for val in variable.domain:
                prob = factor.probabilities.get((val,), 0.0)
                row_data = [val, f"{prob:.4f}"]
                data_rows.append(row_data)
        else:
            # Has parents - new 3-column format
            col_names = [variable.name, " ".join(f"{p.name:<10}" for p in parents), "P"]
            # col_widths = [len(variable.name), len(", ".join([p.name for p in parents])), 6]  # Set minimum widths

            col_widths = [
                len(variable.name),
                len(col_names[1]),
                6,
            ]  # Set minimum widths
            data_rows = []
            parent_domains = [p.domain for p in parents]
            from itertools import product

            parent_combinations = list(product(*parent_domains))

            for val in variable.domain:
                for p_comb in parent_combinations:
                    key = (val,) + p_comb
                    prob = factor.probabilities.get(key, 0.0)
                    # Format parent values with wider spacing like in the target
                    parent_values = []
                    for i, pval in enumerate(p_comb):
                        if i < len(p_comb) - 1:
                            sval = pval + ","
                            parent_values.append(f"{sval:<10}")
                        else:
                            parent_values.append(f"{pval}")
                    parent_str = " ".join(parent_values)
                    row_data = [val, parent_str, f"{prob:.4f}"]
                    data_rows.append(row_data)

        # Update column widths based on data
        for row_data in data_rows:
            for i, cell in enumerate(row_data):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Build formatted output
        lines = []

        # Header row
        header_parts = [f"{name:<{col_widths[i]}}" for i, name in enumerate(col_names)]
        header = " | ".join(header_parts)
        lines.append(header)

        # Separator line
        separator_parts = ["-" * col_widths[i] for i in range(len(col_names))]
        separator = "-+-".join(separator_parts)
        lines.append(separator)

        # Data rows
        for row_data in data_rows:
            row_parts = [
                f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row_data)
            ]
            row = " | ".join(row_parts)
            lines.append(row)

        return "\n".join(lines)

    def get_parents(self, variable_name: str) -> Set[str]:
        """Returns the parents of a variable."""
        return self.network.get_parents(variable_name)

    def get_children(self, variable_name: str) -> Set[str]:
        """Returns the children of a variable."""
        return self.network.get_children(variable_name)

    def show_graph(self) -> str:
        """Returns an ASCII representation of the network graph."""
        lines = ["Bayesian Network Graph:"]
        for var, children in self.network.adj.items():
            if children:
                lines.append(f"  {var} -> {{{', '.join(children)}}}")
        if not any(self.network.adj.values()):
            lines.append("  (No connections in the graph)")
        return "\n".join(lines)

    def is_independent(self, var1_name: str, var2_name: str) -> bool:
        """Checks if two variables are independent."""
        # P(A, B) == P(A) * P(B)
        p_a = self.inference.variable_elimination({var1_name: None}, {})
        p_b = self.inference.variable_elimination({var2_name: None}, {})
        p_ab = self.inference.variable_elimination(
            {var1_name: None, var2_name: None}, {}
        )

        var1 = self.network.variables[var1_name]
        var2 = self.network.variables[var2_name]

        for val1 in var1.domain:
            for val2 in var2.domain:
                prob_a = p_a.probabilities.get((val1,), 0.0)
                prob_b = p_b.probabilities.get((val2,), 0.0)

                # Find correct assignment order in joint probability factor
                if p_ab.variables[0].name == var1_name:
                    prob_ab = p_ab.probabilities.get((val1, val2), 0.0)
                else:
                    prob_ab = p_ab.probabilities.get((val2, val1), 0.0)

                if not np.isclose(prob_ab, prob_a * prob_b):
                    return False
        return True

    def is_cond_independent(
        self, var1_name: str, var2_name: str, cond_vars: List[str]
    ) -> bool:
        """Checks if two variables are conditionally independent given other variables."""
        # P(A, B | C) == P(A | C) * P(B | C)
        cond_evidence_domains = [self.network.variables[v].domain for v in cond_vars]
        from itertools import product

        for cond_values in product(*cond_evidence_domains):
            evidence = dict(zip(cond_vars, cond_values))

            p_a_given_c = self.inference.variable_elimination(
                {var1_name: None}, evidence
            )
            p_b_given_c = self.inference.variable_elimination(
                {var2_name: None}, evidence
            )
            p_ab_given_c = self.inference.variable_elimination(
                {var1_name: None, var2_name: None}, evidence
            )

            var1 = self.network.variables[var1_name]
            var2 = self.network.variables[var2_name]

            for val1 in var1.domain:
                for val2 in var2.domain:
                    prob_a = p_a_given_c.probabilities.get((val1,), 0.0)
                    prob_b = p_b_given_c.probabilities.get((val2,), 0.0)

                    if p_ab_given_c.variables[0].name == var1_name:
                        prob_ab = p_ab_given_c.probabilities.get((val1, val2), 0.0)
                    else:
                        prob_ab = p_ab_given_c.probabilities.get((val2, val1), 0.0)

                    if not np.isclose(prob_ab, prob_a * prob_b):
                        return False
        return True

    def entropy(self, var_name: str) -> float:
        """Computes the entropy of a variable."""
        p_x = self.inference.variable_elimination({var_name: None}, {})
        probs = np.array(list(p_x.probabilities.values()))
        return -np.sum(probs * np.log2(probs))

    def conditional_entropy(self, var_x_name: str, var_y_name: str) -> float:
        """Computes the conditional entropy H(X|Y)."""
        p_xy = self.inference.variable_elimination(
            {var_x_name: None, var_y_name: None}, {}
        )
        p_y = self.inference.variable_elimination({var_y_name: None}, {})

        var_x = self.network.variables[var_x_name]
        var_y = self.network.variables[var_y_name]

        h_x_given_y = 0.0
        for val_y in var_y.domain:
            prob_y = p_y.probabilities.get((val_y,), 0.0)
            if prob_y > 1e-9:
                h_x_given_y_val = 0.0
                for val_x in var_x.domain:
                    if p_xy.variables[0].name == var_x_name:
                        prob_xy = p_xy.probabilities.get((val_x, val_y), 0.0)
                    else:
                        prob_xy = p_xy.probabilities.get((val_y, val_x), 0.0)

                    prob_x_given_y = prob_xy / prob_y
                    if prob_x_given_y > 1e-9:
                        h_x_given_y_val -= prob_x_given_y * math.log2(prob_x_given_y)
                h_x_given_y += prob_y * h_x_given_y_val
        return h_x_given_y

    def mutual_information(self, var1_name: str, var2_name: str) -> float:
        """Computes the mutual information between two variables."""
        # I(X;Y) = H(X) - H(X|Y)
        h_x = self.entropy(var1_name)
        h_x_given_y = self.conditional_entropy(var1_name, var2_name)
        return h_x - h_x_given_y

    def print_jpt(self) -> str:
        """Computes and prints the full Joint Probability Table with proper column alignment."""
        all_vars = list(self.network.variables.keys())
        jpt = self.inference.variable_elimination({var: None for var in all_vars}, {})

        # Get variables in their original declaration order
        ordered_vars = [
            self.network.variables[var_name] for var_name in self.network.variable_order
        ]

        # Calculate column widths
        col_names = [var.name for var in ordered_vars] + ["P"]
        col_widths = [len(name) for name in col_names]

        # Collect all data rows to determine maximum widths
        data_rows = []

        from itertools import product

        # Generate all possible assignments in the declaration order
        all_assignments = product(*(var.domain for var in ordered_vars))

        for assignment in all_assignments:
            # The JPT factor's variables might be in a different order.
            # We need to map our ordered assignment to the JPT's order.
            jpt_var_names = [v.name for v in jpt.variables]

            # Create a dictionary for the current assignment based on ordered_vars
            assignment_dict = {
                ordered_vars[i].name: assignment[i] for i in range(len(ordered_vars))
            }

            # Reorder the assignment tuple to match the JPT factor's variable order
            jpt_assignment_tuple = tuple(
                assignment_dict[var_name] for var_name in jpt_var_names
            )

            prob = jpt.probabilities.get(jpt_assignment_tuple, 0.0)

            row_data = list(assignment) + [f"{prob:.6f}"]
            data_rows.append(row_data)

        # Update column widths based on data
        for row_data in data_rows:
            for i, cell in enumerate(row_data):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Build formatted output
        lines = []

        # Header row
        header_parts = [f"{name:<{col_widths[i]}}" for i, name in enumerate(col_names)]
        header = " | ".join(header_parts)
        lines.append(header)

        # Separator line
        separator_parts = ["-" * col_widths[i] for i in range(len(col_names))]
        separator = "-+-".join(separator_parts)
        lines.append(separator)

        # Data rows
        for row_data in data_rows:
            row_parts = [
                f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row_data)
            ]
            row = " | ".join(row_parts)
            lines.append(row)

        return "\n".join(lines)

    def list_variables(self) -> str:
        """Lists all variables and their domains."""
        if not self.network.variables:
            return "No variables defined in the network."

        # Determine column widths
        var_width = max(len(var) for var in self.network.variables.keys()) + 2
        type_width = max(len("Boolean"), len("Multival")) + 2  # Width for Type column
        states_width = (
            max(len(", ".join(var.domain)) for var in self.network.variables.values())
            + 2
        )

        header = f"{'Variable':<{var_width}} | {'Type':<{type_width}} | {'States':<{states_width}}"
        separator = "-" * (var_width + 3 + type_width + 3 + states_width)

        lines = [header, separator]

        # Add each variable, its type, and its states
        for var_name, var_obj in sorted(self.network.variables.items()):
            states = ", ".join(var_obj.domain)
            var_type = var_obj.var_type
            lines.append(
                f"{var_name:<{var_width}} | {var_type:<{type_width}} | {states:<{states_width}}"
            )

        return "\n".join(lines)

    def load_network(self, filename: str) -> str:
        """
        Load a new Bayesian network from a file.

        Args:
            filename: Path to the network file (.net)

        Returns:
            Success message with network details

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file cannot be parsed
        """
        filename = filename.strip()

        # Expand user home directory if needed
        filename = os.path.expanduser(filename)

        # Check if file exists
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Network file not found: {filename}")

        try:
            # Read the file
            with open(filename, "r") as f:
                network_str = f.read()

            # Parse the network
            lexer = Lexer(network_str)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            new_network = parser.parse()

            # Update the network and inference engine
            self.network = new_network
            self.inference = Inference(new_network)

            # Notify the REPL to update its references if callback is provided
            if self.reload_callback:
                self.reload_callback(new_network)

            # Generate success message
            num_vars = len(new_network.variables)
            var_names = ", ".join(sorted(new_network.variables.keys()))

            return (
                f"Successfully loaded network from: {filename}\n"
                f"Variables ({num_vars}): {var_names}"
            )

        except (SyntaxError, ValueError) as e:
            raise ValueError(f"Error parsing network file '{filename}': {e}")
        except Exception as e:
            raise ValueError(f"Error loading network file '{filename}': {e}")

    def _handle_visualize(self, args_str: str) -> str:
        """
        Handle the visualize command with flexible argument parsing.

        Args:
            args_str: Arguments string (e.g., "output.pdf, show_cpt=False, layout=neato")

        Returns:
            Success message with output file path
        """
        # Check if graphviz is available
        try:
            from .visualizer import NetworkVisualizer
        except ImportError:
            return (
                "Error: graphviz package not installed.\n"
                "Install it with: pip install graphviz\n"
                "You also need the graphviz system package:\n"
                "  macOS: brew install graphviz\n"
                "  Ubuntu/Debian: sudo apt-get install graphviz\n"
                "  Windows: Download from https://graphviz.org/download/"
            )

        # Parse arguments
        args_str = args_str.strip()
        if not args_str:
            return "Error: Output filename required. Usage: visualize(output.pdf)"

        parts = [p.strip() for p in args_str.split(",")]

        # First argument is always the output file
        output_file = parts[0]

        # Parse optional arguments
        format_arg = None
        show_cpt = True
        layout = "dot"
        rankdir = "TB"
        page_size = None
        scale = 1.0

        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "format":
                    format_arg = value
                elif key == "show_cpt":
                    show_cpt = value.lower() in ("true", "1", "yes")
                elif key == "layout":
                    layout = value
                elif key == "rankdir":
                    rankdir = value.upper()
                elif key == "page_size":
                    page_size = value
                elif key == "scale":
                    try:
                        scale = float(value)
                    except ValueError:
                        return (
                            f"Error: Invalid scale value '{value}'. Must be a number."
                        )

        # Determine format from filename extension if not explicitly specified
        if format_arg is None:
            if "." in output_file:
                format_arg = output_file.rsplit(".", 1)[1].lower()
                output_file = output_file.rsplit(".", 1)[0]
            else:
                format_arg = "pdf"

        try:
            visualizer = NetworkVisualizer(self.network)
            output_path = visualizer.generate_graph(
                output_file=output_file,
                format=format_arg,
                show_cpt=show_cpt,
                layout=layout,
                rankdir=rankdir,
                page_size=page_size,
                scale=scale,
            )
            return f"Network visualization saved to: {output_path}"

        except ImportError as e:
            return f"Error: {e}\nMake sure graphviz is installed on your system."
        except ValueError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error generating visualization: {e}"


if __name__ == "__main__":
    # Example usage for testing
    # from .lexer import Lexer
    # from .parser import Parser

    example_net = """
    boolean Rain
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

    cmd_handler = CommandHandler(network)

    print("--- CPT for Rain ---")
    print(cmd_handler.execute("printCPT(Rain)"))

    print("\n--- Parents of GrassWet ---")
    print(cmd_handler.execute("parents(GrassWet)"))

    print("\n--- Children of Rain ---")
    print(cmd_handler.execute("children(Rain)"))

    print("\n--- Graph ---")
    print(cmd_handler.execute("showGraph()"))

    print("\n--- Independence Test ---")
    print(
        f"Is Rain independent of Sprinkler? {cmd_handler.execute('isindependent(Rain, Sprinkler)')}"
    )

    print("\n--- Conditional Independence Test ---")
    print(
        f"Is GrassWet independent of Sprinkler given Rain? {cmd_handler.execute('iscondindependent(GrassWet, Sprinkler | Rain)')}"
    )

    print("\n--- Information Theory ---")
    print(f"Entropy of Rain: {cmd_handler.execute('entropy(Rain)'):.4f}")
    print(
        f"Conditional Entropy of GrassWet given Rain: {cmd_handler.execute('conditional_entropy(GrassWet|Rain)'):.4f}"
    )
    print(
        f"Mutual Information between Rain and GrassWet: {cmd_handler.execute('mutual_information(Rain, GrassWet)'):.4f}"
    )

    print("\n--- Joint Probability Table ---")
    print(cmd_handler.execute("printJPT()"))

    print("\n--- List Variables ---")
    print(cmd_handler.execute("ls"))
