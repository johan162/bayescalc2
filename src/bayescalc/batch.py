"""
This module handles batch mode execution for the Bayesian Network calculator.
"""
import sys
from .lexer import Lexer
from .parser import Parser
from .queries import QueryParser
from .commands import CommandHandler
from .network_model import BayesianNetwork

def execute_commands(network: BayesianNetwork, commands: list[str]):
    """
    Executes a list of commands.
    """
    query_parser = QueryParser(network)
    command_handler = CommandHandler(network)

    for line in commands:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        print(f">> {line}")
        try:
            if line.lower() == 'exit':
                break
            if line.startswith("P("):
                result = query_parser.parse_and_execute(line)
                for assignment, prob in result.probabilities.items():
                    print(f"  P({', '.join(assignment)}) = {prob:.6f}")
            else:
                result = command_handler.execute(line)
                print(result)
        except (ValueError, SyntaxError, KeyError) as e:
            print(f"Error processing command '{line}': {e}", file=sys.stderr)
        finally:
            print("-" * 20)

def run_batch(network: BayesianNetwork, commands_file: str):
    """
    Executes a list of commands from a file in batch mode.
    """
    try:
        with open(commands_file, 'r') as f:
            commands = f.readlines()
            execute_commands(network, commands)

    except FileNotFoundError:
        print(f"Error: Commands file not found at '{commands_file}'", file=sys.stderr)

if __name__ == '__main__':
    # Example usage for testing
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

    # Create a dummy commands file
    commands = [
        "P(Rain | GrassWet=Yes)",
        "showGraph()",
        "# This is a comment",
        "entropy(Sprinkler)"
    ]
    cmd_file_path = "test_commands.txt"
    with open(cmd_file_path, "w") as f:
        f.write("\n".join(commands))

    run_batch(network, cmd_file_path)

    # Clean up the dummy file
    import os
    os.remove(cmd_file_path)
