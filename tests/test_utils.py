"""
Utility functions for testing Bayesian network functionality.
"""
from typing import Dict, List, Tuple, Any
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.network_model import BayesianNetwork, Factor

def parse_string(network_str: str) -> BayesianNetwork:
    """Parse a Bayesian network definition from a string."""
    lexer = Lexer(network_str)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()