"""
This module implements the interactive REPL for the Bayesian Network calculator.
"""

import sys
import os

from typing import Optional, Any
from .parser import Parser
from .queries import QueryParser
from .commands import CommandHandler
from .network_model import BayesianNetwork
from .expression_parser import ExpressionParser

# Only import prompt_toolkit when not running tests
if "pytest" not in sys.modules and not os.environ.get("PYTEST_RUNNING"):
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from .completer import PromptToolkitCompleter

    PROMPT_TOOLKIT_AVAILABLE = True
else:
    # Dummy imports for testing - use type: ignore to suppress type checker warnings
    PromptSession = None  # type: ignore
    FileHistory = None  # type: ignore
    AutoSuggestFromHistory = None  # type: ignore
    PromptToolkitCompleter = None  # type: ignore
    PROMPT_TOOLKIT_AVAILABLE = False


class REPL:
    def __init__(self, network: BayesianNetwork):
        self.network = network
        self.query_parser = QueryParser(network)
        self.command_handler = CommandHandler(network)
        self.expression_parser = ExpressionParser(self.query_parser)

        # Type annotation to allow both PromptToolkitCompleter and None
        self.completer: Optional[object] = None
        if PROMPT_TOOLKIT_AVAILABLE:
            self.completer = PromptToolkitCompleter(network)
        else:
            self.completer = None
        self.history_file = ".bayescalc_history"

        # Type annotation to allow both PromptSession and None
        self.session: Optional[Any] = None
        if PROMPT_TOOLKIT_AVAILABLE:
            self.session = PromptSession(
                history=FileHistory(self.history_file),
                auto_suggest=AutoSuggestFromHistory(),
                completer=self.completer,
                complete_while_typing=True,  # Enable tab completion while typing
            )
        else:
            self.session = None

    def run(self):
        """Starts the REPL loop."""
        if not PROMPT_TOOLKIT_AVAILABLE:
            raise RuntimeError("REPL requires prompt_toolkit to be available")

        print("Bayesian Network Calculator (using prompt_toolkit)")
        print("Type 'help' for a list of commands, 'exit' to quit.")

        while True:
            try:
                line = self.session.prompt(">> ").strip()
                if not line:
                    continue

                if line.lower() == "exit":
                    break
                elif line.lower() == "help":
                    self.print_help()
                    continue

                # Check if it can be evaluated as an expression (mathematical or probability)
                if self.expression_parser.can_evaluate(line):
                    try:
                        result = self.expression_parser.evaluate(line)
                        if hasattr(result, "probabilities"):  # It's a Factor object
                            # Print the result as a distribution
                            for assignment, prob in result.probabilities.items():
                                print(
                                    f"  P({', '.join(assignment) if assignment else ''}) = {prob:.6f}"
                                )
                        else:  # It's a scalar value
                            print(f"  = {result:.6f}")
                    except ValueError as e:
                        print(f"Error: {e}", file=sys.stderr)
                    continue

                # Handle the line as a command
                try:
                    result = self.command_handler.execute(line)
                    print(result)
                except (ValueError, SyntaxError, KeyError) as e:
                    print(f"Error: {e}", file=sys.stderr)

            except (ValueError, SyntaxError, KeyError) as e:
                print(f"Error: {e}", file=sys.stderr)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                break

    def print_help(self):
        """Prints the help message."""
        help_text = """
Available commands:
  P(A, B | C=c, D=d)   - Compute conditional probability.
  Arithmetic Expressions - Compute with probabilities:
    P(A=a)/P(B=b)      - Divide probabilities
    P(A=a)+P(A=b)      - Sum of probabilities
    P(A|B=b)*2-0.5     - Operations with constants
  Mathematical Functions - Pure math or with probabilities:
    log10(0.5)         - Base-10 logarithm
    sqrt(2)            - Square root
    exp(1)             - Exponential
    sin(0), cos(0)     - Trigonometric functions
    log10(P(A=a))      - Apply math functions to probabilities
    sqrt(P(A=a)) * 2   - Combine math and probability operations
  printCPT(X)          - Print the Conditional Probability Table for variable X.
  printJPT()           - Print the full Joint Probability Table.
  parents(X)           - Show the parents of variable X.
  children(X)          - Show the children of variable X.
  showGraph()          - Display an ASCII graph of the network.
  isindependent(A, B)  - Check if variables A and B are independent.
  iscondindependent(A, B | C) - Check for conditional independence.
  entropy(X)           - Compute the entropy of variable X.
  conditional_entropy(X|Y) - Compute conditional entropy H(X|Y).
  mutual_information(X, Y) - Compute mutual information between X and Y.
  help                 - Show this help message.
  exit                 - Exit the calculator.
  ls / vars            - List all defined variables and their states.
"""
        print(help_text)


if __name__ == "__main__":
    # Example usage for testing
    from .lexer import Lexer

    example_net_str = """
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
    lexer = Lexer(example_net_str)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    network = parser.parse()

    repl = REPL(network)
    repl.run()
