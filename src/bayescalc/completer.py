"""
This module implements the autocompletion logic for the REPL,
using the prompt_toolkit library.
"""
from prompt_toolkit.completion import Completer, Completion
from .network_model import BayesianNetwork
import re

class PromptToolkitCompleter(Completer):
    def __init__(self, network: BayesianNetwork):
        self.network = network
        self.commands = [
            "P(", "printCPT(", "printJPT()", "parents(", "children(", "showGraph()",
            "isindependent(", "iscondindependent(", "entropy(", "conditional_entropy(",
            "mutual_information(", "marginals(", "condprobs(", "help", "exit", "ls", "vars"
        ]

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        word_before_cursor = document.get_word_before_cursor(WORD=True)

        # Check if we're inside a probability query
        if "P(" in text_before_cursor:
            # Find the last opening P(
            p_idx = text_before_cursor.rfind("P(")
            text_inside_p = text_before_cursor[p_idx+2:]
            
            # Case 1: Completing a value after an '='
            match = re.search(r'(\w+)\s*=\s*([\w]*)$', text_inside_p)
            if match:
                var_name = match.group(1)
                val_prefix = match.group(2)
                if var_name in self.network.variables:
                    var = self.network.variables[var_name]
                    for val in var.domain:
                        if val.startswith(val_prefix):
                            yield Completion(val, start_position=-len(val_prefix))
                return

            # Case 2: Completing a variable name
            # Find the last token we're trying to complete
            # This could be after a comma, pipe, opening parenthesis, or tilde
            tokens = re.split(r'[,|()]', text_inside_p)
            last_token = tokens[-1].strip()
            
            # Handle negation prefix
            if last_token.startswith('~'):
                last_token = last_token[1:]
                prefix_len = len(last_token)
                negation_prefix = '~'
            else:
                prefix_len = len(last_token)
                negation_prefix = ''
            
            # Complete variables
            for var_name in self.network.variables:
                if var_name.startswith(last_token):
                    var = self.network.variables[var_name]
                    # For boolean variables, we don't need to add = (with shorthand syntax)
                    # For non-boolean, we must add = since there's no default value
                    add_equals = not var.is_boolean
                    completion_text = negation_prefix + var_name + ("=" if add_equals else "")
                    yield Completion(completion_text, start_position=-prefix_len-len(negation_prefix))
            
            return

        # Check if we're inside a command with parentheses (e.g., printCPT(Ma...)
        command_match = re.match(r'(\w+)\((.*?)$', text_before_cursor)
        if command_match:
            command_name = command_match.group(1)
            args_part = command_match.group(2)
            
            # Commands that take variable names as arguments
            variable_arg_commands = [
                'printCPT', 'parents', 'children', 'entropy', 'isindependent', 
                'iscondindependent', 'mutual_information', 'conditional_entropy'
            ]
            
            if command_name in variable_arg_commands:
                # Find the current argument we're completing
                # Split by comma to handle multiple arguments
                args = [arg.strip() for arg in args_part.split(',')]
                current_arg = args[-1] if args else ''
                
                # Handle special cases for commands with "|" (conditional commands)
                if '|' in current_arg:
                    # For conditional commands, complete after the |
                    pipe_parts = current_arg.split('|')
                    if len(pipe_parts) > 1:
                        current_arg = pipe_parts[-1].strip()
                
                # Complete variable names
                for var_name in self.network.variables:
                    if var_name.startswith(current_arg):
                        yield Completion(var_name, start_position=-len(current_arg))
                return

        # Command completion (when not inside a P() query or command arguments)
        for cmd in self.commands:
            if cmd.startswith(word_before_cursor):
                yield Completion(cmd, start_position=-len(word_before_cursor))
