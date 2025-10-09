"""
This module implements the parser for the Bayesian Network input format.
It takes a list of tokens from the lexer and builds a BayesianNetwork object.
"""

import warnings
from typing import List, Tuple

from .lexer import Token, TokenType
from .network_model import BayesianNetwork


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]
        self.pos = 0
        self.network = BayesianNetwork()

    def _peek(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF

    def _advance(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def _consume(self, expected_type: TokenType) -> Token:
        token = self._peek()
        if token.type == expected_type:
            return self._advance()
        raise SyntaxError(
            f"Expected {expected_type.name} but found {token.type.name} at line {token.line}, column {token.column}"
        )

    def parse(self) -> BayesianNetwork:
        while self._peek().type != TokenType.EOF:
            if self._peek().type == TokenType.VARIABLE:
                self._parse_variable_declaration()
            elif self._peek().type == TokenType.BOOLEAN:
                self._parse_boolean_declaration()
            elif self._peek().type == TokenType.IDENTIFIER:
                self._parse_cpt_block()
            else:
                token = self._peek()
                raise SyntaxError(
                    f"Unexpected token {token.type.name} at line {token.line}, column {token.column}"
                )
        return self.network

    def _parse_variable_declaration(self):
        """Parses a variable declaration."""
        self._consume(TokenType.VARIABLE)
        name_token = self._consume(TokenType.IDENTIFIER)
        name = name_token.value

        # Check if domain is explicitly specified
        if self._peek().type == TokenType.LBRACE:
            self._consume(TokenType.LBRACE)  # Consume the left brace

            # Parse domain values
            domain = []
            while self._peek().type != TokenType.RBRACE:
                value = self._consume(TokenType.IDENTIFIER).value
                domain.append(value)

                if self._peek().type == TokenType.COMMA:
                    self._consume(TokenType.COMMA)
                else:  # We only accept comment or spaces after variable declaration
                    break

            self._consume(TokenType.RBRACE)

            # Check if this is an explicit {True, False} domain and warn
            if set(domain) == {"True", "False"}:
                warnings.warn(
                    f"Variable '{name}' at line {name_token.line} uses explicit {{True, False}} domain. "
                    f"Consider using 'boolean {name}' instead for clearer boolean variable declaration.",
                    DeprecationWarning,
                    stacklevel=2,
                )
        else:
            # If domain is not specified, default to Boolean
            domain = ["True", "False"]

        # Add variable to the network
        self.network.add_variable(name, tuple(domain))

    def _parse_boolean_declaration(self):
        """Parses a boolean variable declaration."""
        self._consume(TokenType.BOOLEAN)
        name = self._consume(TokenType.IDENTIFIER).value

        # Boolean variables always have {True, False} domain
        domain = ("True", "False")

        # Add variable to the network
        self.network.add_variable(name, domain)

    def _parse_cpt_block(self):
        variable_name = self._consume(TokenType.IDENTIFIER).value

        parent_names = []
        if self._peek().type == TokenType.PIPE:
            self._consume(TokenType.PIPE)
            while self._peek().type != TokenType.LBRACE:
                parent_names.append(self._consume(TokenType.IDENTIFIER).value)
                if self._peek().type == TokenType.COMMA:
                    self._consume(TokenType.COMMA)

        self._consume(TokenType.LBRACE)

        cpt_entries = {}
        while self._peek().type != TokenType.RBRACE:
            key, prob = self._parse_cpt_entry()
            cpt_entries[key] = prob

        self._consume(TokenType.RBRACE)
        self.network.add_factor(variable_name, parent_names, cpt_entries)

    def _parse_cpt_entry(self) -> Tuple[Tuple[str, ...], float]:
        self._consume(TokenType.PROBABILITY)
        self._consume(TokenType.LPAREN)

        value = self._consume(TokenType.IDENTIFIER).value
        # Convert T/F to True/False for boolean variables
        if value == "T":
            value = "True"
        elif value == "F":
            value = "False"

        conditions = []
        if self._peek().type == TokenType.PIPE:
            self._consume(TokenType.PIPE)
            while self._peek().type != TokenType.RPAREN:
                condition = self._consume(TokenType.IDENTIFIER).value
                # Convert T/F to True/False for boolean variables in conditions
                if condition == "T":
                    condition = "True"
                elif condition == "F":
                    condition = "False"
                conditions.append(condition)
                if self._peek().type == TokenType.COMMA:
                    self._consume(TokenType.COMMA)

        self._consume(TokenType.RPAREN)
        self._consume(TokenType.EQUALS)

        prob_token = self._consume(TokenType.FLOAT)
        prob = float(prob_token.value)

        key = (value,) + tuple(conditions)
        return key, prob


if __name__ == "__main__":
    # Example usage for testing
    from .lexer import Lexer

    example_net = """
    variable Rain {True, False}
    variable Sprinkler {On, Off}
    variable GrassWet {Yes, No}

    Rain {
        P(True) = 0.2
    }

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
    try:
        network = parser.parse()
        print("Network parsed successfully!")
        print(network)
        print(network.variables)
        print(network.factors)
        for name, factor in network.factors.items():
            print(f"Factor for {name}:")
            for k, v in factor.probabilities.items():
                print(f"  {k}: {v}")
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing network: {e}")
