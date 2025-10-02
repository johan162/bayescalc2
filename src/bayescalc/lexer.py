"""
This module implements the lexer for the Bayesian Network input format.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    VARIABLE = auto()
    IDENTIFIER = auto()
    LBRACE = auto()
    RBRACE = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    PIPE = auto()
    EQUALS = auto()
    PROBABILITY = auto()
    FLOAT = auto()
    COMMENT = auto()
    NEWLINE = auto()
    WHITESPACE = auto()
    UNKNOWN = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}, {self.column})"


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def _get_token(self):
        if self.pos >= len(self.text):
            return Token(TokenType.EOF, "", self.line, self.column)

        char = self.text[self.pos]

        if char == "\n":
            token = Token(TokenType.NEWLINE, char, self.line, self.column)
            self.pos += 1
            self.line += 1
            self.column = 1
            return token

        if char.isspace():
            token = Token(TokenType.WHITESPACE, char, self.line, self.column)
            self.pos += 1
            self.column += 1
            return token

        if char == "#":
            match = re.match(r"#.*", self.text[self.pos :])
            value = match.group(0)
            token = Token(TokenType.COMMENT, value, self.line, self.column)
            self.pos += len(value)
            # Comments don't advance line/column in the same way, handled by newline
            return token

        token_regex = {
            TokenType.VARIABLE: r"variable",
            TokenType.PROBABILITY: r"P",
            TokenType.IDENTIFIER: r"[a-zA-Z_][a-zA-Z0-9_]*",
            TokenType.FLOAT: r"\d+\.\d+",
            TokenType.LBRACE: r"\{",
            TokenType.RBRACE: r"\}",
            TokenType.LPAREN: r"\(",
            TokenType.RPAREN: r"\)",
            TokenType.COMMA: r",",
            TokenType.PIPE: r"\|",
            TokenType.EQUALS: r"=",
        }

        for token_type, pattern in token_regex.items():
            match = re.match(pattern, self.text[self.pos :])
            if match:
                value = match.group(0)
                # Handle keywords vs identifiers
                if token_type == TokenType.IDENTIFIER:
                    if value == "variable":
                        token_type = TokenType.VARIABLE
                    elif value == "P":
                        token_type = TokenType.PROBABILITY

                token = Token(token_type, value, self.line, self.column)
                self.pos += len(value)
                self.column += len(value)
                return token

        # If no match, it's an unknown token
        unknown_char = self.text[self.pos]
        token = Token(TokenType.UNKNOWN, unknown_char, self.line, self.column)
        self.pos += 1
        self.column += 1
        return token

    def tokenize(self):
        tokens = []
        while True:
            token = self._get_token()
            if token.type not in (TokenType.WHITESPACE, TokenType.COMMENT):
                tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens


if __name__ == "__main__":
    # Example usage for testing
    example_net = """
    # Example network definition
    variable Rain {True, False}
    variable Sprinkler {On, Off}

    Rain {
        P(True) = 0.2
    }
    """
    lexer = Lexer(example_net)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)
