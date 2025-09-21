"""
This module handles parsing and evaluating arithmetic expressions
of probability queries.
"""
import re
import math
from typing import Dict, Any
from .queries import QueryParser

class ExpressionParser:
    def __init__(self, query_parser: QueryParser):
        self.query_parser = query_parser

    def evaluate(self, expr_str: str):
        """
        Evaluates a mathematical expression containing probability queries.
        e.g., "P(Rain=True | GrassWet=Yes) / P(Rain=True)" or "P(Rain) / P(~Rain)"
        """
        # If it's a single probability query with no operations, just return it directly
        if expr_str.startswith("P(") and expr_str.endswith(")") and not any(op in expr_str[2:-1] for op in ['+', '-', '*', '/', '(', ')']):
            return self.query_parser.parse_and_execute(expr_str)
            
        # Regex to find all P(...) queries
        prob_query_pattern = re.compile(r"P\([^)]+\)")

        # Find all probability queries in the expression
        prob_queries = prob_query_pattern.findall(expr_str)
        if not prob_queries:
            raise ValueError(f"No probability expressions found in: {expr_str}")

        # Create a map of query strings to placeholders to avoid collisions
        placeholders = {}
        expr_with_placeholders = expr_str
        
        # Evaluate each probability query and get its scalar value
        for i, query in enumerate(prob_queries):
            placeholder = f"__PROB_{i}__"
            placeholders[placeholder] = query
            expr_with_placeholders = expr_with_placeholders.replace(query, placeholder)
            
        # Now evaluate each probability query
        values = {}
        for placeholder, query in placeholders.items():
            try:
                result = self.query_parser.parse_and_execute(query)
                
                # Check if we got a single value result
                if not result.variables and len(result.probabilities) == 1:
                    # Single value, use it directly
                    values[placeholder] = list(result.probabilities.values())[0]
                elif '=' in query or '~' in query:
                    # This should have been a single value query like P(Rain=True) or P(~Rain)
                    # If it wasn't caught by the query parser, something's wrong
                    raise ValueError(f"Expected a scalar value for '{query}', but got a distribution.")
                else:
                    # Check if this is a boolean variable with shorthand notation
                    var_name = query[2:-1].strip()  # Extract just the variable name from P(...)
                    if var_name in self.query_parser.network.variables and self.query_parser.network.variables[var_name].is_boolean:
                        # For boolean variables, we can convert P(X) to P(X=True) automatically
                        modified_query = f"P({var_name}=True)"
                        result = self.query_parser.parse_and_execute(modified_query)
                        if not result.variables and len(result.probabilities) == 1:
                            values[placeholder] = list(result.probabilities.values())[0]
                            continue
                    
                    # If we get here, it's a genuinely unresolvable distribution
                    raise ValueError(f"The query '{query}' returns a probability distribution, not a single value. "
                                     f"Please specify a value for each variable.")
                    
            except Exception as e:
                raise ValueError(f"Error evaluating probability expression '{query}': {str(e)}")

        # Replace the placeholders with the actual numeric values
        final_expr = expr_with_placeholders
        for placeholder, value in values.items():
            final_expr = final_expr.replace(placeholder, str(value))

        # Evaluate the final arithmetic expression in a safe environment
        try:
            result = self._safe_eval(final_expr)
            return result
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{expr_str}': {str(e)}")

    def _safe_eval(self, expr: str):
        """
        Safely evaluates a mathematical expression string.
        """
        # Allowed names in the evaluation context
        allowed_names: Dict[str, Any] = {
            "math": math,
            "abs": abs,
            "pow": pow,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
        }
        
        # Check for any suspicious characters
        if re.search(r"[^0-9a-zA-Z_+\-*/().,\s]", expr.replace("math.", "")):
            raise ValueError(f"Expression contains invalid characters: {expr}")

        try:
            # eval is used here, but the expression is sanitized to only contain
            # numbers, operators, and functions from the allowed_names.
            return eval(expr, {"__builtins__": {}}, allowed_names)
        except (SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
            raise ValueError(f"Invalid mathematical expression: {expr}. Error: {e}")