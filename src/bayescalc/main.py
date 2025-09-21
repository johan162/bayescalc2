"""
Main entry point for the Bayesian Network Calculator.
"""
import argparse
import sys

from .lexer import Lexer
from .parser import Parser
from .repl import REPL
from .batch import run_batch

def main():
    """
    Parses command-line arguments and starts the calculator in the appropriate mode.
    """
    parser = argparse.ArgumentParser(description="A Bayesian Network Calculator.")
    parser.add_argument("network_file", help="Path to the Bayesian network definition file (*.net or *.jpt).")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-b", "--batch", dest="batch_file", help="Path to a file with commands to execute in batch mode.")
    group.add_argument("--cmd", dest="cmd_string", help="A string of commands to execute, separated by semicolons.")
    
    args = parser.parse_args()

    try:
        with open(args.network_file, 'r') as f:
            network_str = f.read()
    except FileNotFoundError:
        print(f"Error: Network file not found at '{args.network_file}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading network file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        lexer = Lexer(network_str)
        tokens = lexer.tokenize()
        parser_net = Parser(tokens)
        network = parser_net.parse()
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing network file: {e}", file=sys.stderr)
        sys.exit(1)

    if args.batch_file:
        # Batch mode from file
        run_batch(network, args.batch_file)
    elif args.cmd_string:
        # Batch mode from command string
        from .batch import execute_commands
        commands = [cmd.strip() for cmd in args.cmd_string.split(';')]
        execute_commands(network, commands)
    else:
        # Interactive mode (REPL)
        repl = REPL(network)
        repl.run()

if __name__ == '__main__':
    main()
